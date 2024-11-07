#!/bin/sh

python manage.py migrate --no-input


gunicorn -c ./gunicorn_config.py Bloga.wsgi:application