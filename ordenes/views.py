from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from decimal import Decimal
from .models import Orden
from .forms import OrdenForm, CambiarEstadoOrdenForm
from recetas.models import ProductoFinal
from ventas.models import Venta, DetalleVenta


class OrdenListView(LoginRequiredMixin, ListView):
    model = Orden
    template_name = 'ordenes/orden_list.html'
    context_object_name = 'ordenes'
    paginate_by = 20


class POSView(LoginRequiredMixin, ListView):
    """Pantalla de punto de venta"""
    model = ProductoFinal
    template_name = 'ordenes/pos.html'
    context_object_name = 'productos'


class OrdenCreateView(LoginRequiredMixin, CreateView):
    model = Orden
    form_class = OrdenForm
    template_name = 'ordenes/orden_form.html'
    success_url = reverse_lazy('orden_list')
