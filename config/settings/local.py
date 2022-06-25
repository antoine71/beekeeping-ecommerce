import environ

from .base import *


env = environ.Env()
# reading .env file
environ.Env.read_env()

# APPS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS += [
    'django_extensions',
    "debug_toolbar",
]


MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env('SECRET_KEY')
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['localhost', '0.0.0.0', '127.0.0.1']


# Django Admin URL regex.
ADMIN_URL = 'admin/'


INTERNAL_IPS = [
    "127.0.0.1",
]