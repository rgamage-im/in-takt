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

# Test if Django can load (this will catch import errors)
echo "Testing Django application load..."
python -c "
import sys
import traceback
try:
    from config.wsgi import application
    print('✓ Django application loads successfully')
except Exception as e:
    print('✗ CRITICAL ERROR loading Django:')
    traceback.print_exc()
    sys.exit(1)
"

# Start Gunicorn
echo "Starting Gunicorn on 0.0.0.0:8080..."
exec gunicorn config.wsgi:application \
    --bind=0.0.0.0:8080 \
    --workers=1 \
    --timeout=120 \
    --graceful-timeout=120 \
    --keep-alive=5 \
    --preload \
    --access-logfile=- \
    --error-logfile=- \
    --log-level=debug \
    --capture-output
