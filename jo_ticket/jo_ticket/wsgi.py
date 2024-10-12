import os
from django.core.wsgi import get_wsgi_application

# Le bon chemin pour accéder à production.py, vu la structure à deux niveaux
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jo_ticket.jo_ticket.production")

application = get_wsgi_application()
