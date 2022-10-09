import re
import json
import http.client
import urllib.parse
import urllib.request
from typing import NamedTuple, Optional

from gbooks_dl.books.base.headers import Headers
from gbooks_dl.messages import write_max_page, write_current_page
from gbooks_dl.utils import get_response_encoding, decompress_response_data
from gbooks_dl.books.base.book import Book, URL
from gbooks_dl.books.base.page import Page
from gbooks_dl.books.providers.google.downloader import GoogleDownloader
from gbooks_dl.books.providers.google.cookie import GoogleCookieMixin
from gbooks_dl.books.providers.google.headers import (
    GoogleHeaderKinds,
    GoogleRequestHeadersFactory
)
from gbooks_dl.books.providers.google.exceptions import (
    CannotParseIdException,
    NoPagesInResponseException,
    InvalidPageIdStringException
)


_GPAGEID_KINDS = {
    'PP': 1,
    'PR': 2,
    'PA': 3,
    'PT': 4
}
_GPAGEID_KINDS_REV = {v: k for k, v in _GPAGEID_KINDS.items()}


class _PageId(NamedTuple):
    """
    Custom representation of a Google Books page ID object.

    `kind` is a numerical representation the type of page, e.g.
    1 if the page ID is for a PP page.

    `num` is the number part of the page ID. For example,
    if the string page ID is PP62, then `num` is 62.
    """
    kind: int
    num: int

    @property
    def kind_str(self):
        return _GPAGEID_KINDS_REV[self.kind]

    @classmethod
    def from_id_str(cls, s: str):
        match = re.match(r'(?P<kind>P[PRAT])(?P<num>\d+)', s)
        if match is None:
            raise InvalidPageIdStringException(
                f'Could not evaluate a _GPageId object from page ID string {s}'
            )
        args = match.groupdict()

        k = args['kind']
        args['kind'] = _GPAGEID_KINDS.get(args['kind'])
        if args['kind'] is None:
            raise InvalidPageIdStringException(
                f'Could not evaluate the page ID kind from capture '
                f'group match: {k}. Known types: {",".join(_GPAGEID_KINDS.keys())}'
            )

        k = args['num']
        if args['num'] is None:
            raise InvalidPageIdStringException(
                f'Could not evaluate the page ID number from capture '
                f'group match: {k}.'
            )
        args['num'] = int(args['num'])
        return cls(**args)

    def __str__(self):
        return f'{self.kind_str}{self.num}'


