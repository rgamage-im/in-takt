#!/bin/bash
# Azure App Service startup script for Django

set -e  # Exit on error

echo "Starting In-Takt Portal deployment..."
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Python path: $(which python)"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Ensure superuser exists (from env vars if set)
echo "Ensuring superuser exists..."
python manage.py ensure_superuser

# Start Gunicorn
echo "Starting Gunicorn on 0.0.0.0:8000..."
exec gunicorn config.wsgi:application \
    --bind=0.0.0.0:8000 \
    --workers=4 \
    --timeout=600 \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=info
