from typing import NamedTuple, TypeVar

PageNumber = TypeVar('PageNumber')


class Page(NamedTuple):
    url: str
    number: PageNumber
