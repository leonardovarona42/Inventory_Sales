import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventory_Sales.settings')

print("=== Vercel startup ===", flush=True)
print(f"Python: {sys.version}", flush=True)

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
