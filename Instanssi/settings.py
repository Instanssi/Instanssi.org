# -*- coding: utf-8 -*-

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Tuomas Virtanen', 'katajakasa@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite.db',
        'USER': '', 
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# Google api stuff
GOOGLEAPIKEY = 'AIzaSyCy8WMM6bkEdsDUE2_jPax35M0PXP87W5s'
GOOGLEANALYTICS = False

# Generic stuff
TIME_ZONE = 'Europe/Helsinki'
LANGUAGE_CODE = 'fi-FI'
SITE_ID = 1
USE_I18N = True
USE_L10N = True

# Files
MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = ''
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'

# OpenID
OPENID_CREATE_USERS = True
OPENID_UPDATE_DETAILS_FROM_SREG = True
OPENID_SREG_REQUIRED_FIELDS = []
OPENID_SREG_EXTRA_FIELDS = []
OPENID_FOLLOW_RENAMES = True
LOGIN_URL = '/openid/login/'
LOGIN_REDIRECT_URL = '/'

# Static files
STATICFILES_DIRS = (
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '31+n6s#)q4uqpg2of7_t(33t604-8c2xndwh%r$q5b$(h=m1&5'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'Instanssi.urls'

TEMPLATE_DIRS = (
)

INSTALLED_APPS = (
    'main2012',
    'arkisto',
    'kompomaatti',
    'openidauth',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_openid_auth',
)

AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
