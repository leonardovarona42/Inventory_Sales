from django.db import models
from django.contrib.auth.models import User


class UsuarioPerfil(models.Model):
    """Perfil extendido del usuario"""
    ROLES = (
        ('admin', 'Administrador'),
        ('chef', 'Chef'),
        ('cajero', 'Cajero'),
        ('superadmin', 'Superadmin'),
    )

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='cajero')
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'usuarios'
        verbose_name = 'Usuario Perfil'
        verbose_name_plural = 'Usuarios Perfil'

    def __str__(self):
        return f"{self.usuario.username} ({self.get_rol_display()})"
