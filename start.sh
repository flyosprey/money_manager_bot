#!/bin/bash

echo "Setting logs cleaner..."
chmod +x cleanup_logs.sh
(crontab -l 2>/dev/null; echo "0 0 * * * /usr/local/bin/cleanup_logs.sh") | crontab -

echo "Makemigrations..."
python manage.py makemigrations

echo "Migrate..."
python manage.py migrate

SUPERUSER_NAME=${DJANGO_SUPERUSER_USERNAME}
SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL}
SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}

echo "Create superuser if not exist..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os


User = get_user_model()

username = os.getenv('DJANGO_SUPERUSER_USERNAME', '$SUPERUSER_NAME')
email = os.getenv('DJANGO_SUPERUSER_EMAIL', '$SUPERUSER_EMAIL')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '$SUPERUSER_PASSWORD')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created')
EOF

echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000 &

sleep 20

echo "Executing tbot.shell.main monobank refresh..."
python -m tbot.shell.main monobank refresh &

echo "Executing cron for cleaning logs..."
cron -f

wait