from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from ventas.models import Venta
from productos.models import Producto
from inventario.models import MovimientoStock


class Command(BaseCommand):
    help = 'Crea los grupos del sistema con sus permisos correspondientes'

    def handle(self, *args, **options):
        self.stdout.write('Configurando grupos del sistema...')

        # Crear grupo Superadmin
        superadmin, created = Group.objects.get_or_create(name='Superadmin')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo Superadmin creado'))
        # Superadmin tiene todos los permisos (no se asignan explicitamente)

        # Crear grupo Administrador
        admin_group, created = Group.objects.get_or_create(name='Administrador')
        if created:
            # Permisos para gestionar productos e inventario
            perms = [
                ('add_producto', Producto),
                ('change_producto', Producto),
                ('delete_producto', Producto),
                ('view_producto', Producto),
                ('add_movimientostock', MovimientoStock),
                ('view_movimientostock', MovimientoStock),
                ('view_venta', Venta),
            ]
            for perm_codename, model in perms:
                perm = Permission.objects.get(codename=perm_codename, content_type=ContentType.objects.get_for_model(model))
                admin_group.permissions.add(perm)
            self.stdout.write(self.style.SUCCESS('Grupo Administrador creado con permisos'))

        # Crear grupo Cajero
        cajero, created = Group.objects.get_or_create(name='Cajero')
        if created:
            # Permisos solo para ventas y POS
            perms = [
                ('add_venta', Venta),
                ('view_venta', Venta),
                ('change_venta', Venta),
                ('view_producto', Producto),
            ]
            for perm_codename, model in perms:
                perm = Permission.objects.get(codename=perm_codename, content_type=ContentType.objects.get_for_model(model))
                cajero.permissions.add(perm)
            self.stdout.write(self.style.SUCCESS('Grupo Cajero creado con permisos'))

        self.stdout.write(self.style.SUCCESS('Configuracion de grupos completada'))
        self.stdout.write(f'\nGrupos existentes:')
        for g in Group.objects.all():
            self.stdout.write(f'  - {g.name} ({g.permissions.count()} permisos)')
