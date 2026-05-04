import json
import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from productos.models import Producto

from .models import Venta
from .services import procesar_venta, cancelar_venta

logger = logging.getLogger(__name__)


def _usuario_puede_vender(user):
    return user.is_staff or user.groups.filter(name__in=["Cajero", "Administrador", "Superadmin"]).exists()


def _es_admin(user):
    return user.is_staff or user.groups.filter(name__in=["Administrador", "Superadmin"]).exists()


class VentaListView(LoginRequiredMixin, ListView):
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    paginate_by = 20

    def get_queryset(self):
        qs = Venta.objects.select_related('cajero_user').all()
        if not _es_admin(self.request.user):
            qs = qs.filter(cajero=self.request.user.username)
        return qs.order_by('-fecha_venta')


class VentaDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'

    def test_func(self):
        venta = self.get_object()
        if _es_admin(self.request.user):
            return True
        return self.request.user.username == venta.cajero


class POSView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Producto
    template_name = 'ventas/pos.html'
    context_object_name = 'productos'

    def get_queryset(self):
        return Producto.objects.filter(
            stock_actual__gt=0
        ).prefetch_related("categorias").order_by('nombre')

    def test_func(self):
        return _usuario_puede_vender(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carrito = self.request.session.get("carrito", {})
        categorias = Producto.objects.values_list('categorias__nombre', flat=True).distinct().order_by('categorias__nombre')
        context["carrito_json"] = json.dumps(carrito)
        context["categorias"] = [c for c in categorias if c]
        return context


def _parse_int(value, default=None):
    """Safe integer parsing for AJAX endpoints."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


@login_required
@require_POST
def ajax_agregar_carrito(request):
    if not _usuario_puede_vender(request.user):
        return JsonResponse({"success": False, "error": "No autorizado"}, status=403)

    producto_id = _parse_int(request.POST.get("producto_id"))
    if producto_id is None:
        return JsonResponse({"success": False, "error": "ID de producto invalido"}, status=400)

    cantidad = _parse_int(request.POST.get("cantidad"), 1)
    cantidad = max(1, cantidad)
    producto = get_object_or_404(Producto, id=producto_id)

    if producto.stock_actual <= 0:
        return JsonResponse({"success": False, "error": "Producto sin stock"}, status=400)

    carrito = request.session.get("carrito", {})
    key = str(producto_id)
    if key in carrito:
        carrito[key]["cantidad"] += cantidad
    else:
        carrito[key] = {
            "id": producto_id,
            "nombre": producto.nombre,
            "precio": str(producto.precio_venta or producto.precio_costo or 0),
            "cantidad": cantidad,
            "stock": float(producto.stock_actual),
        }

    request.session["carrito"] = carrito
    return JsonResponse({"success": True, "carrito": carrito})


@login_required
@require_POST
def ajax_quitar_carrito(request):
    if not _usuario_puede_vender(request.user):
        return JsonResponse({"success": False, "error": "No autorizado"}, status=403)

    producto_id = request.POST.get("producto_id")
    carrito = request.session.get("carrito", {})
    if producto_id in carrito:
        del carrito[producto_id]
        request.session["carrito"] = carrito
    return JsonResponse({"success": True, "carrito": carrito})


@login_required
@require_POST
def ajax_limpiar_carrito(request):
    if not _usuario_puede_vender(request.user):
        return JsonResponse({"success": False, "error": "No autorizado"}, status=403)
    request.session["carrito"] = {}
    return JsonResponse({"success": True})


@login_required
@require_POST
def ajax_procesar_venta(request):
    if not _usuario_puede_vender(request.user):
        return JsonResponse({"success": False, "error": "No autorizado"}, status=403)

    carrito = request.session.get("carrito", {})
    if not carrito:
        return JsonResponse({"success": False, "error": "Carrito vacio"})

    metodo_pago = request.POST.get("metodo_pago", "efectivo")
    items = []
    for item_data in carrito.values():
        producto = get_object_or_404(Producto, id=item_data["id"])
        items.append({"producto": producto, "cantidad": item_data["cantidad"]})

    try:
        venta = procesar_venta(metodo_pago=metodo_pago, items=items, cajero=request.user.username)
    except ValidationError as exc:
        return JsonResponse({"success": False, "error": exc.message if hasattr(exc, 'message') else str(exc)})
    except Exception as exc:
        logger.exception("Error procesando venta: %s", exc)
        return JsonResponse({"success": False, "error": "Error interno al procesar la venta"}, status=500)

    request.session["carrito"] = {}
    return JsonResponse(
        {"success": True, "venta_id": venta.id, "ticket": venta.codigo_ticket, "total": str(venta.total_pagado)}
    )


@login_required
@require_POST
def ajax_cancelar_venta(request, pk):
    if not _es_admin(request.user):
        return JsonResponse({"success": False, "error": "No autorizado"}, status=403)

    venta_id = _parse_int(pk)
    if venta_id is None:
        return JsonResponse({"success": False, "error": "ID de venta invalido"}, status=400)

    try:
        cancelar_venta(venta_id=venta_id, motivo="Cancelada por usuario")
    except ValidationError as exc:
        return JsonResponse({"success": False, "error": str(exc)})
    except Exception as exc:
        logger.exception("Error cancelando venta %s: %s", venta_id, exc)
        return JsonResponse({"success": False, "error": "Error interno al cancelar la venta"}, status=500)
    return JsonResponse({"success": True})
