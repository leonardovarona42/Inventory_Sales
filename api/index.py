import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['DJANGO_SETTINGS_MODULE'] = 'Inventory_Sales.settings'
os.environ['DJANGO_DEBUG'] = 'True'

from django.core.wsgi import get_wsgi_application

try:
    application = get_wsgi_application()
except Exception as e:
    import traceback
    tb = traceback.format_exc()
    
    def application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [f"Django init error:\n{tb}\n".encode()]
