"""
Middleware que bloquea el acceso al sistema si no hay licencia valida.
Proteccion anti-manipulacion incluida.
"""
import logging
from django.db.utils import ProgrammingError, OperationalError
from django.shortcuts import redirect
from django.db import connection
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

# Rutas excluidas: SOLO activacion de licencia y recursos estaticos.
# Admin NO esta excluido - se verifica licencia antes de permitir acceso.
RUTAS_EXCLUIDAS = {
    "/activar-licencia/",
    "/static/",
    "/media/",
    "/favicon.ico",
}


class LicenseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._migration_checked = False
        self._migrations_ok = False

    def _migrations_complete(self):
        """Verifica que las migraciones de licencias existen."""
        try:
            return self.__class__._migrations_ok
        except AttributeError:
            pass

        try:
            from django.db import connection
            with connection.cursor() as cursor:
                from django.conf import settings
                app_label = "licencias"
                # Check django_migrations table for licencias
                table_name = connection.ops.quote_name("django_migrations")
                cursor.execute(
                    f"SELECT COUNT(*) FROM {table_name} WHERE app = %s",
                    [app_label]
                )
                count = cursor.fetchone()[0]
                LicenseMiddleware._migrations_ok = count > 0
                return count > 0
        except (ProgrammingError, OperationalError):
            LicenseMiddleware._migrations_ok = False
            return False

    def __call__(self, request):
        path = request.path

        # Excluir solo activacion y recursos estaticos
        if any(path.startswith(excluida) for excluida in RUTAS_EXCLUIDAS):
            return self.get_response(request)

        # Verificar que las migraciones se ejecutaron
        if not self._migrations_complete():
            # Si no hay superuser aun, permitir (instalacion inicial)
            User = get_user_model()
            try:
                if not User.objects.filter(is_superuser=True).exists():
                    return self.get_response(request)
            except (ProgrammingError, OperationalError):
                # DB no existe todavia - permitir
                return self.get_response(request)
            # Hay superuser pero no migraciones de licencia = posible evasion
            # Redirect to activation - no permitir acceso
            return redirect("activar_licencia")

        try:
            from .services import obtener_licencia_activa, verificar_y_actualizar
            licencia = obtener_licencia_activa()
            if licencia is None:
                return redirect("activar_licencia")
            es_valida, mensaje = verificar_y_actualizar(licencia)
            if not es_valida:
                return redirect("activar_licencia")
        except (ProgrammingError, OperationalError):
            # Tabla no existe - no permitir acceso
            return redirect("activar_licencia")

        return self.get_response(request)
