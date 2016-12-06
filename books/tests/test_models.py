from django.test import TestCase
from django.utils.timezone import localtime, now, timedelta

from mixer.backend.django import mixer

from books.models import Author, Book, BookCopy, Customer, Genre, Loan, Review

from unittest.mock import patch

today = localtime(now()).date()

prev_week = today - timedelta(days=7)
prev_fortnight = today - timedelta(days=14)

next_week = today + timedelta(days=7)
next_fortnight = today + timedelta(days=14)


class TestCustomerModel(TestCase):

    def setUp(self):
        self.customer = mixer.blend(Customer, book_allowance=3)

    def test_has_reviewed(self):
        # Test with a book the customer has reviewed
        book = mixer.blend(Book)
        mixer.blend(Review, customer=self.customer, book=book)
        self.assertTrue(self.customer.has_reviewed(book.isbn))

        # Test with a review for a completely new book by another customer
        book = mixer.blend(Book)
        mixer.blend(Review, customer=mixer.blend(Customer), book=book)
        self.assertFalse(self.customer.has_reviewed(book.isbn))

    def test_has_book(self):
        # Test with a book the customer currently owns
        book = mixer.blend(Book)
        mixer.blend(Loan, book_copy=mixer.blend(BookCopy, book=book),
                    customer=self.customer)
        self.assertTrue(self.customer.has_book(book.isbn))

        # Test with a boook the customer has returned
        book = mixer.blend(Book)
        mixer.blend(Loan, book_copy=mixer.blend(BookCopy, book=book),
                    customer=self.customer, returned=True)
        self.assertFalse(self.customer.has_book(book.isbn))

    def test_has_loaned(self):
        # Test with a book the customer has yet to return
        book = mixer.blend(Book)
        mixer.blend(Loan, customer=self.customer,
                    book_copy=mixer.blend(BookCopy, book=book))
        self.assertFalse(self.customer.has_loaned(book.isbn))

        # Test with a book the customer has loaned and returned
        book = mixer.blend(Book)
        mixer.blend(Loan, customer=self.customer, returned=True,
                    book_copy=mixer.blend(BookCopy, book=book))
        self.assertTrue(self.customer.has_loaned(book.isbn))

    def test_get_unreturned_book_loan(self):
        book = mixer.blend(Book)

        # Test nothing is returned if the customer has no unreturned loans for
        # the book
        self.assertIsNone(self.customer.get_unreturned_book_loan(book.isbn))

        # If customer has outstanding loans for a given but, check that the
        # function returns the first loan in the queue
        first_loan, second_loan = mixer.cycle(2).blend(
            Loan, customer=self.customer,
            book_copy=mixer.blend(BookCopy, book=book))
        self.assertEqual(
            self.customer.get_unreturned_book_loan(book.isbn), first_loan)

    def test_overdue_loans(self):

        # Assert the customer has no overdue loans
        self.assertFalse(self.customer.overdue_loans.exists())

        # Create five books
        self.copies = mixer.cycle(5).blend(BookCopy)

        # Create two historic overdue loans
        overdue_loans = mixer.cycle(2).blend(
            Loan, customer=self.customer,
            start_date=prev_fortnight, end_date=prev_week,
            book_copy=(copy for copy in self.copies))

        # Ensure the overdue loans show up in the customers property
        self.assertEqual(self.customer.overdue_loans.count(), 2)
        self.assertEqual(list(self.customer.overdue_loans), overdue_loans)

        # Create two new loans
        mixer.cycle(2).blend(
            Loan, customer=self.customer,
            start_date=None, end_date=None,
            book_copy=(copy for copy in self.copies))

        # Create a historic loan, which has been returned
        mixer.blend(
            Loan, customer=self.customer,
            start_date=prev_fortnight, end_date=prev_week, returned=True,
            book_copy=(copy for copy in self.copies))

        # The customer should still only have two overdue loans
        self.assertEqual(self.customer.overdue_loans.count(), 2)
        self.assertEqual(list(self.customer.overdue_loans), overdue_loans)

    def test_unreturned_loans(self):
        # Test with no unreturned loans
        self.assertFalse(self.customer.unreturned_loans.exists())
        unreturned_loans = mixer.cycle(2).blend(
            Loan, customer=self.customer, book_copy=mixer.blend(
                BookCopy, book=mixer.blend(Book)))
        # With with unreturned loans
        self.assertEqual(self.customer.unreturned_loans.count(), 2)
        self.assertEqual(list(self.customer.unreturned_loans),
                         unreturned_loans)

    def test_can_loan(self):
        # Test customer can loan with no unreturned loans
        self.assertTrue(self.customer.can_loan)

        # Test customer can no longer loan if they have more unreturned books
        # than their book_allowance
        mixer.cycle(4).blend(
            Loan, customer=self.customer, book_copy=mixer.blend(
                BookCopy, book=mixer.blend(Book)))
        # After loaning 4 book copies the customer should be unable to loan
        self.assertFalse(self.customer.can_loan)

    def test_read_list(self):
        # Read list should be empty if customer has not historically loaned and
        # returned any books
        self.assertFalse(self.customer.read_list.exists())

        # Checkout two seperate books
        first_book, second_book = mixer.cycle(2).blend(Book)

        mixer.blend(Loan, customer=self.customer, returned=True,
                    book_copy=mixer.blend(BookCopy, book=first_book))

        mixer.blend(Loan, customer=self.customer, returned=True,
                    book_copy=mixer.blend(BookCopy, book=second_book))

        # Books returned by the customer should show up in their read list
        self.assertEqual(self.customer.read_list.count(), 2)

        # Checkout an extra book for the same customer
        mixer.cycle(2).blend(
            Loan, customer=self.customer, book_copy=mixer.blend(
                BookCopy, book=mixer.blend(Book)))

        # Ensure only returned books should show up in the customers read list
        self.assertEqual(self.customer.read_list.count(), 2)

    def test_get_absolute_url(self):
        # Ensure that the Customer model has an absolute url method
        self.assertIsNotNone(self.customer.get_absolute_url())

    def test_str(self):
        # The Customer __str__ method should return the customers username
        self.assertEqual(str(self.customer), self.customer.username)


