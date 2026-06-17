import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventory_Sales.settings')

print("=== Vercel Django startup ===", flush=True)
print(f"Python: {sys.version}", flush=True)
print(f"DATABASE_URL set: {bool(os.environ.get('DATABASE_URL'))}", flush=True)
print(f"DJANGO_ALLOWED_HOSTS: {os.environ.get('DJANGO_ALLOWED_HOSTS')}", flush=True)

import django
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.db import connections
from pathlib import Path

# Test DB connection before migrations
try:
    db_conn = connections['default']
    db_conn.ensure_connection()
    print("DB connection OK", flush=True)
except Exception as e:
    print(f"DB connection ERROR: {e}", flush=True)

# Collect static files
static_root = Path(settings.STATIC_ROOT)
if not static_root.exists() or not any(static_root.iterdir()):
    print("Running collectstatic...", flush=True)
    call_command('collectstatic', '--noinput', '--clear')
    print("collectstatic completed.", flush=True)

# Run migrations
print("Running migrations...", flush=True)
call_command('migrate', '--noinput')
print("Migrations completed.", flush=True)

# Verify superuser exists or create one
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print("No superuser found - create one via admin panel.", flush=True)

print("=== Startup complete ===", flush=True)

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
