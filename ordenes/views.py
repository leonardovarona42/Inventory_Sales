from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from decimal import Decimal
import json

from .models import Orden
from .forms import OrdenForm, CambiarEstadoOrdenForm
from recetas.models import ProductoFinal
from ventas.models import Venta
from ventas.services import procesar_venta


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carrito = self.request.session.get('carrito', {})
        total = sum(
            Decimal(str(item['precio'])) * item['cantidad']
            for item in carrito.values()
        )
        context['carrito'] = carrito
        context['total'] = total
        context['carrito_json'] = json.dumps(carrito)
        return context


def ajax_agregar_carrito(request):
    """Agrega un producto al carrito (sesión)"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            producto_id = int(request.POST.get('producto_id'))
            cantidad = int(request.POST.get('cantidad', 1))

            producto = get_object_or_404(ProductoFinal, id=producto_id)

            carrito = request.session.get('carrito', {})
            key = str(producto_id)

            if key in carrito:
                carrito[key]['cantidad'] += cantidad
            else:
                carrito[key] = {
                    'id': producto_id,
                    'nombre': producto.nombre,
                    'precio': str(producto.precio_actual),
                    'cantidad': cantidad
                }

            request.session['carrito'] = carrito

            total_items = sum(item['cantidad'] for item in carrito.values())
            total = sum(
                Decimal(str(item['precio'])) * item['cantidad']
                for item in carrito.values()
            )

            return JsonResponse({
                'success': True,
                'total_items': total_items,
                'total': str(total),
                'carrito_count': len(carrito),
                'carrito': carrito
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Solicitud inválida'})


def ajax_quitar_carrito(request):
    """Quita un producto del carrito"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        producto_id = request.POST.get('producto_id')
        carrito = request.session.get('carrito', {})

        if producto_id in carrito:
            del carrito[producto_id]
            request.session['carrito'] = carrito

            total_items = sum(item['cantidad'] for item in carrito.values())
            total = sum(
                Decimal(str(item['precio'])) * item['cantidad']
                for item in carrito.values()
            )

            return JsonResponse({
                'success': True,
                'total_items': total_items,
                'total': str(total),
                'carrito_count': len(carrito),
                'carrito': carrito
            })
    return JsonResponse({'success': False})


def ajax_limpiar_carrito(request):
    """Limpia todo el carrito"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        request.session['carrito'] = {}
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def ajax_procesar_venta(request):
    """Procesa el carrito y crea la venta"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        carrito = request.session.get('carrito', {})

        if not carrito:
            return JsonResponse({'success': False, 'error': 'Carrito vacío'})

        metodo_pago = request.POST.get('metodo_pago', 'efectivo')

        items = []
        for item_data in carrito.values():
            producto = get_object_or_404(ProductoFinal, id=item_data['id'])
            items.append({
                'producto_final': producto,
                'cantidad': item_data['cantidad']
            })

        try:
            from django.utils import timezone
            orden = Orden.objects.create(
                cliente_nombre='Cliente POS',
                cliente_telefono='',
                estado='preparando'
            )

            venta = procesar_venta(
                orden=orden,
                metodo_pago=metodo_pago,
                items=items
            )

            request.session['carrito'] = {}

            messages.success(request, f'Venta #{venta.id} registrada exitosamente')

            return JsonResponse({
                'success': True,
                'venta_id': venta.id,
                'orden_id': orden.numero_orden,
                'total': str(venta.total_pagado),
                'carrito': {}
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Solicitud inválida'})


class OrdenCreateView(LoginRequiredMixin, CreateView):
    model = Orden
    form_class = OrdenForm
    template_name = 'ordenes/orden_form.html'
    success_url = reverse_lazy('orden_list')