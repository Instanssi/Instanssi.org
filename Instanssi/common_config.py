# -*- coding: utf-8 -*-

import os
import sys

CONTENTDIR = os.path.dirname(__file__)
PROJECTDIR = os.path.dirname(CONTENTDIR)

ADMINS = ()
MANAGERS = ADMINS

SITE_ID = 1
USE_I18N = True
USE_L10N = False

# Files
MEDIA_ROOT = os.path.join(PROJECTDIR, 'content/uploads/')
MEDIA_URL = '/uploads/'
STATIC_ROOT = os.path.join(PROJECTDIR, 'content/static/')
STATIC_URL = '/static/'

# Use timezones in database
USE_TZ = True

# Max size for request body (8M)
DATA_UPLOAD_MAX_MEMORY_SIZE = 8 * 1024 * 1024

# Celery
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

# Admin panel settings
ADMIN_LOGIN_URL = '/manage/auth/login/'
LOGIN_URL = '/users/login/'

STATICFILES_DIRS = (
    os.path.join(CONTENTDIR, 'static/'),
)

COMPRESS_OFFLINE = True
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)
COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.rCSSMinFilter',
)

OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'groups': 'Access to your groups'
    }
}

RAVEN_CONFIG = {
    'dsn': '',
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication'
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(CONTENTDIR, 'templates/'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'Instanssi.common.context_processors.short_language_code',
                'Instanssi.common.context_processors.google_settings',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

DEFAULT_FILE_STORAGE = 'Instanssi.common.storage.ASCIIFileSystemStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'Instanssi.common.http.Http403Middleware',
]

ROOT_URLCONF = 'Instanssi.urls'

INSTALLED_APPS = (
    'Instanssi.base_layout',
    'Instanssi.arkisto',
    'Instanssi.main2012',
    'Instanssi.main2013',
    'Instanssi.main2014',
    'Instanssi.main2015',
    'Instanssi.main2016',
    'Instanssi.main2017',
    'Instanssi.main2018',
    'Instanssi.main2019',
    'Instanssi.admin_base',
    'Instanssi.admin_arkisto',
    'Instanssi.admin_blog',
    'Instanssi.admin_upload',
    'Instanssi.admin_slides',
    'Instanssi.admin_events',
    'Instanssi.admin_kompomaatti',
    'Instanssi.admin_users',
    'Instanssi.admin_profile',
    'Instanssi.admin_programme',
    'Instanssi.admin_events_overview',
    'Instanssi.admin_utils',
    'Instanssi.admin_screenshow',
    'Instanssi.admin_store',
    'Instanssi.users',
    'Instanssi.kompomaatti',
    'Instanssi.ext_blog',
    'Instanssi.ext_programme',
    'Instanssi.screenshow',
    'Instanssi.dblog',
    'Instanssi.store',
    'Instanssi.infodesk',
    'imagekit',
    'rest_framework',
    'django_filters',
    'oauth2_provider',
    'twitter_tag',
    'crispy_forms',
    'social_django',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'compressor',
    'raven.contrib.django.raven_compat',
)

# Authentication backends, notice the openid backend here.
AUTHENTICATION_BACKENDS = (
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.battlenet.BattleNetOAuth2',
    'social_core.backends.steam.SteamOpenId',
    'django.contrib.auth.backends.ModelBackend',
)

# Log handlers, insert our own database log handler
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry', 'console', 'main_log'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'log_db': {
            'level': 'INFO',
            'class': 'Instanssi.dblog.handlers.DBLogHandler',
        },
        'main_log': {
            'filters': ['require_debug_false'],
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '{}/var/log/main.log'.format(PROJECTDIR),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'WARNING',
            'handlers': ['console', 'main_log'],
            'propagate': False,
        },
        'raven': {
            'level': 'WARNING',
            'handlers': ['console', 'main_log'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'WARNING',
            'handlers': ['console', 'main_log'],
            'propagate': False,
        },
        'Instanssi': {
            'handlers': ['log_db', 'console', 'sentry', 'main_log'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}


def make_celery_conf(debug_mode):
    return 'redis://127.0.0.1:6379/3', {}


def make_cache_conf(debug_mode):
    if debug_mode:
        return {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake'
            }
        }
    else:
        return {
            'default': {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": "redis://127.0.0.1:6379/2",
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                }
            }
        }


def make_email_conf(debug_mode):
    if debug_mode:
        return 'django.core.mail.backends.console.EmailBackend'
    else:
        return 'django.core.mail.backends.smtp.EmailBackend'
