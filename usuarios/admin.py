from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.utils import IntegrityError
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


class UsuarioInline(admin.StackedInline):
    model = UsuarioPerfil
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'usuario'
    extra = 0


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_roles')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informacion personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions'),
        }),
        ('Miembro de grupos', {
            'description': 'Selecciona uno o mas grupos a los que pertenece este usuario.',
            'fields': ('groups',),
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'is_staff', 'is_superuser'),
        }),
    )

    def get_roles(self, obj):
        if obj.is_superuser:
            return "Superusuario (todos los permisos)"
        roles = list(obj.groups.values_list('name', flat=True))
        return ", ".join(roles) if roles else "Sin grupo"
    get_roles.short_description = "Grupos"


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

