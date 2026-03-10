from django.contrib.auth import get_user_model
from django.urls import reverse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.conf import settings

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Existing code (auto-link user by email)
        if request.user.is_authenticated:
            return '/choose/'

        email = sociallogin.user.email
        if email:
            try:
                existing_user = get_user_model().objects.get(email=email)
                sociallogin.connect(request, existing_user)
            except get_user_model().DoesNotExist:
                pass

    def get_app(self, request, provider=None, client_id=None):
        # Existing code (force single SocialApp)
        qs = SocialApp.objects.filter(provider=provider, sites=settings.SITE_ID)
        try:
            return qs.get()
        except SocialApp.MultipleObjectsReturned:
            return qs.first()
        except SocialApp.DoesNotExist:
            return None

    def is_auto_signup_allowed(self, request, sociallogin):
        return True

    def requires_additional_signup(self, request, sociallogin):
        return False

    def get_login_redirect_url(self, request):
        """
        Override this method to force the post-login URL.
        You can hardcode '/post-login/' or reverse a named URL.
        """
        return '/choose/'