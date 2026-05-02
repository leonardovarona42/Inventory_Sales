from django.db import models


class Proveedor(models.Model):
    """Proveedor de insumos"""
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=150, help_text="Teléfono o email")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'productos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Insumo (materia prima)"""
    UNIDADES_MEDIDA = (
        ('kg', 'Kilogramos'),
        ('g', 'Gramos'),
        ('litro', 'Litro'),
        ('ml', 'Mililitro'),
        ('unidad', 'Unidad'),
        ('paquete', 'Paquete'),
    )

    nombre = models.CharField(max_length=100)
    unidad_medida = models.CharField(max_length=20, choices=UNIDADES_MEDIDA)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    precio_costo = models.DecimalField(max_digits=8, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='productos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'productos'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.unidad_medida})"

    def necesita_reorden(self):
        """Verifica si el producto está por debajo del stock mínimo"""
        return self.stock_actual < self.stock_minimo
