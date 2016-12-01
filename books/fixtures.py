from mixer.backend.django import mixer
from books.models import Author, Book, BookCopy, Customer, Genre, Review, Loan
from random import randrange

# If only python had macros :(


def genre_factory(count=None):
    if count:
        return mixer.cycle(count).blend(Genre)
    return mixer.blend(Genre)


def author_factory(count=None):
    if count:
        return mixer.cycle(count).blend(Author)
    return mixer.blend(Author)


def book_factory():
    return mixer.blend(
        Book,
        isbn=mixer.faker.ean13(),
        tilte=mixer.faker.catch_phrase(),
        subtitle=mixer.faker.catch_phrase(),
        genres=mixer.cycle(randrange(1, 3)).blend(Genre),
        author=mixer.cycle(randrange(1, 3)).blend(Author),
    )


def bookcopy_factory(count=None, book=None):
    book = book or book_factory()
    if count:
        return mixer.cycle(count).blend(BookCopy, book=book)
    return mixer.blend(BookCopy, book=book)


def review_factory(count=None, customer=None, book=None):
    customer = customer or mixer.blend(Customer)
    book = book or mixer.SELECT
    if count:
        return mixer.cycle(count).blend(
            Review,
            customer=customer,
            book=book,
            rating=lambda: randrange(1, 6)
        )
    return mixer.blend(
        Review,
        customer=customer,
        book=book,
        rating=randrange(1, 6)
    )


def loan_factory(count=None, start_date=None, end_date=None, book_copy=None):
    return mixer.blend(Loan, start_date=start_date, end_date=end_date)
