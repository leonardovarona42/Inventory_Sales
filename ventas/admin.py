from django.contrib import admin
from .models import Venta, DetalleVenta


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('precio_unitario',)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('codigo_ticket', 'cajero', 'cajero_user', 'fecha_venta', 'metodo_pago', 'total_pagado')
    list_filter = ('metodo_pago', 'fecha_venta')
    search_fields = ('codigo_ticket', 'cajero')
    readonly_fields = ('fecha_venta', 'created_at', 'updated_at', 'total_pagado')
    inlines = [DetalleVentaInline]
    date_hierarchy = 'fecha_venta'
    fieldsets = (
        ('Informacion de la Venta', {
            'fields': ('codigo_ticket', 'cajero', 'cajero_user', 'metodo_pago')
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
    list_display = ('venta', 'id_producto', 'cantidad', 'precio_unitario')
    list_filter = ('id_producto', 'created_at')
    search_fields = ('id_producto__nombre',)
    readonly_fields = ('precio_unitario', 'created_at')
