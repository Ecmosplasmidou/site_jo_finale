import os
from django.core.wsgi import get_wsgi_application

# Configurez l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jo_ticket.settings")  # Vérifiez que cela pointe vers le bon fichier settings.py

application = get_wsgi_application()  # C'est ce qui sera importé par waitress
