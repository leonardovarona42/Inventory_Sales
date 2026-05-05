from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Cliente(models.Model):
    """Cliente del sistema de ventas"""
    nombre = models.CharField(max_length=150)
    email = models.EmailField(blank=True, default="")
    telefono = models.CharField(max_length=30, blank=True, default="")
    direccion = models.TextField(blank=True, default="")
    rnc = models.CharField(max_length=50, blank=True, default="")
    notas = models.TextField(blank=True, default="")
    activa = models.BooleanField(default=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['telefono']),
        ]

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    """Transaccion de venta"""
    METODOS_PAGO = (
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('otro', 'Otro'),
    )

    codigo_ticket = models.CharField(max_length=30, unique=True, blank=True)
    cajero = models.CharField(max_length=150, blank=True)
    cajero_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=30, choices=METODOS_PAGO)
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_venta']
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        indexes = [
            models.Index(fields=['-fecha_venta']),
            models.Index(fields=['cajero', '-fecha_venta']),
            models.Index(fields=['cliente', '-fecha_venta']),
        ]

    def __str__(self):
        cliente_str = f" - {self.cliente.nombre}" if self.cliente else ""
        return f"Venta #{self.codigo_ticket} - ${self.total_pagado}{cliente_str}"

    def save(self, *args, **kwargs):
        if not self.total_pagado:
            self.total_pagado = 0
        super().save(*args, **kwargs)


class DetalleVenta(models.Model):
    """Detalle de productos en una venta"""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    id_producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Detalle Venta'
        verbose_name_plural = 'Detalles Venta'

    def __str__(self):
        return f"{self.id_producto.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        if not self.precio_unitario and self.id_producto:
            self.precio_unitario = self.id_producto.precio_venta or self.id_producto.precio_costo or Decimal("0")
        super().save(*args, **kwargs)

    def clean(self):
        if self.cantidad is not None and self.cantidad <= 0:
            from django.core.exceptions import ValidationError
            raise ValidationError("La cantidad debe ser mayor a 0")
