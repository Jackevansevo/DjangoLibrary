from django.test import TestCase
from django.core.urlresolvers import reverse

from books.models import Author, Book, BookCopy, Customer, Genre, Loan, Review
from books.forms import BookCreateForm, BookReviewForm

from .test_utils import RequiresLogin, pop_message

from unittest.mock import PropertyMock, MagicMock, patch

from mixer.backend.django import mixer

# [TODO] Test Search views with multiple parameters and stuff
# [TODO] Test pagination stuff
# [TODO] Test the email sending functionality with:
# https://docs.djangoproject.com/en/1.10/topics/testing/tools/#email-services


class TestIndexView(TestCase):
    """Tests `books:index` view"""

    def setUp(self):
        self.books = mixer.cycle(5).blend(Book)
        self.url = reverse('books:index')
        super(TestIndexView, self).setUp()

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'books/index.html')

    @patch('books.models.OverdueLoanManager.get_queryset')
    def test_shows_overdue_loans(self, mock_overdue):
        """Checks that overdue loans are shown on the index page"""
        # Create a new customer, and a new loan for each Book
        customer = mixer.blend(Customer)
        for book in self.books:
            book_copy = mixer.blend(BookCopy, book=book)
            mixer.blend(Loan, book_copy=book_copy, customer=customer)
        resp = self.client.get(self.url)
        # Patch the OverdueLoanManager to make the loans overdue, the
        # underlying implementation of how this is done is not relevant
        mock_overdue.return_value = Loan.objects.all()
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


class TestBookListView(TestCase):
    """Tests `books:book-list` view"""

    def setUp(self):
        self.books = mixer.cycle(5).blend(Book)
        self.url = reverse('books:book-list')
        super(TestBookListView, self).setUp()

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


class TestBookCreateView(RequiresLogin):
    """Tests `books:book-create` view"""

    def setUp(self):
        self.url = reverse('books:book-create')
        super(TestBookCreateView, self).setUp()

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


class TestBookDetailView(RequiresLogin):
    """Tests `books:book-detail` view"""

    def setUp(self):
        self.book = mixer.blend(Book)
        self.url = reverse('books:book-detail', args=[self.book.slug])
        super(TestBookDetailView, self).setUp()

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'books/book_detail.html')

    def test_form_appears_in_context(self):
        resp = self.client.get(self.url)
        self.assertIn('form', resp.context)
        self.assertIsInstance(resp.context['form'], BookReviewForm)

    def test_view_404s_with_no_book(self):
        self.book.delete()
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 404)

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


class AuthorDetailView(TestCase):
    """Tests `books:author-detail` view"""

    def setUp(self):
        self.author = mixer.blend(Author)
        self.books = mixer.cycle(3).blend(Book, author=self.author)
        self.url = reverse('books:author-detail', args=[self.author.slug])

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'books/author_detail.html')


class CustomerDetailView(RequiresLogin):
    """Tests `books:customer-detail`"""

    def setUp(self):
        self.url = reverse('books:customer-detail')
        super(CustomerDetailView, self).setUp()

    def redirects_anonymous_users_to_login_page(self):
        self.client.logout()
        resp = self.client.post(self.url)
        self.assertRedirects(resp, 'books:login')

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'books/customer_detail.html')


class TestGenreList(TestCase):
    def setUp(self):
        self.genres = mixer.cycle(5).blend(Genre)
        self.url = reverse('books:genre-list')

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


class TestGenreDetail(TestCase):
    def setUp(self):
        self.genre = mixer.blend(Genre)
        self.url = reverse('books:genre-detail', args=[self.genre.slug])

    def test_view_uses_correct_template(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, 'books/genre_detail.html')


class TestSendOverdueReminderEmailsView(TestCase):
    # [TODO] Write me
    pass


class TestBookCheckoutView(RequiresLogin):

    def setUp(self):
        self.book = mixer.blend(Book)
        self.book_copy = mixer.blend(BookCopy, book=self.book)
        self.url = reverse('books:book-checkout', args=[self.book.slug])
        super(TestBookCheckoutView, self).setUp()

    def redirects_anonymous_users_to_login_page(self):
        self.client.logout()
        resp = self.client.post(self.url)
        self.assertRedirects(resp, 'books:login')

    def test_view_404s_with_no_book(self):
        self.book.delete()
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 404)

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

    @patch('books.models.Customer.can_loan', new_callable=PropertyMock)
    def test_shows_error_if_customer_cannot_loan(self, mock_can_loan):
        mock_can_loan.return_value = False
        resp = self.client.post(self.url, follow=True)
        message = pop_message(resp)
        self.assertEqual(message.tags, 'error')
        self.assertTrue('Reached loan limit' in message.message)

    @patch('books.models.Book.is_available', new_callable=PropertyMock)
    def test_prevents_loan_if_book_is_unavaiable(self, mock_is_available):
        mock_is_available.return_value = False
        self.client.post(self.url)
        self.assertFalse(Loan.objects.exists())

    @patch('books.models.Book.is_available', new_callable=PropertyMock)
    def test_show_error_if_book_is_unavailable(self, mock_is_available):
        mock_is_available.return_value = False
        resp = self.client.post(self.url, follow=True)
        message = pop_message(resp)
        self.assertEqual(message.tags, 'error')
        self.assertTrue('Book Unavailable' in message.message)


class TestBookReturnView(RequiresLogin):

    def setUp(self):
        self.book = mixer.blend(Book)
        self.book_copy = mixer.blend(BookCopy, book=self.book)
        self.url = reverse('books:book-return', args=[self.book.slug])
        super(TestBookReturnView, self).setUp()

    def test_http_get_method_not_allowed(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 405)

    def redirects_anonymous_users_to_login_page(self):
        self.client.logout()
        resp = self.client.post(self.url)
        self.assertRedirects(resp, 'books:login')

    def test_view_404s_with_no_book(self):
        self.book.delete()
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 404)

    @patch('books.models.Customer.get_unreturned_book_loan')
    @patch('books.models.Customer.has_book')
    def test_updates_loan_on_valid_post(self, mock_has_book, mock_get_loan):
        # Create a new loan, then call the book return view url
        mock_has_book.return_value = True
        # Mock the get_unreturned_book_loan functino to return a Mock object
        mock_loan = MagicMock()
        mock_get_loan.return_value = mock_loan
        # Assert that the mocked loan return property is set to True
        self.client.post(self.url)
        self.assertTrue(mock_loan.returned)

    def test_redirects_to_book_page_on_valid_post(self):
        resp = self.client.post(self.url)
        self.assertRedirects(resp, self.book.get_absolute_url())


class TestBulkReturnView(RequiresLogin):

    def setUp(self):
        self.url = reverse('books:bulk-return')
        super(TestBulkReturnView, self).setUp()

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
