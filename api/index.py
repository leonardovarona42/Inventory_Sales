import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventory_Sales.settings')

import django
django.setup()

from django.conf import settings
from django.core.management import call_command
from pathlib import Path

static_root = Path(settings.STATIC_ROOT)
if not static_root.exists() or not any(static_root.iterdir()):
    print("Running collectstatic...", flush=True)
    call_command('collectstatic', '--noinput', '--clear')
    print("collectstatic completed.", flush=True)

print("Running migrations...", flush=True)
call_command('migrate', '--noinput')
print("Migrations completed.", flush=True)

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
