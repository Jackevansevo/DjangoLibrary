from unittest import TestCase

import books.isbn as isbnlib

# Behold the most boring test suite in existence


class TestHasEnglishIdentifier(TestCase):

    def test_isbn10s(self):
        self.assertTrue(isbnlib.has_english_identifier('1-58182-008-9'))
        self.assertTrue(isbnlib.has_english_identifier('0-330-28498-3'))

        self.assertFalse(isbnlib.has_english_identifier('2-226-05257-7'))
        self.assertFalse(isbnlib.has_english_identifier('3-7965-1900-8'))

    def test_isbn13s(self):
        self.assertTrue(isbnlib.has_english_identifier('9781581820089'))
        self.assertTrue(isbnlib.has_english_identifier('9780330284981'))

        self.assertFalse(isbnlib.has_english_identifier('9782226052575'))
        self.assertFalse(isbnlib.has_english_identifier('9783796519000'))

    def test_on_invalid_isbn(self):
        self.assertFalse(isbnlib.has_english_identifier('123'))


class TestCalcISBN13CheckDigit(TestCase):

    def test_check_digit(self):
        self.assertEqual(isbnlib._calc_isbn_13_check_digit('978030640615'), 7)
        self.assertEqual(isbnlib._calc_isbn_13_check_digit('978159327599'), 0)


class TestCalcISBN10CheckDigit(TestCase):

    def test_check_digit(self):
        self.assertEqual(isbnlib._calc_isbn_10_check_digit('030640615'), 2)
        self.assertEqual(isbnlib._calc_isbn_10_check_digit('097522980'), 'X')


class TestToISBN13(TestCase):

    def test_isb10_to_isbn13(self):
        self.assertEqual(isbnlib.to_isbn13('0071809252'), '9780071809252')

    def test_isbn_13_to_isbn13(self):
        self.assertEqual(isbnlib.to_isbn13('9780071809252'), '9780071809252')


class TestToISBN10(TestCase):

    def test_isbn13_to_isbn10(self):
        self.assertEqual(isbnlib.to_isbn10('9780071809252'), '0071809252')

    def test_isbn_10_to_isbn13(self):
        self.assertEqual(isbnlib.to_isbn10('0071809252'), '0071809252')


class TestConvertingBetweenISBNTypesIntegrationTest(TestCase):

    def test_convert_from_13_back_to_10(self):
        isbn = '0306406152'
        self.assertEqual(isbnlib.to_isbn10(isbnlib.to_isbn13(isbn)), isbn)

    def test_convert_from_10_back_to_13(self):
        isbn = '9780071809252'
        self.assertEqual(isbnlib.to_isbn13(isbnlib.to_isbn10(isbn)), isbn)


class TestIsISBN10(TestCase):
    def test_is_isbn10(self):
        self.assertTrue(isbnlib.is_isbn10('1593272812'))
        self.assertTrue(isbnlib.is_isbn10('097522980X'))

        self.assertFalse(isbnlib.is_isbn10('9780071809252'))
        self.assertFalse(isbnlib.is_isbn10('0975229802'))


class TestIsISBN13(TestCase):
    def test_is_isbn13(self):
        self.assertTrue(isbnlib.is_isbn13('9780306406157'))
        self.assertTrue(isbnlib.is_isbn13('9781593275990'))

        self.assertFalse(isbnlib.is_isbn13('097522980X'))
        self.assertFalse(isbnlib.is_isbn13('9781593275991'))


class TestISBNIsValid(TestCase):

    def test_isbn_valid(self):
        self.assertTrue(isbnlib.isbn_is_valid('9781593272814'))
        self.assertTrue(isbnlib.isbn_is_valid('1593272812'))

        self.assertFalse(isbnlib.isbn_is_valid('123'))


class TestISBNClean(TestCase):

    def test_clean_data(self):
        self.assertEqual(isbnlib.clean('978-0071809252 '), '9780071809252')
        self.assertEqual(isbnlib.clean(' 0-306-40615-2 '), '0306406152')
