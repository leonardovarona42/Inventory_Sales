import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventory_Sales.settings')
django.setup()

from django.urls import get_resolver

resolver = get_resolver()
print("Available URL patterns:")
for url in resolver.url_patterns:
    print(f"  {url.pattern}")
