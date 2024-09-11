#!/bin/bash

echo "Setting logs cleaner..."
chmod +x cleanup_logs.sh
(crontab -l 2>/dev/null; echo "0 0 * * * /usr/local/bin/cleanup_logs.sh") | crontab -

echo "Makemigrations..."
python manage.py makemigrations

echo "Migrate..."
python manage.py migrate

echo "Create superuser if not exist..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
EOF

echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000 &

sleep 20

echo "Executing tbot.shell.main monobank refresh..."
python -m tbot.shell.main monobank refresh &

echo "Executing cron for cleaning logs..."
cron -f

wait