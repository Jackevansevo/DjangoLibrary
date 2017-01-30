from django import forms
from django.core.cache import cache
from django.forms import formset_factory
from django.utils.translation import ugettext as _

from books.models import Review, Book

import books.isbn as isbnlib


class ISBNForm(forms.Form):
    """
    Form allowing allows user to quickly add a book by ISBN. Remaining model
    fields are populated by meta-data sourced from the web
    """

    isbn = forms.CharField(max_length=17, help_text=_("e.g. 0545582970"))
    copies = forms.IntegerField(min_value=1, initial=1)

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

        metadata = isbnlib.meta(isbn)
        if not metadata:
            raise forms.ValidationError('Book Metadata not found')

        cache.set(isbn, metadata)
        return isbn


class BookForm(forms.ModelForm):

    class Meta:
        exclude = ('slug',)
        model = Book


class BookReviewForm(forms.ModelForm):
    CHOICES = [(x, x) for x in map(str, range(1, 6))]
    rating = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)

    class Meta:
        model = Review
        exclude = ('book', 'customer')


ISBNFormSet = formset_factory(ISBNForm, extra=5)
