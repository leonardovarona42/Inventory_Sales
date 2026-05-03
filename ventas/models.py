from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from productos.models import Producto
from inventario.models import MovimientoStock


class Venta(models.Model):
    """TransacciOn de venta"""
    METODOS_PAGO = (
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('otro', 'Otro'),
    )

    codigo_ticket = models.CharField(max_length=30, unique=True, blank=True)
    cajero = models.CharField(max_length=150, blank=True)
    cajero_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
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
            models.Index(fields=['cajero', '-fecha_venta']),
        ]

    def __str__(self):
        return f"Venta #{self.codigo_ticket} - ${self.total_pagado}"

    def save(self, *args, **kwargs):
        generar_ticket = not self.codigo_ticket
        if not self.total_pagado:
            self.total_pagado = 0
        super().save(*args, **kwargs)
        if generar_ticket:
            self.codigo_ticket = f"V-{self.fecha_venta.strftime('%Y%m%d')}-{self.pk:06d}"
            super().save(update_fields=["codigo_ticket"])


class DetalleVenta(models.Model):
    """Detalle de productos en una venta"""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    id_producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'ventas'
        verbose_name = 'Detalle Venta'
        verbose_name_plural = 'Detalles Venta'

    def __str__(self):
        return f"{self.id_producto.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        if not self.precio_unitario and self.id_producto:
            self.precio_unitario = self.id_producto.precio_actual or self.id_producto.precio_base
        super().save(*args, **kwargs)

    def clean(self):
        if self.id_producto and self.id_producto.tipo_producto != 'final':
            raise ValidationError("Solo se pueden vender productos de tipo 'final'")
