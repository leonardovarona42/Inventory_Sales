from django.contrib import admin
from .models import Orden


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('numero_orden', 'cliente_nombre', 'fecha_hora', 'estado', 'total')
    list_filter = ('estado', 'fecha_hora')
    search_fields = ('numero_orden', 'cliente_nombre', 'cliente_telefono')
    readonly_fields = ('numero_orden', 'fecha_hora', 'created_at', 'updated_at')
    date_hierarchy = 'fecha_hora'
    fieldsets = (
        ('Información de la Orden', {
            'fields': ('numero_orden', 'estado')
        }),
        ('Cliente', {
            'fields': ('cliente_nombre', 'cliente_telefono')
        }),
        ('Detalles', {
            'fields': ('total', 'notas')
        }),
        ('Fechas', {
            'fields': ('fecha_hora', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
