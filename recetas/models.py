from django.db import models
from django.utils import timezone
from productos.models import Producto


class ProductoFinal(models.Model):
    """Producto final compuesto por insumos"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio_base = models.DecimalField(max_digits=8, decimal_places=2)
    precio_actual = models.DecimalField(max_digits=8, decimal_places=2, editable=False)
    umbral_demanda_alta = models.IntegerField(default=30, help_text="Ventas en 24h que activan incremento")
    incremento_por_demanda = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    imagen = models.ImageField(upload_to='recetas/')
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'recetas'
        ordering = ['nombre']
        verbose_name = 'Producto Final'
        verbose_name_plural = 'Productos Finales'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # Si precio_actual no está establecido, usar precio_base
        if not self.precio_actual:
            self.precio_actual = self.precio_base
        super().save(*args, **kwargs)

    def calcular_precio_dinamico(self):
        """Calcula y actualiza el precio según la demanda"""
        from django.utils import timezone
        from datetime import timedelta
        from ventas.models import DetalleVenta, Venta
        
        ahora = timezone.now()
        hace_24h = ahora - timedelta(hours=24)
        
        # Contar ventas en las últimas 24 horas
        ventas_24h = DetalleVenta.objects.filter(
            id_producto_final=self,
            venta__fecha_venta__gte=hace_24h
        ).aggregate(models.Sum('cantidad'))['cantidad__sum'] or 0
        
        precio_anterior = self.precio_actual
        
        if ventas_24h >= self.umbral_demanda_alta:
            self.precio_actual = self.precio_base + self.incremento_por_demanda
        else:
            self.precio_actual = self.precio_base
        
        # Guardar cambio en historial si hubo variación
        if precio_anterior != self.precio_actual:
            razon = 'demanda' if ventas_24h >= self.umbral_demanda_alta else 'manual'
            HistorialPrecioProducto.objects.create(
                producto=self,
                precio_anterior=precio_anterior,
                precio_nuevo=self.precio_actual,
                razon=razon
            )
            self.save()


class Receta(models.Model):
    """Receta para un producto final"""
    producto_final = models.OneToOneField(ProductoFinal, on_delete=models.CASCADE, related_name='receta')
    instrucciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'recetas'
        verbose_name = 'Receta'
        verbose_name_plural = 'Recetas'

    def __str__(self):
        return f"Receta de {self.producto_final.nombre}"


class DetalleReceta(models.Model):
    """Detalle de los insumos en una receta"""
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad_necesaria = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        help_text="Cantidad de insumo necesaria por unidad del producto final"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'recetas'
        unique_together = ('receta', 'producto')
        verbose_name = 'Detalle Receta'
        verbose_name_plural = 'Detalles Receta'

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad_necesaria} para {self.receta.producto_final.nombre}"


class HistorialPrecioProducto(models.Model):
    """Historial de cambios de precio de productos finales"""
    RAZONES_CAMBIO = (
        ('demanda', 'Demanda alta'),
        ('manual', 'Ajuste manual'),
    )

    producto = models.ForeignKey(ProductoFinal, on_delete=models.CASCADE, related_name='historial_precios')
    fecha = models.DateTimeField(auto_now_add=True)
    precio_anterior = models.DecimalField(max_digits=8, decimal_places=2)
    precio_nuevo = models.DecimalField(max_digits=8, decimal_places=2)
    razon = models.CharField(max_length=20, choices=RAZONES_CAMBIO)

    class Meta:
        app_label = 'recetas'
        ordering = ['-fecha']
        verbose_name = 'Historial Precio'
        verbose_name_plural = 'Historial Precios'

    def __str__(self):
        return f"{self.producto.nombre}: {self.precio_anterior} → {self.precio_nuevo} ({self.razon})"
