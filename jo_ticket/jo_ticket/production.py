from settings import *
import os
import dj_database_url


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
        "format": "{levelname} {message}",
        },
    },
    "handlers" : {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose"
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
        "djago.request": {
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