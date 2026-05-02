from django.contrib import admin
from .models import MovimientoStock


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'motivo', 'fecha')
    list_filter = ('tipo', 'motivo', 'fecha')
    search_fields = ('producto__nombre', 'notas')
    readonly_fields = ('fecha', 'created_at', 'producto')
    date_hierarchy = 'fecha'
    fieldsets = (
        ('Información del Movimiento', {
            'fields': ('producto', 'tipo', 'cantidad', 'motivo')
        }),
        ('Referencia', {
            'fields': ('referencia_id', 'notas')
        }),
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Fechas', {
            'fields': ('fecha', 'created_at'),
            'classes': ('collapse',)
        }),
    )
