from django.db import models
from productos.models import Producto


class MovimientoStock(models.Model):
    """Movimientos de entrada y salida de stock"""
    ENTRADA = 'entrada'
    SALIDA = 'salida'
    TIPOS_MOVIMIENTO = (
        (ENTRADA, 'Entrada'),
        (SALIDA, 'Salida'),
    )

    COMPRA = 'compra'
    VENTA = 'venta'
    AJUSTE = 'ajuste'
    MERMA = 'merma'
    DEVOLUCION = 'devolucion'
    MOTIVOS = (
        (COMPRA, 'Compra a proveedor'),
        (VENTA, 'Venta'),
        (AJUSTE, 'Ajuste de inventario'),
        (MERMA, 'Merma/Pérdida'),
        (DEVOLUCION, 'Devolución'),
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
        ordering = ['-fecha']
        verbose_name = 'Movimiento Stock'
        verbose_name_plural = 'Movimientos Stock'
        indexes = [
            models.Index(fields=['producto', '-fecha']),
            models.Index(fields=['motivo', '-fecha']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre} x {self.cantidad} ({self.get_motivo_display()})"
