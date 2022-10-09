import os
import urllib.request
from pathlib import Path
from typing import TypeVar, final, Optional
from abc import ABC, abstractmethod
from http.client import HTTPResponse

from gbooks_dl.logging import log_err
from gbooks_dl.books.base.page import Page
from gbooks_dl.messages import (
    write_max_dl_pages,
    write_current_dl_page
)
from gbooks_dl.utils import (
    mimetype_map,
    get_response_encoding,
    get_response_mimetype,
    decompress_response_data,
)

DownloadHeaders = TypeVar('DownloadHeaders')


class Downloader(ABC):
    def __init__(self, dest: os.PathLike, cookie: Optional[tuple[str, str]] = None):
        self._dest = dest
        self._headers = None
        self._initial_cookie = cookie

    @abstractmethod
    def set_headers(self, *a, **kw) -> DownloadHeaders:
        """
        Different providers will require different headers.

        This method should be implemented in concrete classes, and it should generate
        appropriate headers for the given provider.
        """
        ...

    # @abstractmethod
    # def set_initial_headers(self, *a, **kw):
    #     ...

    def set_initial_cookie(self) -> None:
        if self._headers is not None and self._initial_cookie is not None:
            self._headers.update({self._initial_cookie[0]: self._initial_cookie[1]})

    @abstractmethod
    def set_cookie(self, res: HTTPResponse) -> None:
        ...

    @staticmethod
    def _response_is_ok(res: HTTPResponse) -> bool:
        """
        Method for validating. Feel free to override this method.
        Essentially, it just checks that the response is OK before continuing with
        the download. It should be called for each response you get - i.e. for each request.

        Non-OK responses should return `False` or raise an error if it's critical.
        """
        return True if res.status == 200 else False

    @staticmethod
    def _data_is_ok(data: bytes) -> bool:
        """
        Method for validating data returned in response.

        Some providers might return unusable/dummy data despite the response
        validation check passing.

        This method serves to analyse the data returned to check if it is OK.
        """
        return True

    @final
    def download_pages(self, pages: list[Page]) -> None:
        max_pages = len(pages)
        write_max_dl_pages(max_pages)

        headers = self.set_headers()
        self.set_initial_cookie()

        for idx, page in enumerate(pages):
            write_current_dl_page(idx + 1, max_pages)
            filename = f"{idx + 1}_{str(page.number)}"

            req = urllib.request.Request(page.url, headers=headers)
            res = urllib.request.urlopen(req)
            self.set_cookie(res)

            if not self._response_is_ok(res):
                print(f'Response from URL {page.url} failed validation check.')
                continue

            stream = decompress_response_data(
                res.read(),
                get_response_encoding(res)
            )

            extension = mimetype_map().get(
                get_response_mimetype(res)
            )
            filename += extension
            fp = str(Path(self._dest, filename))

            img_data = stream.read()
            if not self._data_is_ok(img_data):
                self._write_invalid_img(page)
                continue
            with open(fp, 'wb') as out:
                out.write(img_data)

    @staticmethod
    def _write_invalid_img(page, *a, **kw):
        log_err(f'Image data from URL {page.url} failed validation check.')
