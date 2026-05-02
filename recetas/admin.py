from django.contrib import admin
from .models import ProductoFinal, Receta, DetalleReceta, HistorialPrecioProducto


class DetalleRecetaInline(admin.TabularInline):
    model = DetalleReceta
    extra = 1


@admin.register(ProductoFinal)
class ProductoFinalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'precio_actual', 'umbral_demanda_alta', 'ultima_actualizacion')
    list_filter = ('umbral_demanda_alta', 'created_at')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('precio_actual', 'ultima_actualizacion', 'created_at')
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'imagen')
        }),
        ('Precios', {
            'fields': ('precio_base', 'precio_actual')
        }),
        ('Configuración de Demanda', {
            'fields': ('umbral_demanda_alta', 'incremento_por_demanda')
        }),
        ('Fechas', {
            'fields': ('ultima_actualizacion', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('producto_final', 'created_at')
    search_fields = ('producto_final__nombre',)
    inlines = [DetalleRecetaInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(HistorialPrecioProducto)
class HistorialPrecioProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'fecha', 'precio_anterior', 'precio_nuevo', 'razon')
    list_filter = ('razon', 'fecha')
    search_fields = ('producto__nombre',)
    readonly_fields = ('fecha', 'producto', 'precio_anterior', 'precio_nuevo', 'razon')
    date_hierarchy = 'fecha'
