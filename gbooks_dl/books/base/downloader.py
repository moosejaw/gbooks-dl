import os
import urllib.request
from pathlib import Path
from typing import TypeVar, final
from abc import ABC, abstractmethod
from http.client import HTTPResponse

from gbooks_dl.books.base.page import Page
from gbooks_dl.utils import (
    mimetype_map,
    get_response_encoding,
    get_response_mimetype,
    decompress_response_data,
)

DownloadHeaders = TypeVar('DownloadHeaders')


class Downloader(ABC):
    def __init__(self, dest: os.PathLike):
        self._dest = dest
        self._headers = None

    @abstractmethod
    def set_headers(self) -> DownloadHeaders:
        """
        Different providers will require different headers.

        This method should be implemented in concrete classes, and it should generate
        appropriate headers for the given provider, including cookies.
        """
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
        for idx, page in enumerate(pages):
            headers = self.set_headers()
            filename = f"{idx}_{str(page.number)}"

            req = urllib.request.Request(page.url, headers=headers)
            res = urllib.request.urlopen(req)

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
                print(f'Image data from URL {page.url} failed validation check.')
                continue
            with open(fp, 'wb') as out:
                out.write(img_data)
