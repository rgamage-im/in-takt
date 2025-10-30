#!/bin/bash
# Azure App Service startup script for Django

echo "Starting In-Takt Portal deployment..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn config.wsgi:application \
    --bind=0.0.0.0:8000 \
    --workers=4 \
    --timeout=600 \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=info
