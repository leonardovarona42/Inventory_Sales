from django.contrib import admin
from .models import Proveedor, Producto, Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'padre', 'orden', 'activa')
    list_filter = ('activa', 'padre')
    search_fields = ('nombre',)
    ordering = ('orden', 'nombre')


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'created_at')
    search_fields = ('nombre', 'contacto')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad_medida', 'stock_actual', 'stock_minimo', 'precio_venta', 'necesita_reorden')
    list_filter = ('categorias', 'created_at')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('categorias',)
    fieldsets = (
        ('Informacion', {'fields': ('nombre', 'descripcion')}),
        ('Stock', {'fields': ('unidad_medida', 'stock_actual', 'stock_minimo')}),
        ('Precios', {'fields': ('precio_costo', 'precio_venta')}),
        ('Clasificacion', {'fields': ('categorias', 'proveedor', 'imagen')}),
        ('Fechas', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
