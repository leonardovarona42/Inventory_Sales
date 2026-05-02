from django.contrib import admin
from .models import UsuarioPerfil


@admin.register(UsuarioPerfil)
class UsuarioPerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'activo', 'created_at')
    list_filter = ('rol', 'activo', 'created_at')
    search_fields = ('usuario__username', 'usuario__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Perfil', {
            'fields': ('rol', 'telefono', 'activo')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
