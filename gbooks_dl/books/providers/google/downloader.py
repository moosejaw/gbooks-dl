import hashlib

from gbooks_dl.logging import log_err
from gbooks_dl.books.base.downloader import Downloader
from gbooks_dl.books.providers.google.cookie import GoogleCookie
from gbooks_dl.books.providers.google.headers import (
    GoogleRequestHeadersFactory,
    GoogleHeaderKinds
)

_NOT_AVAILABLE_PAGE_HASH = 'a64fa89d7ebc97075c1d363fc5fea71f'  # md5 hash of a 'page not available' page


def _get_hash(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


class GoogleDownloader(Downloader):
    def set_headers(self):
        if self._headers is None:
            self._headers = GoogleRequestHeadersFactory.get_headers(
                kind=GoogleHeaderKinds.PAGE_IMAGE
            )
        return self._headers

    def set_cookie(self, res):
        if self._headers is not None:
            cookie = dict(res.info()).get('Set-Cookie')
            if cookie is not None:
                g_cookie = GoogleCookie(cookie)
                g_cookie.add_consent()
                self._headers['Cookie'] = g_cookie.output()

    @staticmethod
    def _data_is_ok(data: bytes) -> bool:
        data_hash = hashlib.md5(data).hexdigest()

        if data_hash == _NOT_AVAILABLE_PAGE_HASH:
            return False
        return True

    @staticmethod
    def _write_invalid_img(page, *a, **kw):
        log_err(f"Page {page.number} not available. ({page.url})\n")
