from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Count, Q, F
from datetime import timedelta
from django.utils import timezone
from ventas.models import Venta, DetalleVenta
from recetas.models import ProductoFinal, HistorialPrecioProducto
from productos.models import Producto
from ordenes.models import Orden
import json


class IsAdminOrChef(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.groups.filter(name__in=['Chef', 'Administrador']).exists()


class DashboardView(LoginRequiredMixin, IsAdminOrChef, TemplateView):
    template_name = 'reportes/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ahora = timezone.now()
        hace_30_dias = ahora - timedelta(days=30)
        hace_7_dias = ahora - timedelta(days=7)

        # Resumen general
        context['total_ventas'] = Venta.objects.count()
        context['ingresos_totales'] = Venta.objects.aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0
        context['productos_finales'] = ProductoFinal.objects.count()
        context['productos_bajo_stock'] = Producto.objects.filter(stock_actual__lt=F('stock_minimo')).count()

        # Top productos
        context['top_productos'] = DetalleVenta.objects.values('id_producto_final__nombre').annotate(
            total=Sum('cantidad')
        ).order_by('-total')[:10]

        # Ventas por día
        ventas_dia = Venta.objects.filter(
            fecha_venta__gte=hace_7_dias
        ).extra(
            select={'fecha': 'DATE(fecha_venta)'}
        ).values('fecha').annotate(total=Sum('total_pagado')).order_by('fecha')
        context['ventas_por_dia'] = list(ventas_dia)

        return context


class DynamicPricingReportView(LoginRequiredMixin, IsAdminOrChef, TemplateView):
    template_name = 'reportes/dynamic_pricing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productos = ProductoFinal.objects.all()
        context['productos'] = productos
        context['historial'] = HistorialPrecioProducto.objects.all().order_by('-fecha')[:50]
        return context
