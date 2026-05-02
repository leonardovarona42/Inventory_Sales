from django.db import models
from django.utils import timezone
from datetime import datetime


class Orden(models.Model):
    """Orden de compra/venta (pedidos)"""
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('preparando', 'En preparación'),
        ('listo', 'Listo para entregar'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )

    numero_orden = models.CharField(max_length=20, unique=True, editable=False)
    cliente_nombre = models.CharField(max_length=100, blank=True)
    cliente_telefono = models.CharField(max_length=20, blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'ordenes'
        ordering = ['-fecha_hora']
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        indexes = [
            models.Index(fields=['numero_orden']),
            models.Index(fields=['estado', '-fecha_hora']),
        ]

    def __str__(self):
        return self.numero_orden

    def save(self, *args, **kwargs):
        # Generar número de orden si no existe
        if not self.numero_orden:
            hoy = datetime.now().strftime('%Y%m%d')
            # Contar órdenes del día
            ordenes_hoy = Orden.objects.filter(
                numero_orden__contains=f'ORD-{hoy}'
            ).count()
            self.numero_orden = f'ORD-{hoy}-{str(ordenes_hoy + 1).zfill(3)}'
        super().save(*args, **kwargs)

    def cambiar_estado(self, nuevo_estado):
        """Cambia el estado de la orden"""
        estados_validos = [estado[0] for estado in self.ESTADOS]
        if nuevo_estado in estados_validos:
            self.estado = nuevo_estado
            self.save()
        else:
            raise ValueError(f"Estado inválido: {nuevo_estado}")
