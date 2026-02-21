# flake8: noqa
# NOTE! THIS FILE IS FOR CI AND UNITTEST TESTING ENVIRONMENT!
from zoneinfo import ZoneInfo

from .common_config import *

# Settings
DEBUG = True
ADMIN = True

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

# Use a fast password hasher for tests (PBKDF2 is intentionally slow)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable AuditlogMiddleware in tests (not needed for assertions, adds per-request overhead)
MIDDLEWARE = [m for m in MIDDLEWARE if m != "auditlog.middleware.AuditlogMiddleware"]

# Use Optimistic strategy for imagekit: generate once on save, skip existence checks on access
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = "imagekit.cachefiles.strategies.Optimistic"

# Google api stuff
GOOGLE_API_KEY = ""

# Generic stuff
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
TIME_ZONE = "Europe/Helsinki"
ZONE_INFO = ZoneInfo(TIME_ZONE)
LANGUAGE_CODE = "en"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "qw35vb23t234dfgdfgdfgt"

# Steam API
SOCIAL_AUTH_STEAM_API_KEY = ""

# Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ""
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ""
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ["email"]

# Github
SOCIAL_AUTH_GITHUB_KEY = ""
SOCIAL_AUTH_GITHUB_SECRET = ""
SOCIAL_AUTH_GITHUB_SCOPE = ["email"]

# Paytrail APIv2
PAYTRAIL_V2_ID = ""
PAYTRAIL_V2_SECRET = ""
PAYTRAIL_V2_API_URL = "http://localhost:8000"

# Mastodon API access
MASTODON_ACCESS_TOKEN = None
MASTODON_BASE_URL = None

# Web Push VAPID keys — fake values for testing (webpush is always mocked)
VAPID_PUBLIC_KEY = "fake-vapid-public-key-for-testing"
VAPID_PRIVATE_KEY = "fake-vapid-private-key-for-testing"
VAPID_CLAIMS_EMAIL = "test@instanssi.org"

# Crispy forms stuff
CRISPY_FAIL_SILENTLY = not DEBUG
CRISPY_TEMPLATE_PACK = "bootstrap3"

# Initialize email configuration
EMAIL_BACKEND = make_email_conf(DEBUG)

# Initialize cache configuration
CACHES = make_cache_conf(DEBUG)

# Initializes celery config
CELERY_BROKER_URL, CELERY_BROKER_TRANSPORT_OPTIONS = make_celery_conf(DEBUG)
CELERY_TASK_ALWAYS_EAGER = True

# Internal ip addresses
INTERNAL_IPS = ("127.0.0.1",)

# Log handlers, insert our own database log handler
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[%(levelname)s][%(asctime)s] %(module)s: %(message)s"},
    },
    "handlers": {
        "console": {"level": "WARNING", "class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO"},
    },
}
