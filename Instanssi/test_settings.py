# flake8: noqa
# NOTE! THIS FILE IS FOR CI AND UNITTEST TESTING ENVIRONMENT!

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

# Google api stuff
GOOGLE_API_KEY = ""

# Generic stuff
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
TIME_ZONE = "Europe/Helsinki"
LANGUAGE_CODE = "fi-FI"

# Make this unique, and don't share it with anybody.
SECRET_KEY = "qw35vb23t234dfgdfgdfgt"

# Twitter tag
TWITTER_OAUTH_TOKEN = ""
TWITTER_OAUTH_SECRET = ""
TWITTER_CONSUMER_KEY = ""
TWITTER_CONSUMER_SECRET = ""

# Steam API
SOCIAL_AUTH_STEAM_API_KEY = ""

# Twitter Auth
SOCIAL_AUTH_TWITTER_KEY = TWITTER_CONSUMER_KEY
SOCIAL_AUTH_TWITTER_SECRET = TWITTER_CONSUMER_SECRET

# Facebook
SOCIAL_AUTH_FACEBOOK_KEY = ""
SOCIAL_AUTH_FACEBOOK_SECRET = ""
SOCIAL_AUTH_FACEBOOK_SCOPE = ["email"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    "locale": "fi_FI",
    "fields": "id,name,email",
}

# Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ""
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ""
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ["email"]

# Battle.net
SOCIAL_AUTH_BATTLENET_OAUTH2_KEY = ""
SOCIAL_AUTH_BATTLENET_OAUTH2_SECRET = ""

# Github
SOCIAL_AUTH_GITHUB_KEY = ""
SOCIAL_AUTH_GITHUB_SECRET = ""
SOCIAL_AUTH_GITHUB_SCOPE = ["email"]

# Paytrail, mock addresses
PAYTRAIL_ID = ""
PAYTRAIL_SECRET = ""
PAYTRAIL_API_URL = "http://localhost:8000"

# Paytrail APIv2
PAYTRAIL_V2_ID = ""
PAYTRAIL_V2_SECRET = ""
PAYTRAIL_V2_API_URL = "http://localhost:8000"

# Crispy forms stuff
CRISPY_FAIL_SILENTLY = not DEBUG
CRISPY_TEMPLATE_PACK = "bootstrap3"

# Initialize email configuration
EMAIL_BACKEND = make_email_conf(DEBUG)

# Initialize cache configuration
CACHES = make_cache_conf(DEBUG)

# Initializes celery config
CELERY_BROKER_URL, CELERY_BROKER_TRANSPORT_OPTIONS = make_celery_conf(DEBUG)

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
