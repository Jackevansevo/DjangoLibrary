from django.test import TestCase

from unittest.mock import patch

from books.forms import BookQuickCreateForm


class TestBookQuickCreateForm(TestCase):

    @patch('books.isbn.meta')
    def test_form_with_valid_isbn(self, mock_meta):
        mock_meta.return_value = True
        form = BookQuickCreateForm({'isbn': '9781593272814'})
        self.assertTrue(form.is_valid())

    @patch('books.forms.cache')
    def test_skip_form_validation_if_isbn_in_cache(self, mock_cache):
        mock_cache.__contains__.return_value = True
        form = BookQuickCreateForm({'isbn': '9781593272074'})
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_invalid_isbn(self):
        form = BookQuickCreateForm({'isbn': '1-2-3'})
        self.assertFalse(form.is_valid())
        self.assertIn(
            'ISBN Number was Invalid',
            form['isbn'].errors
        )

    @patch('books.isbn.is_isbn13')
    def test_form_invalid_with_non_english_isbn_identifier(self, mock_valid):
        mock_valid.return_value = True
        form = BookQuickCreateForm({'isbn': '2-226-05257-7'})
        self.assertFalse(form.is_valid())
        self.assertIn(
            'ISBN Contains a non English-language identifier',
            form['isbn'].errors
        )

    @patch('books.isbn.meta')
    def test_form_invalid_if_book_meta_data_missing(self, mock_meta):
        mock_meta.return_value = None
        form = BookQuickCreateForm({'isbn': '9781593272074'})
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Book Metadata not found',
            form['isbn'].errors
        )
