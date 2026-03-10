from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Book, Collection, BorrowRequest, BorrowerReview, CollectionAccessRequest, BookReview
from django.db.models import Q


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'description', 'image', 'location']
        labels = {
            'description': 'Description (Optional)',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book title'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter author name'
            }),
            'genre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter genre'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter book description',
                'rows': 3
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'location': forms.Select(attrs={
                'class': 'form-control form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['author'].required = True
        self.fields['genre'].required = True
        self.fields['image'].required = True
        self.fields['description'].required = False
        self.fields['location'].required = True

        # Insert the placeholder option at the top
        self.fields['location'].choices = [('', '-- Select a location --')] + list(self.fields['location'].choices)

        # Clear any default pre-selection (like 'TBD')
        self.fields['location'].initial = ''



class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['title', 'description', 'visibility', 'allowed_users', 'books']
        labels = {
            'title': 'Collection Title',
            'description': 'Description (Optional)',
        }
        help_texts = {
            'title': 'Be specific when naming your collection.',
            'description': 'Add a short description so others know what this collection is for. (Optional)',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
            'allowed_users': forms.SelectMultiple(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select users'
            }),
            'books': forms.SelectMultiple(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select books'
            }),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if instance:
            self.fields['books'].queryset = Book.objects.filter(
                ~Q(collection__visibility='private') | Q(pk__in=instance.books.values('pk'))
            ).distinct()
        else:
            self.fields['books'].queryset = Book.objects.exclude(
                collection__visibility='private'
            ).distinct()

class BorrowerReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        label='Rate borrower (1‑5)'
    )

    class Meta:
        model = BorrowerReview
        fields = ['rating'] 

class BorrowRequestForm(forms.ModelForm):
    class Meta:
        model = BorrowRequest
        fields = ['message', 'start_date', 'end_date'] 
        labels = {
            'message': 'Message (Optional)', 
            'start_date': 'Start Date',
            'end_date': 'End Date'
        }
        widgets = {
            'message': forms.Textarea(attrs={
                'maxlength': '500', 
                'class': 'form-control',
                'placeholder': 'Why do you want to borrow this book?'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'When do you plan to borrow it?'
            
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'When do you plan to return it?'
            }),
        }

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        today = timezone.now().date()
        if start_date and start_date < today:
            raise forms.ValidationError("Start date cannot be in the past.")
        return start_date
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError("End date must be after the start date.")

            max_end_date = start_date + timedelta(days=180)
            if end_date > max_end_date:
                raise forms.ValidationError("End date cannot be more than 6 months after the start date.")

class CollectionAccessRequestForm(forms.ModelForm):
    class Meta:
        model = CollectionAccessRequest
        fields = ['message']
        labels = {
            'message': 'Message (Optional)'
        }
        widgets = {
            'message': forms.Textarea(attrs={
                'maxlength': '500',
                'class': 'form-control',
                'placeholder': 'Why do you want to access this collection?'
            }),
        }
            
class BookReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        label='Rate borrower (1‑5)'
    )

    class Meta:
        model = BookReview
        fields = ['rating','comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'maxlength': '500', 
                'class': 'form-control',
                'placeholder': 'Enter a review for this book:'
            }),
        }
