from gbooks_dl.books.base.book import Book
from gbooks_dl.books.providers.google import GoogleBook


PROVIDERS = {
    'google',
}


def get_provider_book(provider: str, *a, **kw) -> Book | None:
    provider_book = {
        'google': GoogleBook
    }.get(provider)

    if provider_book is not None:
        return provider_book(*a, **kw)
    return provider_book
