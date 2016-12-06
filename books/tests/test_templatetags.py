from django.test import TestCase
from books.templatetags.book_tags import getReviewStars


class TestGetReviewStars(TestCase):

    def test_review_stars(self):
        star_text = "<i class='fa gold fa-star' aria-hidden='true'></i>"
        expected = star_text * 2
        # Ensure the template tag results the same resutl as expected
        self.assertEqual(getReviewStars(2.4), expected)
