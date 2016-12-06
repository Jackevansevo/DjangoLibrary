from django import forms
from django.core.cache import cache

from books.models import Review

import books.isbn as isbnlib


class BookCreateForm(forms.Form):
    isbn = forms.CharField(max_length=17)

    def clean_isbn(self):
        isbn = isbnlib.to_isbn13(self.cleaned_data['isbn'])

        # Skip validation if the isbn has been cached
        if isbn in cache:
            return isbn

        if not isbnlib.is_isbn13(isbn):
            raise forms.ValidationError('ISBN Number was Invalid')

        if not isbnlib.has_english_identifier(isbn):
            error_msg = 'ISBN Contains a non English-language identifier'
            raise forms.ValidationError(error_msg)

        matadata = isbnlib.meta(isbn)
        if not matadata:
            raise forms.ValidationError('Book Metadata not found')

        cache.set(isbn, matadata)
        return isbn


class BookReviewForm(forms.ModelForm):
    CHOICES = [(str(x), str(x)) for x in range(1, 6)]
    rating = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)

    class Meta:
        model = Review
        exclude = ('book', 'customer')
