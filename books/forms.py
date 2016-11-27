from django import forms
from .isbn import clean, has_english_identifier, is_isbn13, meta, to_isbn13


class BookCreateForm(forms.Form):
    isbn = forms.CharField(max_length=17)

    def clean_isbn(self):
        data = self.cleaned_data['isbn']
        data = clean(data)
        data = to_isbn13(data)
        if not is_isbn13(data):
            raise forms.ValidationError('ISBN Number was Invalid')
        if not has_english_identifier(data):
            error_msg = 'ISBN Contains a non English-language identifier'
            raise forms.ValidationError(error_msg)
        if not meta(data):
            raise forms.ValidationError('Book Meta-data not found')
        return data
