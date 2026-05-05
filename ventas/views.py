import json
import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from productos.models import Producto

from .models import Venta, DetalleVenta, Cliente, ConfiguracionSistema
from .services import procesar_venta, cancelar_venta
from .forms import ClienteForm, ConfiguracionForm
from utils import IsCajeroOrAbove, IsAdminUser, _tiene_rol

logger = logging.getLogger(__name__)

def _usuario_puede_vender(user):
    return _tiene_rol(user, ["Cajero", "Administrador", "Superadmin"]) if hasattr(user, 'is_authenticated') else False

def _es_admin(user):
    return _tiene_rol(user, ["Administrador", "Superadmin"]) if hasattr(user, 'is_authenticated') else False


class VentaListView(LoginRequiredMixin, IsCajeroOrAbove, ListView):
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    paginate_by = 20

    def get_queryset(self):
        qs = Venta.objects.select_related('cajero_user', 'cliente').all()
        if not _es_admin(self.request.user):
            qs = qs.filter(cajero=self.request.user.username)
        return qs.order_by('-fecha_venta')


class VentaDetailView(LoginRequiredMixin, IsCajeroOrAbove, DetailView):
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'

    def get_queryset(self):
        return Venta.objects.select_related('cajero_user', 'cliente').all()

    def test_func(self):
        venta = self.get_object()
        if _es_admin(self.request.user):
            return True
        return self.request.user.username == venta.cajero


class POSView(LoginRequiredMixin, IsCajeroOrAbove, ListView):
    model = Producto
    template_name = 'ventas/pos.html'
    context_object_name = 'productos'

    def get_queryset(self):
        return Producto.objects.filter(
            stock_actual__gt=0
        ).prefetch_related("categorias").order_by('nombre')

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
    cliente_id = _parse_int(request.POST.get("cliente_id"))
    items = []
    for item_data in carrito.values():
        producto = get_object_or_404(Producto, id=item_data["id"])
        items.append({"producto": producto, "cantidad": item_data["cantidad"]})

    try:
        venta = procesar_venta(
            metodo_pago=metodo_pago,
            items=items,
            cajero=request.user.username,
            cliente_id=cliente_id,
        )
    except ValidationError as exc:
        return JsonResponse({"success": False, "error": str(exc)})
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


@login_required
def ajax_buscar_cliente(request):
    if not _usuario_puede_vender(request.user):
        return JsonResponse({"success": False, "error": "No autorizado"}, status=403)

    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"success": False, "error": "Ingrese al menos 2 caracteres"})

    clientes = Cliente.objects.filter(activa=True, nombre__icontains=query).values("id", "nombre", "telefono", "email")[:10]
    return JsonResponse({"success": True, "clientes": list(clientes)})


@login_required
def ajax_buscar_producto_barras(request):
    if not _usuario_puede_vender(request.user):
        return JsonResponse({"success": False, "error": "No autorizado"}, status=403)

    codigo = request.GET.get("codigo", "").strip()
    if not codigo:
        return JsonResponse({"success": False, "error": "Codigo requerido"})

    try:
        producto = Producto.objects.get(codigo_barras=codigo, stock_actual__gt=0)
        return JsonResponse({
            "success": True,
            "producto": {
                "id": producto.id,
                "nombre": producto.nombre,
                "precio": str(producto.precio_venta or producto.precio_costo or 0),
                "stock": float(producto.stock_actual),
            }
        })
    except Producto.DoesNotExist:
        return JsonResponse({"success": False, "error": "Producto no encontrado o sin stock"})


class ClienteListView(LoginRequiredMixin, IsCajeroOrAbove, ListView):
    model = Cliente
    template_name = 'ventas/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 20

    def get_queryset(self):
        qs = Cliente.objects.annotate(num_ventas=Count('ventas'))
        query = self.request.GET.get('q', '').strip()
        if query:
            qs = qs.filter(nombre__icontains=query)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total'] = Cliente.objects.count()
        ctx['activos'] = Cliente.objects.filter(activa=True).count()
        return ctx


class ClienteCreateView(LoginRequiredMixin, IsAdminUser, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'ventas/cliente_form.html'
    success_url = reverse_lazy('cliente_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nuevo Cliente'
        return ctx


class ClienteUpdateView(LoginRequiredMixin, IsAdminUser, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'ventas/cliente_form.html'
    success_url = reverse_lazy('cliente_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Editar Cliente'
        return ctx


class ClienteDeleteView(LoginRequiredMixin, IsAdminUser, DeleteView):
    model = Cliente
    template_name = 'ventas/cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente_list')


@login_required
@require_POST
def ajax_crear_cliente(request):
    if not _usuario_puede_vender(request.user):
        return JsonResponse({"success": False, "error": "No autorizado"}, status=403)

    nombre = request.POST.get("nombre", "").strip()
    if not nombre:
        return JsonResponse({"success": False, "error": "El nombre es obligatorio"})

    try:
        cliente = Cliente.objects.create(
            nombre=nombre,
            telefono=request.POST.get("telefono", "").strip(),
            email=request.POST.get("email", "").strip(),
            rnc=request.POST.get("rnc", "").strip(),
            direccion=request.POST.get("direccion", "").strip(),
            notas=request.POST.get("notas", "").strip(),
        )
        return JsonResponse({
            "success": True,
            "id": cliente.id,
            "nombre": cliente.nombre,
            "telefono": cliente.telefono,
        })
    except Exception as exc:
        return JsonResponse({"success": False, "error": str(exc)})


class ConfiguracionUpdateView(LoginRequiredMixin, IsAdminUser, UpdateView):
    model = ConfiguracionSistema
    form_class = ConfiguracionForm
    template_name = 'ventas/configuracion_form.html'
    success_url = reverse_lazy('configuracion_update')

    def get_object(self, queryset=None):
        obj, _ = ConfiguracionSistema.objects.get_or_create(pk=1)
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Configuracion del Sistema'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Configuracion actualizada correctamente.')
        return super().form_valid(form)

