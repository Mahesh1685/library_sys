#Forms for Librarian to add/edit/delete books from library

from django import forms
from librarian.models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'total_copies']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter book title'}),
            'author': forms.TextInput(attrs={'placeholder': 'Enter author'}),
            'isbn': forms.TextInput(attrs={'placeholder': '13-digit ISBN'}),
        }