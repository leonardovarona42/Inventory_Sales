from django.contrib import admin
from .models import Venta, DetalleVenta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('precio_unitario',)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'orden', 'fecha_venta', 'metodo_pago', 'total_pagado')
    list_filter = ('metodo_pago', 'fecha_venta')
    search_fields = ('orden__numero_orden', 'id')
    readonly_fields = ('fecha_venta', 'created_at', 'updated_at', 'total_pagado')
    inlines = [DetalleVentaInline]
    date_hierarchy = 'fecha_venta'
    fieldsets = (
        ('Información de la Venta', {
            'fields': ('orden', 'metodo_pago')
        }),
        ('Totales', {
            'fields': ('total_pagado',)
        }),
        ('Fechas', {
            'fields': ('fecha_venta', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'id_producto_final', 'cantidad', 'precio_unitario')
    list_filter = ('id_producto_final', 'created_at')
    search_fields = ('id_producto_final__nombre',)
    readonly_fields = ('precio_unitario', 'created_at')
