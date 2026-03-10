import os
import dj_database_url
from pathlib import Path
import environ
import logging
import ssl
import redis
from redis.asyncio.connection import SSLConnection
from urllib.parse import urlparse

redis_url = os.environ.get("REDIS_TLS_URL") or os.environ.get("REDIS_URL")
parsed = urlparse(redis_url)

#logging.basicConfig(level=logging.DEBUG)

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize django-environ and load .env from BASE_DIR
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Security Settings
SECRET_KEY = env('SECRET_KEY', default='fallback-dev-key')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['.herokuapp.com', 'localhost', '127.0.0.1'])

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000 # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

else:
    SECURE_SSL_REDIRECT = False

# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
    'storages',  # Required for AWS S3
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'books.apps.BooksConfig',
    'accounts.apps.AccountsConfig',
    'django_htmx',
]

#ASGI_APPLICATION = 'projectb18.asgi.application'
WSGI_APPLICATION = 'projectb18.wsgi.application'

'''if not DEBUG:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    REDIS_TLS_URL = env("REDIS_TLS_URL")

    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [{
                    "address": REDIS_TLS_URL,  # loaded only in prod
                    "ssl": ssl_context,
                }],
            },
        },
    }'''
CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }



# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files efficiently
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# URLs and WSGI
ROOT_URLCONF = 'projectb18.urls'
WSGI_APPLICATION = 'projectb18.wsgi.application'

# Templates Configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Social Account Providers
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': env("GOOGLE_CLIENT_ID", default=''),
            'secret': env("GOOGLE_CLIENT_SECRET", default=''),
            'key': '',
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'select_account'
        }
    }
}

# Database Configuration (Heroku & Local)
DATABASES = {
    'default': dj_database_url.config(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# django-allauth settings
# site id = 9 for heroku!
SITE_ID = 9
SOCIALACCOUNT_ADAPTER = "projectb18.adapters.MySocialAccountAdapter"
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_ASSOCIATE_BY_EMAIL = True
SOCIALACCOUNT_LOGIN_ON_GET = True

LOGIN_REDIRECT_URL = '/choose/'
LOGIN_URL = 'account_login'
SOCIALACCOUNT_LOGIN_REDIRECT_URL = '/choose/'

ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"

AUTH_USER_MODEL = 'accounts.CustomUser'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_TZ = True

# ------------------------------
# Static and Media Files Settings
# ------------------------------

# Define S3 storages for both static and media files
STORAGES = {
    # Media (user-uploaded) files:
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    # Static files (CSS, JS, etc):
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
}

# AWS S3 Settings
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='projectb18')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
AWS_S3_SIGNATURE_NAME = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False  # Disable query string auth for public static files

# Static and Media Files URLs and Storage
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL  = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

if DEBUG:
    STATIC_URL = '/static/'
    STORAGES['staticfiles'] = { 'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage' }
else:
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

try:
    if 'HEROKU' in os.environ:
        import django_heroku
        django_heroku.settings(locals())
except ImportError:
    pass