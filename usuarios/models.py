from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UsuarioPerfil(models.Model):
    """Perfil extendido del usuario"""
    CAJERO = 'cajero'
    ADMINISTRADOR = 'administrador'
    SUPERADMIN = 'superadmin'
    ROLES = (
        (CAJERO, 'Cajero'),
        (ADMINISTRADOR, 'Administrador'),
        (SUPERADMIN, 'Superadmin'),
    )

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default=CAJERO)
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usuario Perfil'
        verbose_name_plural = 'Usuarios Perfil'

    def __str__(self):
        return f"{self.usuario.username} ({self.get_rol_display()})"


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        UsuarioPerfil.objects.get_or_create(usuario=instance)

