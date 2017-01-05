from django.test import TestCase
from django.core.urlresolvers import reverse

from books.models import Author, Book, BookCopy, Customer, Genre, Loan, Review
from books.forms import BookCreateForm, BookReviewForm

from .test_utils import RequiresLogin, pop_message

from unittest.mock import PropertyMock, MagicMock, patch

from mixer.backend.django import mixer


class IndexViewTests(TestCase):
    """Tests `books:index` view"""

    @classmethod
    def setUpTestData(cls):
        cls.books = mixer.cycle(3).blend(Book)
        cls.url = reverse('books:index')

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'books/index.html')

    @patch('books.models.OverdueLoanManager.get_queryset')
    def test_shows_overdue_loans(self, mock_overdue):
        """Checks that overdue loans are shown on the index page"""
        # Create a new customer, and a new loan for each Book
        customer = mixer.blend(Customer)
        copies = mixer.cycle(3).blend(BookCopy, book=(b for b in self.books))
        loans = mixer.cycle(3).blend(
            Loan, book_copy=(c for c in copies), customer=customer)
        resp = self.client.get(self.url)
        # Patch the OverdueLoanManager to make the loans overdue, the
        # underlying implementation of how this is done is not relevant
        mock_overdue.return_value = loans
        self.assertQuerysetEqual(
            resp.context['overdue_loans'],
            ['<Loan: {}>'.format(l.start_date) for l in mock_overdue],
            ordered=False
        )

    def test_shows_latest_books(self):
        """Checks the most recently added books are shown on the index page"""
        resp = self.client.get(self.url)
        self.assertQuerysetEqual(
            resp.context['latest_books'],
            ['<Book: {}>'.format(b.title) for b in self.books],
            ordered=False
        )


class PaginatedBookViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('books:book-list')

    @patch('books.views.Paginator')
    def test_pagination_with_empty_page(self, mock_paginator):
        from django.core.paginator import PageNotAnInteger

        mock_page = MagicMock()
        mock_page.page.side_effect = PageNotAnInteger
        mock_paginator.return_value = mock_page

        with self.assertRaises(PageNotAnInteger):
            self.client.get(self.url, follow=True)
            mock_paginator.page.assert_called_once()


class BookListViewTests(TestCase):
    """Tests `books:book-list` view"""

    @classmethod
    def setUpTestData(cls):
        cls.books = mixer.cycle(5).blend(Book)
        cls.url = reverse('books:book-list')

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'books/book_list.html')

    def test_redirects_to_search_view_on_post(self):
        resp = self.client.post(self.url, data={'query': 'test'})
        self.assertRedirects(resp, reverse('books:book-search', args=['test']))

    def test_render_book_list_view_if_search_query_is_empty(self):
        resp = self.client.post(self.url, data={'query': ''})
        self.assertTemplateUsed(resp, 'books/book_list.html')


class BookSearchViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        titles = (
            'Portable Code', 'Great Code', 'Code', 'Coding for Dummies',
            'Nineteen Eighty-Four', 'Lord of the Flies'
         )
        mixer.cycle(len(titles)).blend(Book, title=(t for t in titles))

    def shows_search_matches(self):
        resp = self.client.get(reverse('books:book-search', args=['']))
        self.assertEqual(len(resp.context['books']), 0)
        resp = self.client.get(reverse('books:book-search', args=['Code']))
        self.assertEqual(len(resp.context['books']), 4)


class BookCreateViewTests(RequiresLogin):
    """Tests `books:book-create` view"""

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('books:book-create')

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'books/book_create.html')

    def test_form_appears_in_context(self):
        resp = self.client.get(self.url)
        self.assertIn('form', resp.context)
        self.assertIsInstance(resp.context['form'], BookCreateForm)

    def redirects_anonymous_users_to_login_page(self):
        self.client.logout()
        resp = self.client.post(self.url)
        self.assertRedirects(resp, 'books:login')

    @patch('books.views.BookCreateForm')
    @patch('books.models.Book.objects.create_book_from_metadata')
    def test_creates_new_book_on_post(self, mock_create, mock_form):
        isbn = '9781593272074'
        mock_form.is_valid.return_value = True
        mock_form.cleaned_data.return_value = {'isbn': isbn}
        mock_create.return_value = mixer.blend(Book, isbn=isbn)
        self.client.post(self.url, data={'isbn': isbn})
        self.assertTrue(Book.objects.exists())

    @patch('books.views.BookCreateForm.is_valid')
    def test_view_shows_error_on_invalid_post(self, mock_valid):
        mock_valid.return_value = False
        resp = self.client.post(self.url, follow=True)
        form_errors = resp.context['form'].errors
        # Empty ErrorDict evaluates to False
        self.assertTrue(form_errors)


