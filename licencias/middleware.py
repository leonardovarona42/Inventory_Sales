"""
Middleware que bloquea el acceso al sistema si no hay licencia valida.
"""
import logging
from django.db.utils import ProgrammingError
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)

RUTAS_EXCLUIDAS = {
    "/activar-licencia/",
    "/admin/",
    "/static/",
    "/media/",
    "/favicon.ico",
}


class LicenseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if any(path.startswith(excluida) for excluida in RUTAS_EXCLUIDAS):
            return self.get_response(request)

        try:
            from .services import obtener_licencia_activa, verificar_y_actualizar
            licencia = obtener_licencia_activa()
            if licencia is None:
                return redirect("activar_licencia")
            es_valida, mensaje = verificar_y_actualizar(licencia)
            if not es_valida:
                return redirect("activar_licencia")
        except ProgrammingError:
            # Table doesn't exist yet (migrations not run) - allow access
            pass

        return self.get_response(request)
