from gbooks_dl.exceptions import BookException


class GoogleBookException(BookException):
    """Base exception to use for all Google book exceptions."""
    ...


class InvalidPageIdStringException(GoogleBookException):
    ...


class CannotParseIdException(GoogleBookException):
    ...


class NoPagesInResponseException(GoogleBookException):
    ...
