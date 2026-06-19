"""
URL configuration for Inventory_Sales project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.db.models import Sum, F
from django.utils import timezone
from django.shortcuts import render, redirect
from ventas.models import Venta
from productos.models import Producto


def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    context = {}
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
    path('', include('licencias.urls')),
]

# Serve static and media files ALWAYS (not just when DEBUG=True).
# The static() helper returns [] when DEBUG=False, so we must use
# re_path + static_serve directly for offline standalone installation.
urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', static_serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
]
