from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, F
from .models import MovimientoStock
from productos.models import Producto


class IsAdminUser(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class MovimientoListView(LoginRequiredMixin, IsAdminUser, ListView):
    model = MovimientoStock
    template_name = 'inventario/movimiento_list.html'
    context_object_name = 'movimientos'
    paginate_by = 50
    ordering = ['-fecha']


class LowStockListView(LoginRequiredMixin, IsAdminUser, ListView):
    model = Producto
    template_name = 'inventario/low_stock.html'
    context_object_name = 'productos'

    def get_queryset(self):
        return Producto.objects.filter(stock_actual__lt=F('stock_minimo'))
