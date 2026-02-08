"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import traceback

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

try:
    from django.core.wsgi import get_wsgi_application
    print("✓ Django WSGI import successful", flush=True)
    
    application = get_wsgi_application()
    print("✓ Django application initialized successfully", flush=True)
    
except Exception as e:
    print(f"✗ CRITICAL ERROR initializing Django:", flush=True)
    print(f"Error type: {type(e).__name__}", flush=True)
    print(f"Error message: {str(e)}", flush=True)
    traceback.print_exc()
    sys.exit(1)
