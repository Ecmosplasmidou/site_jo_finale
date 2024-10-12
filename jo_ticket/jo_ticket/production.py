from .settings import *
import os
import dj_database_url
from decouple import config
from pathlib import Path

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    'default': dj_database_url.config(
        env='DATABASE_URL', default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    ),
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    },
}

DEBUG = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": ("%(asctime)s [%(process)d] [%(levelname)s] " +
                       "pathname=%(pathname)s lineno=%(lineno)s " +
                       "funcname=%(funcName)s %(message)s"),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s %(message)s",  # Changez à '%' style
        },
    },
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {
        "testlogger": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "root": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "django.request": {  # Correction de la faute de frappe 'djago'
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.security.csrf": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


# logout and login redirect
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'


BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