class TestAuthorModel(TestCase):

    def setUp(self):
        self.author = mixer.blend(Author)

    def test_get_absolute_url(self):
        # Ensure that the Author model has an absolute url method
        self.assertIsNotNone(self.author.get_absolute_url())

    def test_str(self):
        # The Author __str__ method should return the authors name
        self.assertEqual(str(self.author), self.author.name)


class TestGenreModel(TestCase):

    def setUp(self):
        self.genre = mixer.blend(Genre)

    def test_get_absolute_url(self):
        # Ensure that the Genre model has an absolute url method
        self.assertIsNotNone(self.genre.get_absolute_url())

    def test_str(self):
        # The Genre __str__ method should return the genres' name
        self.assertEqual(str(self.genre), self.genre.name)


class TestBookManager(TestCase):

    def test_create_book_from_metadata_with_existing_book(self):
        # Ensure the method prevents duplicates of the same book
        book = mixer.blend(Book)
        self.assertEqual(
            book, Book.objects.create_book_from_metadata(book.isbn))

    @patch('books.models.meta')
    def test_create_book_from_metadata(self, mock_meta):
        mock_meta.return_value = {
            'title': 'land of lisp',
            'img': "<img src='http://placehold.it/350x150'>",
            'authors': ['conrad barski'],
            'categories': ['programming', 'lisp']
        }
        book = Book.objects.create_book_from_metadata('9781593272814')

        self.assertEqual(book.title, "Land Of Lisp")
        self.assertEqual(
            list(book.authors.values_list('name', flat=True)),
            ['Conrad Barski'],
        )
        self.assertEqual(
            list(book.genres.values_list('name', flat=True)),
            ["Lisp", "Programming"]
        )


class TestBookModel(TestCase):

    def setUp(self):
        self.book = mixer.blend(Book)

    def test_get_average_rating(self):
        ratings = (1, 5, 4, 3, 2, 4, 1)
        # Create some ratings
        mixer.cycle(len(ratings)).blend(
            Review, book=self.book, rating=(r for r in ratings))
        avg = sum(ratings) / len(ratings)
        self.assertEqual(self.book.average_rating, avg)

    def test_get_absolute_url(self):
        # Ensure that the Book model has an absolute url method
        self.assertIsNotNone(self.book.get_absolute_url())

    def test_str(self):
        # The Book __str__ method should return the books title
        self.assertEqual(str(self.book), self.book.title)


class TestBookCopyModel(TestCase):

    def setUp(self):
        self.book_copy = mixer.blend(BookCopy)

    def test_on_loan(self):
        # A book copy with no current oustanding loans should return False
        self.assertFalse(self.book_copy.on_loan)

        # Ensure property return true after creating an outstanding book loan
        mixer.blend(Loan, book_copy=self.book_copy)
        self.assertTrue(self.book_copy.on_loan)

    def test_str(self):
        # The BookCopy __str__ method should return the parent books title
        self.assertEqual(
            str(self.book_copy), '{} Copy'.format(self.book_copy.book.title))


class TestLoanModel(TestCase):

    def setUp(self):
        self.loan = mixer.blend(Loan)

    def test_is_overdue(self):
        # A loan whose end_date is in the past should return True
        self.loan.start_date = prev_fortnight
        self.loan.end_date = prev_week
        self.assertTrue(self.loan.is_overdue)

        # A loan whose end_date is in the past should False
        self.loan.start_date = next_week
        self.loan.end_date = next_fortnight
        self.assertFalse(self.loan.is_overdue)

    def test_str(self):
        # The Loan __str__ method should return the loans start_date
        self.assertEqual(str(self.loan), str(self.loan.start_date))


class TestReviewModel(TestCase):
    def setUp(self):
        self.review = mixer.blend(Review)

    def test_str(self):
        # The Review __str__ method should return the loans start_date
        self.assertEqual(str(self.review), str(self.review.rating))
