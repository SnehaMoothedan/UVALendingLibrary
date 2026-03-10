from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('borrower', 'Borrower'),
        ('provider', 'Provider'),
    )

    # Choice field for user role
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)

    # Field to store admin approval for providers
    is_provider_approved = models.BooleanField(default=False)

    # New field for storing the user’s profile picture
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Additional fields
    birthday = models.DateField(blank=True, null=True)
    interests = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # field to track if a user has requested provider status.
    provider_requested = models.BooleanField(default=False)

    @property
    def borrower_rating(self):
        """
        Returns the user's average rating as a borrower.
        """
        stats = self.recieved_reviews.aggregate(
            avg=Avg('rating')
        )
        if stats['avg'] is not None:
            stats['avg'] = round(stats['avg'], 2)
        return stats['avg']

    def save(self, *args, **kwargs):
        """
        Overridden save method:
        - If the user is approved but not currently a provider, set their role to 'provider'.
        - If the user is provider approved, clear the provider_requested flag.
        """
        if self.is_provider_approved and self.role != 'provider':
            self.role = 'provider'
        # if a user becomes provider approved, you can clear their request.
        if self.is_provider_approved:
            self.provider_requested = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username