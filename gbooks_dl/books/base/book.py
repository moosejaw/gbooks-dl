from typing import Type
from abc import ABC, abstractmethod

from gbooks_dl.books.base.page import Page
from gbooks_dl.books.base.downloader import Downloader

URL = str


class Book(ABC):
    downloader: Type[Downloader] = Downloader

    url: str
    pages: list[Page]

    def __init__(self, url: str):
        self.url = url

    @abstractmethod
    def get_pages(self) -> list[Page]:
        ...
