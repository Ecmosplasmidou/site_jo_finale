from .settings import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "mysql": {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='jo_ticket'),
        'USER': 'root',
        'PASSWORD': config('DB_PASSWORD', default='root'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
    }
}