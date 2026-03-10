from django.test import TestCase, Client

# Create your tests here.

from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
User = get_user_model()  # For superuser in admin tests
from accounts.models import CustomUser
from accounts.apps import AccountsConfig
from accounts.views import (
    home,
    anonymous_view,
    choose_view,
    provide_view,
    borrow_view,
)


# Admin Tests

class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a superuser
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')

    def test_admin_site_access(self):
        # Tests that the admin index page is accessible and returns a 200 status code
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

    def test_customuser_in_admin(self):
        # Tests that the CustomUser model is registered in the admin site by checking the change list view
        url = reverse('admin:accounts_customuser_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


# Apps Tests

class AccountsConfigTest(TestCase):
    def test_apps_config(self):
        # Ensures the Accounts app is correctly configured
        self.assertEqual(AccountsConfig.name, 'accounts')


# Models Tests

class CustomUserModelTest(TestCase):
    def test_string_representation(self):
        # Test that the __str__ method of CustomUser returns the username
        user = CustomUser.objects.create(username='john_smith')
        self.assertEqual(str(user), 'john_smith')

    def test_provider_role_set_on_save(self):
        # Tests that when a user is provider-approved but has role 'borrower',
        user = CustomUser.objects.create(
            username='jane_doe',
            role='borrower',
            is_provider_approved=True
        )
        # After saving, because is_provider_approved is True, the role should be updated to 'provider'
        self.assertEqual(user.role, 'provider')

    def test_no_change_if_not_approved(self):
        # Test that if a user is not approved (is_provider_approved=False),
        # their role remains unchanged after saving
        user = CustomUser.objects.create(
            username='no_approval_user',
            role='borrower',
            is_provider_approved=False
        )
        # The role remains 'borrower' because the user has not been approved yet
        self.assertEqual(user.role, 'borrower')


# URL Tests

class TestAccountsUrls(TestCase):
    def test_home_url_resolves(self):
        # Tests that the URL named 'home' resolves to the home view function
        url = reverse('home')
        self.assertEqual(resolve(url).func, home)

    def test_anonymous_url_resolves(self):
        # Tests that the URL named 'anonymous' resolves to the anonymous_view function
        url = reverse('anonymous')
        self.assertEqual(resolve(url).func, anonymous_view)

    def test_choose_url_resolves(self):
        # Tests that the URL named 'choose' resolves to the choose_view function
        url = reverse('choose')
        self.assertEqual(resolve(url).func, choose_view)
""""
    def test_provide_url_resolves(self):
        # Tests that the URL named 'provide_page' resolves to the provide_view function
        url = reverse('provide_page')
        from accounts.views import provide_view
        self.assertEqual(resolve(url).func, provide_view)

    def test_borrow_url_resolves(self):
        # Tests that the URL named 'borrow_page' resolves to the borrow_view function
        url = reverse('borrow_page')
        from accounts.views import borrow_view
        self.assertEqual(resolve(url).func, borrow_view)
"""

# Views Tests

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a regular user for testing
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')

    def test_home_view(self):
        # Tests that the home view returns a 200 status code and uses the correct template
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/home.html')

    def test_anonymous_view(self):
        # Tests that the anonymous view returns a 200 status code and uses the correct template
        response = self.client.get(reverse('anonymous'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/anonymous.html')

    def test_choose_view_requires_login(self):
        # Without login, accessing the choose view should redirect
        response = self.client.get(reverse('choose'))
        self.assertEqual(response.status_code, 302)

        # Log in and try again
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('choose'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/choose.html')

    def test_choose_view_post_provider_approved(self):
        # Set up a user that is provider-approved
        self.user.is_provider_approved = True
        self.user.save()

        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('choose'), {'choice': 'provider'})
        self.assertRedirects(response, reverse('provide_page'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'provider')

def test_choose_view_post_provider_not_approved(self):
    # User is not approved as provider
    self.client.login(username='testuser', password='testpass')
    response = self.client.post(reverse('choose'), {'choice': 'provider'}, follow=True)
    self.assertEqual(response.status_code, 200)
    # Checks that the last redirect in the chain goes to the 'choose' URL
    self.assertEqual(response.redirect_chain[-1][0], reverse('choose'))
    # Ensures role is not changed to provider
    self.user.refresh_from_db()
    self.assertNotEqual(self.user.role, 'provider')

    def test_choose_view_post_borrower(self):
        # Tests that a user posting 'borrower' is redirected to the borrow page and their role is set to 'borrower'
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('choose'), {'choice': 'borrower'})
        self.assertRedirects(response, reverse('borrow_page'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'borrower')

    def test_provide_view_requires_login(self):
        # Tests that the provide view redirects non-logged in users, and loads correctly for logged in users
        response = self.client.get(reverse('provide_page'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('provide_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/provide.html')

    def test_borrow_view_requires_login(self):
        # Tests that the borrow view redirects non-logged in users, and loads correctly for logged in users
        response = self.client.get(reverse('borrow_page'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('borrow_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/borrow.html')

