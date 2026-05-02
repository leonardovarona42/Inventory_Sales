from decimal import Decimal

from django.db import transaction

from .models import Venta, DetalleVenta


@transaction.atomic
def procesar_venta(*, orden, metodo_pago, items):
    """
    Registra una venta completa dentro de una transaccion atomica.

    items: lista de dicts con llaves `producto_final` y `cantidad`.
    """
    venta = Venta.objects.create(
        orden=orden,
        metodo_pago=metodo_pago,
        total_pagado=Decimal("0"),
    )

    for item in items:
        DetalleVenta.objects.create(
            venta=venta,
            id_producto_final=item["producto_final"],
            cantidad=item["cantidad"],
            precio_unitario=item["producto_final"].precio_actual,
        )

    venta.total_pagado = venta.calcular_total()
    venta.save(update_fields=["total_pagado", "updated_at"])
    return venta