class BookDetailViewTests(RequiresLogin):
    """Tests `books:book-detail` view"""

    @classmethod
    def setUpTestData(cls):
        cls.book = mixer.blend(Book)
        cls.url = reverse('books:book-detail', args=[cls.book.slug])

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'books/book_detail.html')

    def test_form_appears_in_context(self):
        resp = self.client.get(self.url)
        self.assertIn('form', resp.context)
        self.assertIsInstance(resp.context['form'], BookReviewForm)

    def test_creates_new_book_reivew_on_post(self):
        self.client.post(self.url, data={'rating': '5', 'review': 'Good book'})
        self.assertTrue(Review.objects.exists())

    @patch('books.views.BookReviewForm.is_valid')
    def test_show_error_on_invalid_post(self, mock_valid):
        mock_valid.return_value = False
        resp = self.client.post(self.url, follow=True)
        form_errors = resp.context['form'].errors
        # Empty ErrorDict evaluates to False
        self.assertTrue(form_errors)

    @patch('books.models.Customer.has_book')
    @patch('books.models.Customer.has_loaned')
    @patch('books.models.Customer.has_reviewed')
    def test_slip_fetching_user_information_if_user_not_authenticated(
            self, mock_book, mock_loaned, mock_reviewed):
        self.client.logout()
        self.client.get(self.url)
        assert not mock_book.called
        assert not mock_loaned.called
        assert not mock_reviewed.called


class AuthorDetailViewTests(TestCase):
    """Tests `books:author-detail` view"""

    @classmethod
    def setUpTestData(cls):
        cls.author = mixer.blend(Author)
        cls.books = mixer.cycle(3).blend(Book, author=cls.author)
        cls.url = reverse('books:author-detail', args=[cls.author.slug])

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'books/author_detail.html')


class CustomerDetailViewTests(RequiresLogin):
    """Tests `books:customer-detail`"""

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('books:customer-detail')

    def redirects_anonymous_users_to_login_page(self):
        self.client.logout()
        resp = self.client.post(self.url)
        self.assertRedirects(resp, 'books:login')

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'books/customer_detail.html')


class GenreListViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.genres = mixer.cycle(5).blend(Genre)
        cls.url = reverse('books:genre-list')

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, 'books/genre_list.html')

    def test_redirects_to_search_view_on_post(self):
        resp = self.client.post(self.url, data={'query': 'test'})
        self.assertRedirects(
            resp, reverse('books:genre-search', args=['test']))

    def test_render_genre_list_view_if_search_query_is_empty(self):
        resp = self.client.post(self.url, data={'query': ''})
        self.assertTemplateUsed(resp, 'books/genre_list.html')


class GenreDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.genre = mixer.blend(Genre)
        cls.url = reverse('books:genre-detail', args=[cls.genre.slug])

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, 'books/genre_detail.html')


class SendOverdueReminderEmailsViewTests(TestCase):
    # [TODO] Write me
    pass


