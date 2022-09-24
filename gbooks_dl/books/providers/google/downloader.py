import hashlib

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
        cookie_str = self._headers.get("Set-Cookie")
        if cookie_str is not None:
            cookie = GoogleCookie(cookie_str)
            cookie.add_consent()
            self._headers.update({'Cookie': cookie.output()})
        return self._headers

    @staticmethod
    def _data_is_ok(data: bytes) -> bool:
        data_hash = hashlib.md5(data).hexdigest()

        if data_hash == _NOT_AVAILABLE_PAGE_HASH:
            return True
        return False
