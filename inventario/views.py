from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, F
from django.db import transaction
from .models import MovimientoStock
from productos.models import Producto
from .forms import AjusteStockForm
from utils import IsAdminUser


class MovimientoListView(LoginRequiredMixin, IsAdminUser, ListView):
    model = MovimientoStock
    template_name = 'inventario/movimiento_list.html'
    context_object_name = 'movimientos'
    paginate_by = 50
    ordering = ['-fecha']

    def get_queryset(self):
        return MovimientoStock.objects.select_related('producto').order_by('-fecha')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['ajustes'] = MovimientoStock.objects.filter(
            motivo__in=[MovimientoStock.AJUSTE, MovimientoStock.MERMA, MovimientoStock.DEVOLUCION]
        ).select_related('producto').order_by('-fecha')[:20]
        return ctx


class LowStockListView(LoginRequiredMixin, IsAdminUser, ListView):
    model = Producto
    template_name = 'inventario/low_stock.html'
    context_object_name = 'productos'

    def get_queryset(self):
        return Producto.objects.filter(
            stock_actual__lt=F('stock_minimo')
        ).select_related('proveedor').prefetch_related('categorias').order_by('nombre')


class AjusteStockView(LoginRequiredMixin, IsAdminUser, FormView):
    """Vista para ajustes manuales de inventario"""
    template_name = 'inventario/ajuste_stock.html'
    form_class = AjusteStockForm
    success_url = reverse_lazy('ajuste_stock')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Ajuste de Inventario'
        ctx['historial'] = MovimientoStock.objects.filter(
            motivo__in=[MovimientoStock.AJUSTE, MovimientoStock.MERMA, MovimientoStock.DEVOLUCION]
        ).select_related('producto').order_by('-fecha')[:50]
        return ctx

    def form_valid(self, form):
        producto = form.cleaned_data['producto']
        tipo = form.cleaned_data['tipo']
        cantidad = form.cleaned_data['cantidad']
        motivo = form.cleaned_data['motivo']
        notas = form.cleaned_data['notas']

        with transaction.atomic():
            # Lock product row
            producto = Producto.objects.select_for_update().get(pk=producto.pk)

            if tipo == MovimientoStock.ENTRADA:
                producto.stock_actual += cantidad
            else:
                if producto.stock_actual < cantidad:
                    messages.error(
                        self.request,
                        f'Stock insuficiente. {producto.nombre} tiene {producto.stock_actual:.2f} disponibles.'
                    )
                    return self.form_invalid(form)
                producto.stock_actual -= cantidad

            producto.save()

            MovimientoStock.objects.create(
                producto=producto,
                tipo=tipo,
                cantidad=cantidad,
                motivo=motivo,
                notas=notas,
                usuario=self.request.user.get_full_name() or self.request.user.username,
            )

        messages.success(self.request, f'Ajuste registrado: {producto.nombre} ({tipo}) {cantidad:.2f}.')
        return super().form_valid(form)

