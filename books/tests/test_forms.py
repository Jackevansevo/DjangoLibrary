from django.test import TestCase

from unittest.mock import patch

from books.forms import BookCreateForm


class TestBookCreateForm(TestCase):

    @patch('books.isbn.meta')
    def test_form_with_valid_isbn(self, mock_meta):
        mock_meta.return_value = True
        form = BookCreateForm({
            'isbn': '9781593272814'
        })
        self.assertTrue(form.is_valid())

    @patch('books.isbn.meta')
    def test_form_with_non_english_isbn_identifier(self, mock_meta):
        mock_meta.return_value = True
        form = BookCreateForm({
            'isbn': '2-226-05257-7'
        })
        self.assertFalse(form.is_valid())
        self.assertInHTML(
            'ISBN Contains a non English-language identifier',
            form['isbn'].errors
        )
