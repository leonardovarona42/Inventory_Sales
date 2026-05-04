"""
Núcleo de validación de licencias para InventorySales.
Comparte el mismo algoritmo de verificación con KeyManagement.
"""
import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone as dt_timezone

from django.conf import settings

TIPOS_LICENCIA = {
    "trimestral": ("Trimestral (90 días)", 90),
    "semestral": ("Semestral (180 días)", 180),
    "perpetua": ("Perpetua", None),
}


def get_license_secret() -> str:
    secret = getattr(settings, "LICENSE_SECRET", None)
    if not secret:
        raise RuntimeError("LICENSE_SECRET no configurada en settings.py")
    return secret


def verificar_licencia(licencia_texto: str) -> dict | None:
    """
    Verifica la firma HMAC de una licencia.
    Retorna el payload si es válida, None si es inválida.
    """
    try:
        if not licencia_texto.startswith("LIC-"):
            return None

        encoded = licencia_texto[4:]
        data = json.loads(base64.urlsafe_b64decode(encoded))

        payload_json = data["p"]
        firma_provided = data["s"]

        secret = get_license_secret()
        firma_calculada = hmac.new(
            secret.encode("utf-8"),
            payload_json.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(firma_provided, firma_calculada):
            return None

        return json.loads(payload_json)

    except Exception:
        return None


def hash_licencia(licencia_texto: str) -> str:
    """Genera un hash SHA256 de la licencia para almacenamiento seguro."""
    return hashlib.sha256(licencia_texto.encode("utf-8")).hexdigest()


def verificar_vencimiento(payload: dict, ultima_verificacion: datetime = None) -> tuple[bool, str]:
    """
    Verifica si una licencia está vigente.
    Usa ultima_verificacion para detectar manipulación del reloj.
    Retorna: (es_valida, mensaje)
    """
    if payload.get("tipo") == "perpetua":
        return True, "Licencia perpetua activa"

    vencimiento_str = payload.get("vencimiento")
    if not vencimiento_str:
        return False, "Licencia sin fecha de vencimiento"

    vencimiento = datetime.fromisoformat(vencimiento_str)
    ahora = datetime.now(dt_timezone.utc)

    # Detectar manipulación de reloj
    if ultima_verificacion:
        if ultima_verificacion.tzinfo is None:
            from django.utils import timezone as django_tz
            ultima_verificacion = django_tz.make_aware(ultima_verificacion)

        if ahora < ultima_verificacion:
            # El reloj retrocedió
            ahora_efectivo = ultima_verificacion
        else:
            ahora_efectivo = ahora
    else:
        ahora_efectivo = ahora

    if ahora_efectivo > vencimiento:
        return False, f"Licencia vencida el {vencimiento.strftime('%Y-%m-%d %H:%M')}"

    dias_restantes = (vencimiento - ahora_efectivo).days
    if dias_restantes <= 30:
        return True, f"Licencia vigente - vence en {dias_restantes} días"

    return True, "Licencia vigente"
