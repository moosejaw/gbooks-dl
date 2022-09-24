import locale
from abc import ABC, abstractmethod
from typing import TypeVar, Optional

URL = str
Headers = dict
HeadersKind = TypeVar('HeadersKind')


class RequestHeadersFactory(ABC):
    """
    Abstract representation of a factory class for producing request headers.

    A concrete implementation should be made for each provider, e.g. Google, etc.
    and `get_headers()` should return a dict representation of headers that
    the receiving servers are satisfied with.
    """
    @staticmethod
    @abstractmethod
    def get_headers(*, kind: Optional[HeadersKind] = None) -> Headers:
        ...

    @staticmethod
    def get_locale():
        ...