class BookCheckoutViewTests(RequiresLogin):

    @classmethod
    def setUpTestData(cls):
        cls.book = mixer.blend(Book)
        cls.book_copy = mixer.blend(BookCopy, book=cls.book)
        cls.url = reverse('books:book-checkout', args=[cls.book.slug])

    def redirects_anonymous_users_to_login_page(self):
        self.client.logout()
        resp = self.client.post(self.url)
        self.assertRedirects(resp, 'books:login')

    @patch('books.models.Customer.can_loan', new_callable=PropertyMock)
    @patch('books.models.Book.is_available', new_callable=PropertyMock)
    def test_creates_new_loan_on_post(self, mock_is_available, mock_can_loan):
        mock_is_available.return_value = True
        mock_can_loan.return_value = True
        self.client.post(self.url)
        self.assertTrue(Loan.objects.exists())

    @patch('books.models.Customer.can_loan', new_callable=PropertyMock)
    @patch('books.models.Book.is_available', new_callable=PropertyMock)
    def test_redirects_to_book_page(self, mock_is_available, mock_can_loan):
        mock_is_available.return_value = True
        mock_can_loan.return_value = True
        resp = self.client.post(self.url)
        self.assertRedirects(resp, self.book.get_absolute_url())

    @patch('books.models.Customer.can_loan', new_callable=PropertyMock)
    def test_prevents_loan_if_customer_cannot_loan(self, mock_can_loan):
        mock_can_loan.return_value = False
        self.client.post(self.url)
        self.assertFalse(Loan.objects.exists())

    @patch('books.models.Book.is_available', new_callable=PropertyMock)
    def test_prevents_loan_if_book_is_unavaiable(self, mock_is_available):
        mock_is_available.return_value = False
        self.client.post(self.url)
        self.assertFalse(Loan.objects.exists())

    @patch('books.models.Customer.can_loan', new_callable=PropertyMock)
    def test_shows_error_if_customer_cannot_loan(self, mock_can_loan):
        mock_can_loan.return_value = False
        resp = self.client.post(self.url, follow=True)
        message = pop_message(resp)
        self.assertEqual(message.tags, 'error')
        self.assertTrue('Reached loan limit' in message.message)

    @patch('books.models.Book.is_available', new_callable=PropertyMock)
    def test_show_error_if_book_is_unavailable(self, mock_is_available):
        mock_is_available.return_value = False
        resp = self.client.post(self.url, follow=True)
        message = pop_message(resp)
        self.assertEqual(message.tags, 'error')
        self.assertTrue('Book Unavailable' in message.message)


class TestBookReturnView(RequiresLogin):

    @classmethod
    def setUpTestData(cls):
        cls.book = mixer.blend(Book)
        cls.book_copy = mixer.blend(BookCopy, book=cls.book)
        cls.url = reverse('books:book-return', args=[cls.book.slug])

    def test_http_get_method_not_allowed(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 405)

    def redirects_anonymous_users_to_login_page(self):
        self.client.logout()
        resp = self.client.post(self.url)
        self.assertRedirects(resp, 'books:login')

    @patch('books.models.Customer.get_unreturned_book_loan')
    @patch('books.models.Customer.has_book')
    def test_updates_loan_on_valid_post(self, mock_has_book, mock_get_loan):
        """View should update book loan on valid post"""
        # Create a new loan, then call the book return view url
        mock_has_book.return_value = True
        # Mock the get_unreturned_book_loan function to return a Mock object
        mock_loan = MagicMock()
        mock_get_loan.return_value = mock_loan
        # Assert that the mocked loan return property is set to True
        self.client.post(self.url)
        self.assertTrue(mock_loan.returned)

    def test_redirects_to_book_page_on_valid_post(self):
        """View should redirect back to book page on valid post"""
        resp = self.client.post(self.url)
        self.assertRedirects(resp, self.book.get_absolute_url())


class TestBulkReturnView(RequiresLogin):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('books:bulk-return')

    @patch('books.models.Customer.unreturned_loans')
    def test_returns_multiple_books(self, mock_unreturned_loans):
        loans = mixer.cycle(3).blend(Loan, customer=self.customer)
        mock_unreturned_loans.__iter__.return_value = loans
        self.client.post(self.url)
        # Check all customer loans are returned after post request
        self.assertTrue(all([l.returned for l in loans]))

    def test_http_get_method_not_allowed(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 405)

    def test_redirects_anonymous_users_to_login_page(self):
        self.client.logout()
        resp = self.client.post(self.url)
        self.assertRedirects(resp, '/login/?next=/books/bulk-return/')
