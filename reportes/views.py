import logging
from datetime import timedelta
from decimal import Decimal

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Count, F, Case, When, Value, IntegerField
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.http import HttpResponse

from ventas.models import Venta, DetalleVenta
from productos.models import Producto, Categoria

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'reportes/dashboard.html'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.groups.filter(
            name__in=['Administrador', 'Superadmin']
        ).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ahora = timezone.now()
        hace_30_dias = ahora - timedelta(days=30)
        hace_7_dias = ahora - timedelta(days=7)

        context['total_ventas'] = Venta.objects.count()
        context['ingresos_totales'] = Venta.objects.aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0
        context['productos_activos'] = Producto.objects.filter(stock_actual__gt=0).count()
        context['productos_bajo_stock'] = Producto.objects.filter(stock_actual__lt=F('stock_minimo')).count()

        context['top_productos'] = DetalleVenta.objects.values(
            'id_producto__nombre'
        ).annotate(
            total=Sum('cantidad')
        ).order_by('-total')[:10]

        ventas_dia = Venta.objects.filter(
            fecha_venta__gte=hace_7_dias
        ).annotate(
            fecha=TruncDate('fecha_venta')
        ).values('fecha').annotate(
            total=Sum('total_pagado')
        ).order_by('fecha')

        context['ventas_por_dia'] = [
            {'fecha': v['fecha'].strftime('%Y-%m-%d'), 'total': float(v['total'])}
            for v in ventas_dia
        ]

        ventas_por_cajero = Venta.objects.values('cajero').annotate(
            total=Count('id'),
            ingresos=Sum('total_pagado')
        ).order_by('-ingresos')[:10]
        context['ventas_por_cajero'] = ventas_por_cajero

        return context


class InventarioValoracionView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Reporte de valoracion de inventario"""
    template_name = 'reportes/inventario_valoracion.html'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.groups.filter(
            name__in=['Administrador', 'Superadmin']
        ).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Valoracion de Inventario'

        # Totales generales
        productos = Producto.objects.select_related('proveedor').prefetch_related('categorias').filter(
            stock_actual__gt=0
        ).order_by('nombre')

        valor_costo_total = Decimal('0')
        valor_venta_total = Decimal('0')
        unidades_totales = Decimal('0')

        productos_data = []
        for p in productos:
            valor_costo = p.stock_actual * p.precio_costo
            valor_venta = p.stock_actual * p.precio_venta
            margen = valor_venta - valor_costo if valor_costo > 0 else Decimal('0')
            valor_costo_total += valor_costo
            valor_venta_total += valor_venta
            unidades_totales += p.stock_actual
            productos_data.append({
                'producto': p,
                'valor_costo': valor_costo,
                'valor_venta': valor_venta,
                'margen': margen,
            })

        context['productos'] = productos_data
        context['valor_costo_total'] = valor_costo_total
        context['valor_venta_total'] = valor_venta_total
        context['unidades_totales'] = unidades_totales
        context['ganancia_potencial'] = valor_venta_total - valor_costo_total

        # Desglose por categoria
        categorias = Categoria.objects.all()
        desglose_categorias = []
        for cat in categorias:
            prods = cat.productos.filter(stock_actual__gt=0)
            if prods.exists():
                vc = sum(p.stock_actual * p.precio_costo for p in prods)
                vv = sum(p.stock_actual * p.precio_venta for p in prods)
                desglose_categorias.append({
                    'nombre': cat.nombre,
                    'color': cat.color,
                    'valor_costo': vc,
                    'valor_venta': vv,
                    'cantidad': prods.count(),
                })
        context['desglose_categorias'] = desglose_categorias

        # Desglose por proveedor
        desglose_proveedores = []
        proveedores = Producto.objects.values_list('proveedor__nombre', flat=True).distinct()
        for prov_nombre in proveedores:
            if prov_nombre:
                prods = Producto.objects.filter(proveedor__nombre=prov_nombre, stock_actual__gt=0)
                vc = sum(p.stock_actual * p.precio_costo for p in prods)
                vv = sum(p.stock_actual * p.precio_venta for p in prods)
                desglose_proveedores.append({
                    'nombre': prov_nombre,
                    'valor_costo': vc,
                    'valor_venta': vv,
                    'cantidad': prods.count(),
                })
        context['desglose_proveedores'] = sorted(desglose_proveedores, key=lambda x: x['valor_costo'], reverse=True)[:10]

        # Top productos por valor
        top_productos = sorted(productos_data, key=lambda x: x['valor_costo'], reverse=True)[:10]
        context['top_productos'] = top_productos

        return context

    def export_csv(self, request, *args, **kwargs):
        """Exportar valoracion a CSV"""
        from django.utils.text import slugify
        import csv

        productos = Producto.objects.filter(stock_actual__gt=0).order_by('nombre')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="valoracion_inventario.csv"'

        writer = csv.writer(response)
        writer.writerow(['Producto', 'Categoria', 'Proveedor', 'Stock', 'Precio Costo', 'Precio Venta', 'Valor Costo', 'Valor Venta', 'Margen'])

        for p in productos:
            cats = ', '.join(c.nombre for c in p.categorias.all())
            valor_costo = p.stock_actual * p.precio_costo
            valor_venta = p.stock_actual * p.precio_venta
            margen = valor_venta - valor_costo
            writer.writerow([
                p.nombre,
                cats,
                p.proveedor.nombre if p.proveedor else '-',
                float(p.stock_actual),
                float(p.precio_costo),
                float(p.precio_venta),
                float(valor_costo),
                float(valor_venta),
                float(margen),
            ])

        return response
