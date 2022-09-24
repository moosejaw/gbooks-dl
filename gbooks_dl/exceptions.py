class GBooksDlException(Exception):
    ...


class GBooksDlHttpException(GBooksDlException):
    ...


class CannotDecompressResponseException(GBooksDlHttpException):
    ...


class ProviderException(GBooksDlException):
    ...


class CouldNotParseProviderException(ProviderException):
    ...


class NoRegisteredProviderException(ProviderException):
    ...


class BookException(GBooksDlException):
    ...
