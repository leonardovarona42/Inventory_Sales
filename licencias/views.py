"""
Vistas para activación de licencias.
"""
import logging
import time

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

from .services import activar_licencia, obtener_licencia_activa, verificar_y_actualizar

logger = logging.getLogger(__name__)

# Rate limiting simple para activacion (5 intentos por minuto por IP)
_ACTIVATION_ATTEMPTS = {}
_RATE_LIMIT_WINDOW = 60  # segundos
_RATE_LIMIT_MAX = 5


def _check_rate_limit(request):
    """Verifica rate limiting por IP."""
    ip = request.META.get("REMOTE_ADDR", "unknown")
    now = time.time()

    if ip not in _ACTIVATION_ATTEMPTS:
        _ACTIVATION_ATTEMPTS[ip] = []

    # Limpiar intentos viejos
    _ACTIVATION_ATTEMPTS[ip] = [t for t in _ACTIVATION_ATTEMPTS[ip] if now - t < _RATE_LIMIT_WINDOW]

    if len(_ACTIVATION_ATTEMPTS[ip]) >= _RATE_LIMIT_MAX:
        return False

    _ACTIVATION_ATTEMPTS[ip].append(now)
    return True


@require_GET
def activar_licencia_view(request):
    """Pantalla de activación de licencia (pantalla de bloqueo)."""
    licencia = obtener_licencia_activa()
    contexto = {"licencia": licencia}

    if licencia:
        es_valida, mensaje = verificar_y_actualizar(licencia)
        contexto["es_valida"] = es_valida
        contexto["mensaje"] = mensaje
    else:
        contexto["es_valida"] = False
        contexto["mensaje"] = "No se ha activado ninguna licencia"

    return render(request, "licencias/activar_licencia.html", contexto)


@require_POST
@csrf_protect
def procesar_activacion(request):
    """Procesa la activación de una nueva licencia."""
    # Rate limiting
    if not _check_rate_limit(request):
        messages.error(request, "Demasiados intentos. Espere un momento e intente de nuevo.")
        return redirect("activar_licencia")

    licencia_texto = request.POST.get("licencia", "").strip()

    if not licencia_texto:
        messages.error(request, "Ingrese la clave de licencia.")
        return redirect("activar_licencia")

    exito, mensaje, licencia = activar_licencia(licencia_texto)

    if exito:
        messages.success(request, mensaje)
        return redirect("home")
    else:
        messages.error(request, mensaje)
        return redirect("activar_licencia")


@login_required
@require_GET
def acerca_de_view(request):
    """Información del sistema y estado de la licencia."""
    from datetime import datetime, timezone as dt_tz

    licencia = obtener_licencia_activa()
    info = {
        "nombre": "MiNegocio POS",
        "version": "1.0.0",
        "descripcion": "Sistema de Gestión de Inventario y Ventas",
        "licencia": licencia,
    }

    if licencia:
        info["es_valida"], info["mensaje"] = verificar_y_actualizar(licencia)
        ahora = datetime.now(dt_tz.utc)
        if licencia.fecha_vencimiento:
            restante = licencia.fecha_vencimiento - ahora
            info["dias_restantes"] = max(0, restante.days)
        else:
            info["dias_restantes"] = None  # perpetua
    else:
        info["es_valida"] = False
        info["mensaje"] = "Sin licencia activa"
        info["dias_restantes"] = 0

    return render(request, "licencias/acerca_de.html", info)


@login_required
@require_POST
def renovar_licencia_view(request):
    """Renueva la licencia con una nueva clave."""
    # Rate limiting
    if not _check_rate_limit(request):
        messages.error(request, "Demasiados intentos. Espere un momento e intente de nuevo.")
        return redirect("acerca_de")

    licencia_texto = request.POST.get("licencia", "").strip()

    if not licencia_texto:
        messages.error(request, "Ingrese la clave de licencia.")
        return redirect("acerca_de")

    exito, mensaje, licencia = activar_licencia(licencia_texto)

    if exito:
        messages.success(request, f"Licencia renovada: {mensaje}")
    else:
        messages.error(request, mensaje)

    return redirect("acerca_de")
