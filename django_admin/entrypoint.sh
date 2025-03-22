#!/bin/sh
sleep 5

python manage.py collectstatic --no-input
python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py createsuperuser --no-input

exec "$@"
