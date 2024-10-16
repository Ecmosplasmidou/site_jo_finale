web: gunicorn --pythonpath jo_ticket jo_ticket.wsgi --log-file -
python manage.py collectstatic --noinput
manage.py migrate