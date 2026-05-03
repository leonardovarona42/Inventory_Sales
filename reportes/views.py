from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, F
from datetime import timedelta
from django.utils import timezone
from ventas.models import Venta, DetalleVenta
from productos.models import Producto


class IsAdminOrStaff(LoginRequiredMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.groups.filter(
            name__in=['Administrador', 'Superadmin']
        ).exists()


class DashboardView(IsAdminOrStaff, TemplateView):
    template_name = 'reportes/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ahora = timezone.now()
        hace_30_dias = ahora - timedelta(days=30)
        hace_7_dias = ahora - timedelta(days=7)

        context['total_ventas'] = Venta.objects.count()
        context['ingresos_totales'] = Venta.objects.aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0
        context['productos_activos'] = Producto.objects.filter(stock_actual__gt=0).count()
        context['productos_bajo_stock'] = Producto.objects.filter(stock_actual__lt=F('stock_minimo')).count()

        context['top_productos'] = DetalleVenta.objects.values('id_producto__nombre').annotate(
            total=Sum('cantidad')
        ).order_by('-total')[:10]

        ventas_dia = Venta.objects.filter(
            fecha_venta__gte=hace_7_dias
        ).extra(select={'fecha': 'DATE(fecha_venta)'}).values('fecha').annotate(
            total=Sum('total_pagado')
        ).order_by('fecha')
        context['ventas_por_dia'] = list(ventas_dia)

        ventas_por_cajero = Venta.objects.values('cajero').annotate(
            total=Count('id'),
            ingresos=Sum('total_pagado')
        ).order_by('-ingresos')[:10]
        context['ventas_por_cajero'] = ventas_por_cajero

        return context
