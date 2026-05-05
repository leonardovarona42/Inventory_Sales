from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal


class ConfiguracionSistema(models.Model):
    """Configuración global del sistema (singleton)"""
    nombre_negocio = models.CharField(max_length=150, default="Mi Negocio", verbose_name="Nombre del Negocio")
    rnc_negocio = models.CharField(max_length=50, blank=True, default="", verbose_name="RNC del Negocio")
    direccion = models.TextField(blank=True, default="", verbose_name="Dirección")
    telefono = models.CharField(max_length=30, blank=True, default="", verbose_name="Teléfono")
    email = models.EmailField(blank=True, default="", verbose_name="Email")
    simbolo_moneda = models.CharField(max_length=5, default="RD$", verbose_name="Símbolo de Moneda")
    tasa_impuesto = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"), verbose_name="Tasa de Impuesto (%)")
    mensaje_recibo_superior = models.TextField(blank=True, default="", verbose_name="Mensaje Recibo (superior)", help_text="Texto que aparece arriba del recibo")
    mensaje_recibo_inferior = models.TextField(blank=True, default="", verbose_name="Mensaje Recibo (inferior)", help_text="Texto que aparece abajo del recibo")
    pie_pagina = models.CharField(max_length=200, blank=True, default="Gracias por su compra", verbose_name="Pie de página")
    logo = models.ImageField(upload_to="logos/", blank=True, null=True, verbose_name="Logo del Negocio")
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuración del Sistema'

    def __str__(self):
        return self.nombre_negocio

    def save(self, *args, **kwargs):
        # Enforce singleton: only one row
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete('configuracion_sistema')

    @classmethod
    def cargar(cls):
        """Obtener la configuracion (cached)"""
        config = cache.get('configuracion_sistema')
        if config is None:
            config, _ = cls.objects.get_or_create(pk=1)
            cache.set('configuracion_sistema', config, timeout=3600)
        return config


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
