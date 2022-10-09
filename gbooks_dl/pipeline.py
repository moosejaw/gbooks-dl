import os

from gbooks_dl.logging import log_out
from gbooks_dl.parser import get_provider_name
from gbooks_dl.books.providers.resolver import get_provider_book
from gbooks_dl.exceptions import (
    NoRegisteredProviderException,
    CouldNotParseProviderException
)


def pipeline(url: str, dest: os.PathLike | str):
    # Start by parsing the second level domain of the URL to get the provider
    provider = get_provider_name(url)
    if provider is None:
        raise CouldNotParseProviderException(
            "Could not parse a provider from the input URL. "
            "Did you leave the URL unmodified before pasting?\n"
            "Providers are inferred from the second-level domain of the URL, "
            "e.g. the 'google' part of 'https://www.google.com'."
        )
    log_out(f'Extracted provider from URL: {provider}\n')

    # Now attempt to get a Book instance for the parsed provider
    book = get_provider_book(provider, url)
    if book is None:
        raise NoRegisteredProviderException(
            f"There is no provider registered for provider '{provider}'."
        )

    # Now let's get the source URL of each available page in the book.
    pages = book.get_pages()

    # Once we have the pages, download them.
    downloader = book.downloader(dest, book.cookie)
    downloader.download_pages(pages)
