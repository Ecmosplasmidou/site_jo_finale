from .settings import *
import dj_database_url


DATABASES = {
    "default": dj_database_url.config(default=config('DATABASE_URL')),  # Utilisation correcte pour l'URL de la base de données
    "sqlite3": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
    "mysql": {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='jo_ticket'),
        'USER': config('DB_USER', default='root'),  # Utilisez config pour obtenir l'utilisateur aussi
        'PASSWORD': config('DB_PASSWORD', default='root'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
    }
}