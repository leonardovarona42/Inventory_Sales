from decimal import Decimal

from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Venta, DetalleVenta
from inventario.models import MovimientoStock


@transaction.atomic
def procesar_venta(*, orden, metodo_pago, items):
    """
    Registra una venta completa dentro de una transacción atómica.
    Incluye: creación de venta, detalle, descuento de stock y movimientos.

    items: lista de dicts con llaves `producto_final` y `cantidad`.
    
    Retorna: instancia de Venta
    
    Lanza: ValidationError si stock insuficiente
    """
    # PASO 1: Validar stock disponible para TODOS los items
    errores_stock = []
    
    for item in items:
        producto_final = item["producto_final"]
        cantidad = item["cantidad"]
        
        if not hasattr(producto_final, 'receta'):
            errores_stock.append(
                f"{producto_final.nombre}: No tiene receta asociada"
            )
            continue
        
        receta = producto_final.receta
        for detalle_receta in receta.detalles.all():
            cantidad_necesaria = detalle_receta.cantidad_necesaria * cantidad
            stock_disponible = detalle_receta.producto.stock_actual
            
            if stock_disponible < cantidad_necesaria:
                errores_stock.append(
                    f"{detalle_receta.producto.nombre}: "
                    f"necesario {cantidad_necesaria} {detalle_receta.producto.unidad_medida}, "
                    f"disponible {stock_disponible}"
                )
    
    if errores_stock:
        raise ValidationError(errores_stock)
    
    # PASO 2: Crear venta
    venta = Venta.objects.create(
        orden=orden,
        metodo_pago=metodo_pago,
        total_pagado=Decimal("0"),
    )
    
    # PASO 3: Crear detalles de venta
    detalles_creados = []
    for item in items:
        detalle = DetalleVenta.objects.create(
            venta=venta,
            id_producto_final=item["producto_final"],
            cantidad=item["cantidad"],
            precio_unitario=item["producto_final"].precio_actual,
        )
        detalles_creados.append(detalle)
    
    # PASO 4: Descontar stock y registrar movimientos
    for detalle in detalles_creados:
        _descontar_stock_y_registrar(detalle)
    
    # PASO 5: Actualizar total y guardar
    venta.total_pagado = venta.calcular_total()
    venta.save(update_fields=["total_pagado", "updated_at"])
    
    # PASO 6: Actualizar estado de orden si existe
    if orden and orden.estado == 'pendiente':
        orden.cambiar_estado('preparando')
    
    return venta


def _descontar_stock_y_registrar(detalle_venta):
    """
    Descuenta stock de insumos y registra movimientos.
    Se asume que ya se validó el stock previamente.
    """
    receta = detalle_venta.id_producto_final.receta
    
    for detalle_receta in receta.detalles.all():
        cantidad_a_descontar = detalle_receta.cantidad_necesaria * detalle_venta.cantidad
        producto = detalle_receta.producto
        
        # Actualizar stock
        producto.stock_actual -= cantidad_a_descontar
        producto.save(update_fields=["stock_actual", "updated_at"])
        
        # Registrar movimiento de salida
        MovimientoStock.objects.create(
            producto=producto,
            tipo='salida',
            cantidad=cantidad_a_descontar,
            motivo='venta',
            referencia_id=detalle_venta.venta.id,
            notas=f"Venta #{detalle_venta.venta.id}: "
                  f"{detalle_venta.id_producto_final.nombre} "
                  f"x{detalle_venta.cantidad}"
        )


@transaction.atomic
def cancelar_venta(venta, motivo):
    """
    Cancela una venta y revierte el stock.
    
    Lanza: ValidationError si no se puede cancelar
    """
    if venta.detalles.count() == 0:
        raise ValidationError("Venta sin detalles")
    
    # Revertir movimientos de stock
    for detalle in venta.detalles.all():
        receta = detalle.id_producto_final.receta
        for detalle_receta in receta.detalles.all():
            cantidad_revertir = detalle_receta.cantidad_necesaria * detalle.cantidad
            producto = detalle_receta.producto
            
            # Revertir stock
            producto.stock_actual += cantidad_revertir
            producto.save(update_fields=["stock_actual", "updated_at"])
            
            # Registrar movimiento de reversión
            MovimientoStock.objects.create(
                producto=producto,
                tipo='entrada',
                cantidad=cantidad_revertir,
                motivo='ajuste',
                referencia_id=venta.id,
                notas=f"Cancelación Venta #{venta.id}: "
                      f"reversión de {detalle.id_producto_final.nombre}"
            )
    
    # Marcar venta como cancelada (soft delete)
    venta.delete()  # Soft delete si está configurado
    
    # Actualizar orden asociada
    if venta.orden:
        venta.orden.cambiar_estado('cancelado')
