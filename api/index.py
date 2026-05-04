import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# Add the project directory to the sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventory_Sales.settings')

django.setup()

application = get_wsgi_application()

def handler(request, context):
    return application
