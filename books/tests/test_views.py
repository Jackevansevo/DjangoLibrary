from django.test import TestCase
from django.core.urlresolvers import reverse

from books.models import Book, BookCopy, Customer, Loan
from books.forms import BookCreateForm

from .test_utils import RequiresLogin

from unittest.mock import patch

from mixer.backend.django import mixer


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

    @patch('books.models.add_book_copy')
    def test_creates_new_book_on_post(self, mock_add_book):
        mock_add_book.return_value = mixer.blend(Book)
        self.client.post(self.url, data={'isbn': '9781593272074'})
        self.assertTrue(Book.objects.exists())

    @patch('books.views.BookCreateForm.is_valid')
    def test_view_shows_error_on_invalid_post(self, form_valid):
        form_valid.return_value = False
        resp = self.client.post(self.url, follow=True)
        form_errors = resp.context['form'].errors
        # Empty ErrorDict evaluates to False
        self.assertTrue(form_errors)
