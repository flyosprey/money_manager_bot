#!/bin/bash

echo "Setting logs cleaner..."
chmod +x cleanup_logs.sh

CRON_JOB="0 0 * * * cleanup_logs.sh >> cronjob.log 2>&1"
crontab -l 2>/dev/null | grep -vF "$CRON_JOB" | crontab -

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
gunicorn --reload money_manager.wsgi:application --bind 0.0.0.0:${WEB_PORT} --workers 3 --timeout 120 &

sleep 20

echo "Executing tbot.shell.main monobank refresh..."
python -m tbot.shell.main monobank refresh &

echo "Executing cron for cleaning logs..."
cron -f

wait
