from abc import ABC, abstractmethod
from typing import Type

from gbooks_dl.books.base.page import Page
from gbooks_dl.books.base.downloader import Downloader


class Book(ABC):
    downloader: Type[Downloader]  # Override this in concrete classes

    url: str
    pages: list[Page]

    def __init__(self, url: str):
        self.url = url

    @abstractmethod
    def get_pages(self) -> list[Page]:
        ...
