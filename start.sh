#!/bin/bash
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

sleep 10

echo "Executing tbot.shell.main monobank refresh..."
python -m tbot.shell.main monobank refresh

wait