from django.test import TestCase

# Create your tests here.

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Book

User = get_user_model()

class BookModelTest(TestCase):
    def setUp(self):
        # Creates a user for testing
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='testpass'
        )

    def test_book_creation_without_uploader_email(self):
        """Ensure that if we create a Book with a user but no uploader_email,
        the uploader_email auto-fills with the user’s email."""
        book = Book.objects.create(
            user=self.user,
            title="Test Book",
            author="Test Author",
            genre="Fiction",
            description="A test book for unit testing",
        )
        self.assertEqual(book.uploader_email, "testuser@example.com")
        self.assertEqual(str(book), "Test Book")  # tests the __str__ method

    def test_book_creation_with_uploader_email(self):
        """If we explicitly set an uploader_email, it remains as is, even if user is set."""
        book = Book.objects.create(
            user=self.user,
            uploader_email='custom@example.com',
            title="Custom Email Book"
        )
        self.assertEqual(book.uploader_email, 'custom@example.com')

    def test_auto_set_uploader_email_only_if_blank(self):
        """Check that uploader_email is set only if blank. 
           If we reassign, the user’s email shouldn’t overwrite it."""
        book = Book.objects.create(
            user=self.user,
            uploader_email='alreadyset@example.com',
            title="Already Set Email"
        )
        # Because the email was already set, it should remain
        self.assertEqual(book.uploader_email, 'alreadyset@example.com')

    def test_book_author_genre_defaults(self):
        """Ensure that author and genre can be blank and handle gracefully."""
        book = Book.objects.create(
            user=self.user,
            title="No Author/Genre"
        )
        self.assertEqual(book.author, "")
        self.assertEqual(book.genre, "")

    def test_book_description_can_be_blank(self):
        """Ensure that a Book can be created with a blank description."""
        book = Book.objects.create(
            user=self.user,
            title="No Description Book",
            description=""
        )
        self.assertEqual(book.description, "")

    def test_multiple_books_for_user(self):
        """Test that a single user can have multiple Book instances associated via the related_name."""
        book1 = Book.objects.create(user=self.user, title="Book One")
        book2 = Book.objects.create(user=self.user, title="Book Two")
        self.assertEqual(self.user.books.count(), 2)

    def test_updating_uploader_email_manually(self):
        """Test that if uploader_email is manually updated, it remains after subsequent saves."""
        book = Book.objects.create(user=self.user, title="Update Email Book")
        # Initially auto-set from user
        self.assertEqual(book.uploader_email, "testuser@example.com")
        # Update manually
        book.uploader_email = "newemail@example.com"
        book.save()
        self.assertEqual(book.uploader_email, "newemail@example.com")

    def test_created_at_not_updated_on_save(self):
        """Test that the created_at field remains unchanged when a Book is updated."""
        book = Book.objects.create(user=self.user, title="Immutable Timestamp")
        original_timestamp = book.created_at
        book.title = "Updated Title"
        book.save()
        self.assertEqual(book.created_at, original_timestamp)

    def test_description_field_allows_text(self):
        """Ensure that the description field can hold long text without errors."""
        long_text = "Lorem ipsum " * 50  # a long string
        book = Book.objects.create(user=self.user, title="Long Description Book", description=long_text)
        self.assertEqual(book.description, long_text)

    def test_book_str_method_returns_title(self):
        """Confirm that the __str__ method returns the book's title (again, as an extra check)."""
        book = Book.objects.create(user=self.user, title="String Method Test")
        self.assertEqual(str(book), "String Method Test")

    def test_update_book_fields(self):
        """Test that updating fields on a Book instance works correctly."""
        book = Book.objects.create(user=self.user, title="Initial Title", author="Initial Author")
        book.title = "New Title"
        book.author = "New Author"
        book.save()
        updated_book = Book.objects.get(pk=book.pk)
        self.assertEqual(updated_book.title, "New Title")
        self.assertEqual(updated_book.author, "New Author")


"""
    def test_genre_field_length_limit(self):
        Test that the genre field does not exceed its max_length of 100 characters.
        long_genre = 'G' * 101  # 101 characters
        book = Book(user=self.user, title="Long Genre Book", genre=long_genre)
        with self.assertRaises(ValidationError):
            book.full_clean()
"""

"""
    def test_author_field_length_limit(self):
        Test that the author field does not exceed its max_length of 255 characters.
        long_author = 'A' * 256  # 256 characters
        book = Book(user=self.user, title="Long Author Book", author=long_author)
        with self.assertRaises(ValidationError):
            book.full_clean()  # Should raise an error due to max_length
"""

""""
    def test_title_field_required(self):
        Verify that creating a Book without a title fails validation.
        with self.assertRaises(ValidationError):
            book = Book(user=self.user)  # missing title
            book.full_clean()  # triggers validation"
            ""
"""

"""
    def test_image_field(self):
        Test that an image can be associated with the Book.
        # Create a fake image
        fake_image = SimpleUploadedFile(
            "test_cover.jpg", b"fake-image-bytes", content_type="image/jpeg"
        )
        book = Book.objects.create(
            user=self.user,
            title="Image Test Book",
            image=fake_image
        )
        self.assertTrue("test_cover.jpg", book.image.name)
"""


