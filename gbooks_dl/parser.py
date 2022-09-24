import urllib.parse

from gbooks_dl.books.providers.resolver import PROVIDERS


def get_provider_name(url: str) -> str | None:
    """
    As there is no reliable way of extracting a second level domain through
    regex (that I know of yet!), we'll instead split the 'hostname' part of
    the URL up and match each element against our provider set.

    If we have a match, break and return it, otherwise return None if we
    exhaust the loop and don't find anything.

    I feel like this isn't the best way of doing this, but for now I can't
    think of a viable solution.
    """
    host = urllib.parse.urlparse(url).hostname
    parts = host.split('.')
    for part in parts:
        if part in PROVIDERS:
            return part
    return None
