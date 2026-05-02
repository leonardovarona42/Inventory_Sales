from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum, F
from decimal import Decimal
from .models import Proveedor, Producto
from .forms import ProveedorForm, ProductoForm
from inventario.models import MovimientoStock


class IsAdminUser(UserPassesTestMixin):
    """Verifica que el usuario sea administrador"""
    def test_func(self):
        return self.request.user.is_staff


class ProveedorListView(LoginRequiredMixin, IsAdminUser, ListView):
    """Lista de proveedores"""
    model = Proveedor
    template_name = 'productos/proveedor_list.html'
    context_object_name = 'proveedores'
    paginate_by = 20


class ProveedorCreateView(LoginRequiredMixin, IsAdminUser, CreateView):
    """Crear nuevo proveedor"""
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'productos/proveedor_form.html'
    success_url = reverse_lazy('proveedor_list')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor creado exitosamente')
        return super().form_valid(form)


class ProveedorUpdateView(LoginRequiredMixin, IsAdminUser, UpdateView):
    """Actualizar proveedor"""
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'productos/proveedor_form.html'
    success_url = reverse_lazy('proveedor_list')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor actualizado exitosamente')
        return super().form_valid(form)


class ProveedorDeleteView(LoginRequiredMixin, IsAdminUser, DeleteView):
    """Eliminar proveedor"""
    model = Proveedor
    template_name = 'productos/proveedor_confirm_delete.html'
    success_url = reverse_lazy('proveedor_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Proveedor eliminado exitosamente')
        return super().delete(request, *args, **kwargs)


class ProductoListView(LoginRequiredMixin, IsAdminUser, ListView):
    """Lista de productos (insumos)"""
    model = Producto
    template_name = 'productos/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 20

    def get_queryset(self):
        queryset = Producto.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(Q(nombre__icontains=search))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock_total'] = sum(p.stock_actual * p.precio_costo for p in Producto.objects.all())
        context['productos_bajo_stock'] = Producto.objects.filter(stock_actual__lt=F('stock_minimo'))
        return context


class ProductoCreateView(LoginRequiredMixin, IsAdminUser, CreateView):
    """Crear nuevo producto"""
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto creado exitosamente')
        return super().form_valid(form)


class ProductoUpdateView(LoginRequiredMixin, IsAdminUser, UpdateView):
    """Actualizar producto"""
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado exitosamente')
        return super().form_valid(form)


class ProductoDeleteView(LoginRequiredMixin, IsAdminUser, DeleteView):
    """Eliminar producto"""
    model = Producto
    template_name = 'productos/producto_confirm_delete.html'
    success_url = reverse_lazy('producto_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Producto eliminado exitosamente')
        return super().delete(request, *args, **kwargs)


class ProductoDetailView(LoginRequiredMixin, IsAdminUser, DetailView):
    """Detalle de un producto"""
    model = Producto
    template_name = 'productos/producto_detail.html'
    context_object_name = 'producto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producto = self.get_object()
        context['movimientos'] = MovimientoStock.objects.filter(producto=producto).order_by('-fecha')[:10]
        context['valor_total'] = producto.stock_actual * producto.precio_costo
        context['necesita_reorden'] = producto.necesita_reorden()
        return context
