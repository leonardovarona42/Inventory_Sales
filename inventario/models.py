from django.db import models
from productos.models import Producto


class MovimientoStock(models.Model):
    """Movimientos de entrada y salida de stock"""
    TIPOS_MOVIMIENTO = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    )

    MOTIVOS = (
        ('compra', 'Compra a proveedor'),
        ('venta', 'Venta'),
        ('ajuste', 'Ajuste de inventario'),
        ('merma', 'Merma/Pérdida'),
        ('devolucion', 'Devolución'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPOS_MOVIMIENTO)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=50, choices=MOTIVOS)
    referencia_id = models.PositiveIntegerField(blank=True, null=True, help_text="ID de orden o venta asociada")
    notas = models.TextField(blank=True)
    usuario = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'inventario'
        ordering = ['-fecha']
        verbose_name = 'Movimiento Stock'
        verbose_name_plural = 'Movimientos Stock'
        indexes = [
            models.Index(fields=['producto', '-fecha']),
            models.Index(fields=['motivo', '-fecha']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre} x {self.cantidad} ({self.get_motivo_display()})"
