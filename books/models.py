import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Book(models.Model):
    LOCATION_CHOICES = [
        ('Brown Library', 'Brown Library'), 
        ('Clemons Library', 'Clemons Library'), 
        ('Fine Arts Library', 'Fine Arts Library'), 
        ('Harrison/Small Library', 'Harrison/Small Library'), 
        ('Music Library', 'Music Library'), 
        ('Shannon Library', 'Shannon Library'), 
        ('TBD', 'TBD')
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='books'
    )
    uploader_email = models.EmailField(blank=True)  # New field to store the uploader's email
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    current_borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='borrowed_books',
        help_text="User who currently has this book borrowed"
        )
    location = models.CharField(
        max_length=25, 
        choices=LOCATION_CHOICES,
        default='TBD'
    )

    def save(self, *args, **kwargs):
        # Automatically set uploader_email if not already set and user exists.
        if self.user and not self.uploader_email:
            self.uploader_email = self.user.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def is_available(self):
        """
        Returns True if the book is available (i.e., no current borrower).
        """
        return self.current_borrower is None

class Collection(models.Model):
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    books = models.ManyToManyField(Book)
    visibility = models.CharField(
        max_length=7,
        choices=PRIVACY_CHOICES,
        default='public',
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collections'
    )
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='shared_collections',
        help_text="Only for private collections"
    )

    def user_can_access(self, user):
        """
        Check if the user can access this collection.
        Returns True if the collection is public or if the user is allowed in a private collection.
        """
        if self.visibility == 'public':
            return True
        elif self.visibility == 'private' and user in self.allowed_users.all():
            return True
        return False

    def __str__(self):
        return f"{self.title} ({self.visibility})"

class BorrowRequest(models.Model):
    REQUEST_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_requests')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrow_requests_list')
    message = models.TextField(blank=True, max_length=500)
    requested_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    status = models.CharField(max_length=10, choices=REQUEST_STATUS, default='pending')
    approved_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_requests'
    )

    def __str__(self):
        return f"Request by {self.requester} for '{self.book.title}' ({self.status})"

class CollectionAccessRequest(models.Model):
    REQUEST_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='access_requests')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='collection_access_requests')
    status = models.CharField(max_length=10, choices=REQUEST_STATUS, default='pending')
    message = models.TextField(blank=True, max_length=500)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_collection_requests'
    )

    def __str__(self):
        return f"Access request by {self.requester} for '{self.collection.title}' ({self.status})"

class BorrowerReview(models.Model):
    """Model to store reviews about borrowers."""
    borrow_request = models.OneToOneField(
        BorrowRequest,
        on_delete=models.CASCADE,
        related_name='review'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_reviews'
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recieved_reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

class BookReview(models.Model):
    # user's review books that are marked as returned
    borrow_request = models.OneToOneField(
        'BorrowRequest',
        on_delete=models.CASCADE,
        related_name='book_review'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='review',
        null=True
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='book_review_by_user'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} rated '{self.borrow_request.book.title}' {self.rating}/5"