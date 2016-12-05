from django import forms

from books.models import Review

import books.isbn as isbnlib


class BookCreateForm(forms.Form):
    isbn = forms.CharField(max_length=17)

    def clean_isbn(self):
        data = isbnlib.to_isbn13(self.cleaned_data['isbn'])
        if not isbnlib.is_isbn13(data):
            raise forms.ValidationError('ISBN Number was Invalid')
        if not isbnlib.has_english_identifier(data):
            error_msg = 'ISBN Contains a non English-language identifier'
            raise forms.ValidationError(error_msg)
        if not isbnlib.meta(data):
            raise forms.ValidationError('Book Meta-data not found')
        return data


class BookReviewForm(forms.ModelForm):
    CHOICES = [(str(x), str(x)) for x in range(1, 6)]
    rating = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)

    class Meta:
        model = Review
        exclude = ('book', 'customer')
