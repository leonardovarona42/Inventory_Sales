from django.db import models
from django.core.exceptions import ValidationError


class Categoria(models.Model):
    """Categoria de productos (Aseo, Alimentos, Utiles, Herramientas) con soporte jerarquico"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True, help_text="Clase Font Awesome, ej: fa-soap")
    color = models.CharField(max_length=7, default='#6c757d')
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)
    padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategorias',
        verbose_name='Categoria padre'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        if self.padre:
            return f"{self.padre.nombre} > {self.nombre}"
        return self.nombre

    def get_hijos(self):
        return self.subcategorias.filter(activa=True)


class Proveedor(models.Model):
    """Proveedor de productos"""
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=150, help_text="Telefono o email")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Producto del inventario"""
    UNIDAD = 'unidad'
    KILOGRAMO = 'kg'
    GRAMO = 'g'
    LITRO = 'litro'
    MILILITRO = 'ml'
    PAQUETE = 'paquete'
    CAJA = 'caja'
    UNIDADES_MEDIDA = (
        (UNIDAD, 'Unidad'),
        (KILOGRAMO, 'Kilogramos'),
        (GRAMO, 'Gramos'),
        (LITRO, 'Litros'),
        (MILILITRO, 'Mililitros'),
        (PAQUETE, 'Paquete'),
        (CAJA, 'Caja'),
    )

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    codigo_barras = models.CharField(max_length=50, unique=True, null=True, blank=True, db_index=True, verbose_name="Codigo de Barras")
    lote = models.CharField(max_length=100, blank=True, default="", verbose_name="Lote")
    fecha_vencimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Vencimiento")
    unidad_medida = models.CharField(max_length=20, choices=UNIDADES_MEDIDA, default=UNIDAD)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=5)
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    categorias = models.ManyToManyField(Categoria, blank=True, related_name='productos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['codigo_barras']),
            models.Index(fields=['fecha_vencimiento']),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.stock_actual} {self.unidad_medida})"

    def necesita_reorden(self):
        return self.stock_actual < self.stock_minimo
