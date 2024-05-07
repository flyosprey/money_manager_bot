#!/bin/bash
celery -A money_manager.celery.app worker -l info &

celery -A money_manager.celery.app beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

python manage.py runserver 0.0.0.0:8000
