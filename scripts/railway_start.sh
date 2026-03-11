#!/usr/bin/env bash
set -euo pipefail

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn canteen_management.wsgi:application --access-logfile - --log-file -
