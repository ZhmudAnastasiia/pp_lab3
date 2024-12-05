
# forms.py
# forms.py
from django import forms
from .models import Book, Author, BookCategory

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'publication_year']  # Використовуйте authors і categories

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['authors'].queryset = Author.objects.all()  # Встановіть queryset для authors
        self.fields['categories'].queryset = BookCategory.objects.all()  # Встановіть queryset для categories
    
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # або SelectMultiple для випадаючого списку
        required=False)
    categories = forms.ModelMultipleChoiceField(
        queryset=BookCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Використання CheckboxSelectMultiple
        required=False
    )