from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'original_date', 'document_file', 'document_type', 'keywords']
        widgets = {
            'original_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ключевое слово1, ключевое слово2, ...'
            }),
        }

class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label='Ключевые слова',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ключевые слова через запятую'
        })
    )
    date_from = forms.DateField(
        required=False,
        label='Дата с',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        required=False,
        label='Дата по',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )