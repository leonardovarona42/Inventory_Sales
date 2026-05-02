from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError
from recetas.models import ProductoFinal
from ordenes.models import Orden
from inventario.models import MovimientoStock
from productos.models import Producto


class Venta(models.Model):
    """Transacción de venta"""
    METODOS_PAGO = (
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('otro', 'Otro'),
    )

    orden = models.OneToOneField(Orden, on_delete=models.PROTECT, null=True, blank=True, related_name='venta')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=30, choices=METODOS_PAGO)
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'ventas'
        ordering = ['-fecha_venta']
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        indexes = [
            models.Index(fields=['-fecha_venta']),
        ]

    def __str__(self):
        if self.orden:
            return f"Venta #{self.id} - Orden {self.orden.numero_orden}"
        return f"Venta #{self.id}"

    def calcular_total(self):
        """Calcula el total de la venta basado en sus detalles"""
        total = sum(
            detalle.cantidad * detalle.precio_unitario 
            for detalle in self.detalles.all()
        )
        return total

    def save(self, *args, **kwargs):
        # Calcular total si no se ha establecido
        if not self.total_pagado:
            if self.pk:
                self.total_pagado = self.calcular_total()
            else:
                self.total_pagado = 0
        super().save(*args, **kwargs)


class DetalleVenta(models.Model):
    """Detalle de productos en una venta"""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    id_producto_final = models.ForeignKey(ProductoFinal, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'ventas'
        verbose_name = 'Detalle Venta'
        verbose_name_plural = 'Detalles Venta'
        indexes = [
            models.Index(fields=['id_producto_final', '-created_at']),
        ]

    def __str__(self):
        return f"{self.id_producto_final.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        # Usar el precio actual del producto si no se especificó
        if not self.precio_unitario:
            self.precio_unitario = self.id_producto_final.precio_actual

        with transaction.atomic():
            # Validar que haya suficiente stock
            self._verificar_stock()

            # Registrar el cambio en la base de datos antes de descontar stock
            es_nueva = not self.pk
            super().save(*args, **kwargs)

            # Descontar stock y registrar movimientos solo si es nuevo
            if es_nueva:
                self._descontar_stock()

    def _verificar_stock(self):
        """Verifica que haya suficiente stock de todos los insumos"""
        if not hasattr(self.id_producto_final, 'receta'):
            raise ValidationError("El producto no tiene receta asociada")
        
        receta = self.id_producto_final.receta
        errores = []
        
        for detalle_receta in receta.detalles.all():
            cantidad_necesaria = detalle_receta.cantidad_necesaria * self.cantidad
            stock_disponible = detalle_receta.producto.stock_actual
            
            if stock_disponible < cantidad_necesaria:
                errores.append(
                    f"Stock insuficiente de {detalle_receta.producto.nombre}: "
                    f"necesario {cantidad_necesaria} {detalle_receta.producto.unidad_medida}, "
                    f"disponible {stock_disponible}"
                )
        
        if errores:
            raise ValidationError(errores)

    def _descontar_stock(self):
        """Descuenta el stock de todos los insumos necesarios"""
        receta = self.id_producto_final.receta
        
        for detalle_receta in receta.detalles.all():
            cantidad_a_descontar = detalle_receta.cantidad_necesaria * self.cantidad
            producto = detalle_receta.producto
            
            # Actualizar stock
            producto.stock_actual -= cantidad_a_descontar
            producto.save()
            
            # Registrar movimiento
            MovimientoStock.objects.create(
                producto=producto,
                tipo='salida',
                cantidad=cantidad_a_descontar,
                motivo='venta',
                referencia_id=self.venta.id,
                notas=f"Venta: {self.id_producto_final.nombre}"
            )
