#!/bin/sh

python manage.py migrate --no-input

 # Create the superuser without interactive prompts (using the shell to set password)
python manage.py shell <<EOF
from django.contrib.auth.models import User
user = User.objects.filter(username="adminjehoshaphat").first()

if not user:
    user = User.objects.create_superuser('adminjehoshaphat', 'admin@example.com', 'pentatonic')
    user.save()
EOF


gunicorn -c ./gunicorn_config.py Bloga.wsgi:application