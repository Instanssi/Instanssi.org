from datetime import timedelta
from pathlib import Path
from typing import Any

import sentry_sdk

PROJECT_DIR = Path(__file__).resolve(strict=True).parent
BASE_DIR = PROJECT_DIR.parent

ADMINS = ()
MANAGERS = ADMINS

SITE_ID = 1
USE_I18N = True
USE_L10N = False  # Disable to keep default timestamps
USE_TZ = True

LANGUAGES = [
    ("en", "English"),
    ("fi", "Finnish"),
]
LANGUAGE_CODE = "en"
LOCALE_PATHS = [PROJECT_DIR / "locale"]

# Files
MEDIA_ROOT = BASE_DIR / "content" / "uploads"
MEDIA_URL = "/uploads/"
STATIC_ROOT = BASE_DIR / "content" / "static"
STATIC_URL = "/static/"

# These configuration options are revealed to templates via settings.OPTION_NAME.
TEMPLATE_SETTINGS_EXPORT = ["GOOGLE_API_KEY"]

# We map qr_code library to /qr/ via path mapping, no need for the library to
# add any more path segments.
SERVE_QR_CODE_IMAGE_PATH = ""

# Max size for request body (8M)
DATA_UPLOAD_MAX_MEMORY_SIZE = 8 * 1024 * 1024

# Celery
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULE = {
    "check-upcoming-events": {
        "task": "Instanssi.notifications.tasks.check_upcoming_events",
        "schedule": timedelta(minutes=5),
    },
    "cleanup-old-sent-notifications": {
        "task": "Instanssi.notifications.tasks.cleanup_old_sent_notifications",
        "schedule": timedelta(days=1),
    },
}

# Specific media directories (under MEDIA_ROOT)
MEDIA_COMPO_ALTERNATES: str = "kompomaatti/alternates"
MEDIA_COMPO_ENTRIES: str = "kompomaatti/entries"
MEDIA_COMPO_SOURCES: str = "kompomaatti/sources"
MEDIA_COMPO_IMAGES: str = "kompomaatti/images"
MEDIA_PROGRAMME_IMAGES: str = "programme/images"
MEDIA_STORE_IMAGES: str = "store/images"
MEDIA_UPLOAD_FILES: str = "files"

AUTH_USER_MODEL = "users.User"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"

# Shorten session expiration (default is 2 weeks)
SESSION_COOKIE_AGE = 24 * 3600

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

COMMON_STATIC_DIR = PROJECT_DIR / "static"
STATICFILES_DIRS = (COMMON_STATIC_DIR,)

COMPRESS_OFFLINE = True
COMPRESS_PRECOMPILERS = (("text/x-scss", "django_libsass.SassCompiler"),)
COMPRESS_STORAGE = "compressor.storage.GzipCompressorFileStorage"

SENTRY_DSN = ""

# VAPID keys for Web Push notifications
VAPID_PUBLIC_KEY = ""
VAPID_PRIVATE_KEY = ""
VAPID_CLAIMS_EMAIL = "admin@instanssi.org"

REST_KNOX = {
    "AUTH_TOKEN_CHARACTER_LENGTH": 64,
    "TOKEN_TTL": timedelta(days=7),
    "TOKEN_LIMIT_PER_USER": 3,
    "AUTO_REFRESH": True,
}

# Default for django 6.0
FORMS_URLFIELD_ASSUME_HTTPS = True

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "knox.auth.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "Instanssi.api.exception_handler.custom_exception_handler",
}

# OpenAPI
SPECTACULAR_SETTINGS = {
    "TITLE": "Instanssi.org",
    "DESCRIPTION": "Instanssi.org APIv2",
    "VERSION": "2.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "PREPROCESSING_HOOKS": ["Instanssi.api.openapi.preprocessor_hook"],
    "POSTPROCESSING_HOOKS": ["Instanssi.api.openapi.merge_allauth_spec"],
    "SCHEMA_PATH_PREFIX": "/api/v[0-9]",
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [PROJECT_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "Instanssi.common.context.settings_export",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "Instanssi.common.middleware.UserLanguageMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
]

ROOT_URLCONF = "Instanssi.urls"

INSTALLED_APPS = (
    "Instanssi.base_layout",
    "Instanssi.arkisto",
    "Instanssi.main2026",
    "Instanssi.admin_upload",
    "Instanssi.users.apps.UsersConfig",
    "Instanssi.kompomaatti",
    "Instanssi.ext_blog",
    "Instanssi.ext_programme",
    "Instanssi.ext_mastodon",
    "Instanssi.store",
    "Instanssi.notifications",
    "Instanssi.infodesk",
    "imagekit",
    "rest_framework",
    "knox",
    "csvexport",
    "django_filters",
    "crispy_forms",
    "crispy_bootstrap3",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    "allauth.headless",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "compressor",
    "qr_code",
    "auditlog",
    "drf_spectacular",
    "django_cleanup.apps.CleanupConfig",  # Must be last - cleans up files on model delete/update
)

# Authentication backends
AUTHENTICATION_BACKENDS = ("Instanssi.users.backends.SystemUserAwareAuthBackend",)

# Allauth settings
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_ADAPTER = "Instanssi.users.adapter.AccountAdapter"
HEADLESS_ONLY = False
HEADLESS_SERVE_SPECIFICATION = True
HEADLESS_CLIENTS = ("browser",)
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": "/accounts/confirm-email/{key}",
    "account_reset_password_from_key": "/accounts/password/reset/key/{key}",
    "socialaccount_login_error": "/accounts/login",
}

# Social account provider config (actual keys set in settings.py)
SOCIALACCOUNT_PROVIDERS = {
    "google": {"APPS": [{"client_id": "", "secret": "", "key": ""}]},
    "github": {"APPS": [{"client_id": "", "secret": "", "key": ""}]},
}

# Log handlers, insert our own database log handler
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[%(levelname)s][%(asctime)s] %(module)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def make_celery_conf(debug_mode: bool) -> tuple[str, dict[str, Any]]:
    return "redis://127.0.0.1:6379/3", {}


def make_cache_conf(debug_mode: bool) -> dict[str, Any]:
    if debug_mode:
        return {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "unique-snowflake",
            }
        }
    else:
        return {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379/2",
            }
        }


def make_email_conf(debug_mode: bool) -> str:
    if debug_mode:
        return "django.core.mail.backends.console.EmailBackend"
    else:
        return "django.core.mail.backends.smtp.EmailBackend"


def setup_sentry(conf: dict[str, Any]) -> None:
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=conf.get("SENTRY_DSN"),
        integrations=[
            DjangoIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
        ],
    )
