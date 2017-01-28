from django.test import TestCase
from books.templatetags.book_tags import review_stars


class TestGetReviewStars(TestCase):

    def test_review_stars(self):
        star = "<i class='fa fa-star text-warning' aria-hidden='true'></i>"
        expected = star * 2
        # Ensure the template tag results the same resutl as expected
        self.assertEqual(review_stars(2.4), expected)
