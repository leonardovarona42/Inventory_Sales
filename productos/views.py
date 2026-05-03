from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, F
from .models import Proveedor, Producto, Categoria
from .forms import ProveedorForm, ProductoForm
from inventario.models import MovimientoStock


class IsAdminUser(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class ProveedorListView(LoginRequiredMixin, IsAdminUser, ListView):
    model = Proveedor
    template_name = 'productos/proveedor_list.html'
    context_object_name = 'proveedores'
    paginate_by = 20


class ProveedorCreateView(LoginRequiredMixin, IsAdminUser, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'productos/proveedor_form.html'
    success_url = reverse_lazy('proveedor_list')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor creado exitosamente')
        return super().form_valid(form)


class ProveedorUpdateView(LoginRequiredMixin, IsAdminUser, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'productos/proveedor_form.html'
    success_url = reverse_lazy('proveedor_list')

    def form_valid(self, form):
        messages.success(self.request, 'Proveedor actualizado exitosamente')
        return super().form_valid(form)


class ProveedorDeleteView(LoginRequiredMixin, IsAdminUser, DeleteView):
    model = Proveedor
    template_name = 'productos/proveedor_confirm_delete.html'
    success_url = reverse_lazy('proveedor_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Proveedor eliminado exitosamente')
        return super().delete(request, *args, **kwargs)


class ProductoListView(LoginRequiredMixin, IsAdminUser, ListView):
    model = Producto
    template_name = 'productos/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 20

    def get_queryset(self):
        queryset = Producto.objects.select_related('proveedor').prefetch_related('categorias')
        search = self.request.GET.get('search')
        categoria = self.request.GET.get('categoria')
        if search:
            queryset = queryset.filter(Q(nombre__icontains=search) | Q(descripcion__icontains=search))
        if categoria:
            queryset = queryset.filter(categorias__nombre=categoria)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.filter(padre__isnull=True).order_by('nombre')
        return context


class ProductoCreateView(LoginRequiredMixin, IsAdminUser, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        MovimientoStock.objects.create(
            producto=self.object,
            tipo="entrada",
            cantidad=self.object.stock_actual,
            motivo="compra",
            referencia_id=self.object.id,
            notas="Ingreso inicial",
            usuario=self.request.user.username,
        )
        messages.success(self.request, 'Producto creado exitosamente')
        return response


class ProductoUpdateView(LoginRequiredMixin, IsAdminUser, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/producto_form.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        producto_anterior = Producto.objects.get(pk=self.object.pk)
        stock_previo = producto_anterior.stock_actual
        response = super().form_valid(form)
        diferencia = self.object.stock_actual - stock_previo
        if diferencia != 0:
            MovimientoStock.objects.create(
                producto=self.object,
                tipo="entrada" if diferencia > 0 else "salida",
                cantidad=abs(diferencia),
                motivo="ajuste",
                referencia_id=self.object.id,
                notas="Ajuste de stock",
                usuario=self.request.user.username,
            )
        messages.success(self.request, 'Producto actualizado exitosamente')
        return response


class ProductoDeleteView(LoginRequiredMixin, IsAdminUser, DeleteView):
    model = Producto
    template_name = 'productos/producto_confirm_delete.html'
    success_url = reverse_lazy('producto_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Producto eliminado exitosamente')
        return super().delete(request, *args, **kwargs)


class ProductoDetailView(LoginRequiredMixin, IsAdminUser, DetailView):
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
