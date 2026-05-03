"""
URL configuration for Inventory_Sales project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.db.models import Sum, F
from django.utils import timezone
from django.shortcuts import render
from ventas.models import Venta
from productos.models import Producto


def home_view(request):
    context = {}
    if request.user.is_authenticated:
        hoy = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ventas_hoy = Venta.objects.filter(fecha_venta__gte=hoy).count()
        total_hoy = Venta.objects.filter(fecha_venta__gte=hoy).aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0
        productos_activos = Producto.objects.filter(stock_actual__gt=0).count()
        stock_bajo = Producto.objects.filter(stock_actual__lt=F('stock_minimo')).count()
        context['ventas_hoy'] = ventas_hoy
        context['total_hoy'] = total_hoy
        context['productos_activos'] = productos_activos
        context['stock_bajo'] = stock_bajo
    return render(request, 'home.html', context)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home_view, name='home'),
    path('products/', include('productos.urls')),
    path('sales/', include('ventas.urls')),
    path('inventory/', include('inventario.urls')),
    path('reports/', include('reportes.urls')),
    path('users/', include('usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
