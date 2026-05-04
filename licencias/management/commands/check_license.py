from django.core.management.base import BaseCommand
from django.utils import timezone
from licencias.models import Licencia
from licencias.services import verificar_y_actualizar, obtener_licencia_activa


class Command(BaseCommand):
    help = "Verifica el estado de la licencia activa del sistema"

    def handle(self, *args, **options):
        licencia = obtener_licencia_activa()

        if not licencia:
            self.stdout.write(
                self.style.ERROR("No hay licencia activa. El sistema esta bloqueado.")
            )
            return

        es_valida, mensaje = verificar_y_actualizar(licencia)

        if es_valida:
            self.stdout.write(self.style.SUCCESS(f"LICENCIA ACTIVA"))
            self.stdout.write(f"  Cliente: {licencia.cliente_nombre}")
            self.stdout.write(f"  Tipo: {licencia.get_tipo_display()}")
            self.stdout.write(f"  Estado: {mensaje}")
            if licencia.fecha_vencimiento:
                self.stdout.write(f"  Vencimiento: {licencia.fecha_vencimiento.strftime('%Y-%m-%d %H:%M')}")
            else:
                self.stdout.write("  Vencimiento: Perpetua")
        else:
            self.stdout.write(self.style.ERROR(f"LICENCIA NO VALIDA"))
            self.stdout.write(f"  Cliente: {licencia.cliente_nombre}")
            self.stdout.write(f"  Motivo: {mensaje}")
