import logging
from decimal import Decimal

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Venta, DetalleVenta
from productos.models import Producto
from inventario.models import MovimientoStock

logger = logging.getLogger(__name__)


def _generar_ticket(venta):
    """Genera el codigo de ticket unico para una venta."""
    return f"V-{venta.fecha_venta.strftime('%Y%m%d')}-{venta.pk:06d}"


@transaction.atomic
def procesar_venta(*, metodo_pago, items, cajero="", cliente_id=None):
    """
    Registra una venta completa dentro de una transaccion atomica.

    items: lista de dicts con llaves `producto` y `cantidad`.
            Los productos deben estar bloqueados con select_for_update.
    cliente_id: ID del cliente (opcional, null para venta sin cliente)

    Retorna: instancia de Venta

    Lanza: ValidationError si stock insuficiente
    """
    from django.db import transaction as db_transaction

    errores_stock = []

    productos_ids = [item["producto"].id for item in items]
    productos_locked = Producto.objects.select_for_update().filter(id__in=productos_ids)
    producto_por_id = {p.id: p for p in productos_locked}

    for item in items:
        producto = producto_por_id.get(item["producto"].id)
        if not producto:
            errores_stock.append(f"{item['producto'].nombre}: producto no encontrado")
            continue
        cantidad = item["cantidad"]
        if producto.stock_actual < cantidad:
            errores_stock.append(
                f"{producto.nombre}: necesario {cantidad}, disponible {producto.stock_actual}"
            )

    if errores_stock:
        raise ValidationError(errores_stock)

    venta = Venta.objects.create(
        metodo_pago=metodo_pago,
        total_pagado=Decimal("0"),
        cajero=cajero,
        cliente_id=cliente_id if cliente_id else None,
    )

    if cajero:
        try:
            from django.contrib.auth.models import User
            venta.cajero_user = User.objects.filter(username=cajero).first()
            venta.save(update_fields=["cajero_user"])
        except Exception:
            pass

    venta.codigo_ticket = _generar_ticket(venta)
    venta.save(update_fields=["codigo_ticket"])

    detalles_creados = []
    total_venta = Decimal("0")
    for item in items:
        producto = producto_por_id[item["producto"].id]
        precio = producto.precio_venta or producto.precio_costo or Decimal("0")
        detalle = DetalleVenta.objects.create(
            venta=venta,
            id_producto=producto,
            cantidad=item["cantidad"],
            precio_unitario=precio,
        )
        detalles_creados.append(detalle)
        total_venta += detalle.cantidad * detalle.precio_unitario

        producto.stock_actual -= item["cantidad"]
        producto.save(update_fields=["stock_actual", "updated_at"])

        MovimientoStock.objects.create(
            producto=producto,
            tipo='salida',
            cantidad=item["cantidad"],
            motivo='venta',
            referencia_id=venta.id,
            notas=f"Venta #{venta.codigo_ticket}: {producto.nombre} x{item['cantidad']}"
        )

    venta.total_pagado = total_venta
    venta.save(update_fields=["total_pagado"])

    return venta


@transaction.atomic
def cancelar_venta(venta_id, motivo=""):
    """
    Cancela una venta y revierte el stock.
    """
    try:
        venta = Venta.objects.get(id=venta_id)
    except Venta.DoesNotExist:
        raise ValidationError("Venta no encontrada")

    if venta.detalles.count() == 0:
        raise ValidationError("Venta sin detalles")

    for detalle in venta.detalles.all():
        producto = detalle.id_producto
        producto.stock_actual += detalle.cantidad
        producto.save(update_fields=["stock_actual", "updated_at"])

        MovimientoStock.objects.create(
            producto=producto,
            tipo='entrada',
            cantidad=detalle.cantidad,
            motivo='devolucion',
            referencia_id=venta.id,
            notas=f"Cancelacion Venta #{venta.codigo_ticket}: {producto.nombre}"
        )

    venta.detalles.all().delete()
    venta.delete()
