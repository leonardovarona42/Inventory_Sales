from django.contrib import admin
from .models import Proveedor, Producto


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'created_at')
    search_fields = ('nombre', 'contacto')
    list_filter = ('created_at',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad_medida', 'stock_actual', 'stock_minimo', 'precio_costo', 'necesita_reorden')
    list_filter = ('unidad_medida', 'proveedor', 'created_at')
    search_fields = ('nombre',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'unidad_medida')
        }),
        ('Stock', {
            'fields': ('stock_actual', 'stock_minimo')
        }),
        ('Finanzas', {
            'fields': ('precio_costo', 'proveedor')
        }),
        ('Imagen', {
            'fields': ('imagen',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