class GoogleBook(Book, GoogleCookieMixin):
    downloader = GoogleDownloader

    def __init__(self, url: str):
        super().__init__(url)
        self._id = None
        self._headers = GoogleRequestHeadersFactory.get_headers(kind=GoogleHeaderKinds.LOOKUP)

    @property
    def id(self) -> str:
        if self._id is None:
            try:
                parsed_url = urllib.parse.urlparse(self.url)
            except AttributeError as exc:
                raise CannotParseIdException("Bad URL: Must be type string.") from exc
            query = urllib.parse.parse_qs(parsed_url.query)
            try:
                book_id = query['id']
            except KeyError as exc:
                raise CannotParseIdException("No 'id' field found in URL query string.") from exc
            self._id = book_id[0]
        return self._id

    def get_pages(self) -> list[Page]:
        """
        To get the pages, a URL is built to return a JSON response containing
        some pages and the link to the underlying image of each. In this project,
        it is referred to as a lookup.

        We build the URL for each max page number given in the response
        until we reach the end of the book preview. Once each page number and
        URL is collected, the page list is sorted to the correct order.

        Google gives page 'numbers' in three formats, PPx, PAx, and PTx,
        where x indicates a number. We'll call these 'PageIDs'.

        PP and PR IDs usually refer to book covers, inserts, etc., PA refers to
        the contents of the book, and PT refers to things like the back cover.
        As such, the page list order goes PP -> PR -> PA -> PT.

        There is also a fairly big limitation here:

        Google Books sends a JSON containing information about each page listed
        in the preview, but large chunks may be unavailable. For example, page 1-10
        may be available, but 11-99 are not. Then, page 100-110 might be available.

        As each page is listed in the response, we still naively request the
        source image of each page, under the assumption that each page will return
        an image source URL. If we don't get an image source, we continue on (by
        incrementing the page number for the next request).
        """
        pages: dict[_PageId, Page] = {}
        current_page = _PageId(kind=1, num=1)
        prev_max_page = None

        while True:
            write_current_page(current_page)

            # Start at PP1 and get every page possible
            url = self._get_lookup_url(current_page)

            # Send request to the URL and get the response
            res = self._get_response(url, self._headers)
            assert res.status == 200, f'Got a non-200 response: {res.status}'

            # Set cookie
            cookie = self.extract_cookies_from_response(res)
            if cookie is not None:
                self._headers.update(cookie)

            res_json = self._get_json(res)
            pages.update(self._extract_pages_from_json(res_json))
            max_page_encountered = self._get_max_page_from_json(res_json)
            if max_page_encountered != prev_max_page:
                write_max_page(max_page_encountered)
                prev_max_page = max_page_encountered

            current_page = self._resolve_next_page(
                current_page,
                pages,
                res_json
            )

            if max_page_encountered == current_page:
                break

        return sorted(pages.values(), key=lambda p: p.number)

    def _get_lookup_url(self, page_id: str | _PageId) -> URL:
        query = urllib.parse.urlencode({
            'id': self.id,
            'newbks': 0,
            'pg': str(page_id),
            'source': 'entity_page',
            'jscmd': 'click3'
        })
        tld = '.com'  # TODO: Extract and use TLD of original URL?
        return f'https://books.google{tld}/books?{query}'

    @staticmethod
    def _get_response(url: URL, headers: Headers = None) -> http.client.HTTPResponse:
        if headers is None:
            headers = {}
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req)
        return res

    @staticmethod
    def _get_json(res) -> dict:
        encoding = get_response_encoding(res)
        res_data = res.read()
        res_json = decompress_response_data(res_data, encoding)
        return json.load(res_json)

    @staticmethod
    def _extract_pages_from_json(res: dict) -> dict[_PageId, Page]:
        rtn = {}
        res_pages = res.get('page')

        no_src_lim = 3
        no_src_count = 0  # if no_src_lim is reached, assume we've run out of sources
        if res_pages is None:
            # TODO: Not handled yet. What should we do here?
            raise NoPagesInResponseException(
                f"Expected 'pages' attribute in response but it "
                f"was not found: {str(res)}"
            )
        for r_p in res_pages:
            # Check if we have a source
            has_src = r_p.get('src') is not None
            if not has_src:
                no_src_count += 1
                if no_src_lim == no_src_count:
                    break
                continue

            # Reset the counter and parse
            no_src_count = 0
            page_id = _PageId.from_id_str(r_p['pid'])
            url = r_p['src']
            rtn[page_id] = Page(url=url, number=page_id)
        return rtn

    @staticmethod
    def _resolve_next_page(current_page: _PageId, pages: dict, response_data: dict) -> _PageId:
        """
        Logic for getting the next PageId. If the next page (i.e. current_page + 1) is unavailable
        in the Google Books preview, then the page url is automatically incremented.

        Otherwise, the max PageId of the current collection of pages is returned,
        which should return a response with data for the subsequent pages.
        """
        response_pids = [
            _PageId.from_id_str(p['pid'])
            for p in response_data.get('page')
            if p.get('src') is not None
        ]
        # No srcs in response data? Try the URL again.
        if not response_pids:
            return _PageId(kind=current_page.kind, num=current_page.num + 1)

        # More page IDs are available, so keep going
        if max(response_pids) > current_page:
            return max(pages)

        # Manually increment the page ID
        return _PageId(kind=current_page.kind, num=current_page.num + 1)

    @staticmethod
    def _get_max_page_from_json(res: dict):
        res_pages = res.get('page')
        return max([_PageId.from_id_str(r['pid']) for r in res_pages])

    @property
    def cookie(self) -> Optional[tuple[str, str]]:
        cookie = self._headers.get('cookie')
        if cookie is not None:
            return 'cookie', cookie
        return None
