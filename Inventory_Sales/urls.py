"""
URL configuration for Inventory_Sales project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('products/', include('productos.urls')),
    path('pos/', include('ordenes.urls')),
    path('orders/', include('ordenes.urls')),
    path('sales/', include('ventas.urls')),
    path('recipes/', include('recetas.urls')),
    path('inventory/', include('inventario.urls')),
    path('reports/', include('reportes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
