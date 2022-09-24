from gbooks_dl.books.base.book import Book
from gbooks_dl.books.providers.google import GoogleBook


def get_book_class(second_level_domain: str) -> Book | None:
    return {
        'google': GoogleBook
    }.get(second_level_domain)
