"""
Servicio de validación y activación de licencias.
"""
import logging
from datetime import datetime

from django.utils import timezone
from django.db import transaction
from django.db.utils import IntegrityError

from .models import Licencia
from .license_core import verificar_licencia as verificar_firma, hash_licencia, verificar_vencimiento

logger = logging.getLogger(__name__)


def obtener_licencia_activa() -> Licencia | None:
    """Retorna la licencia activa actual, o None si no existe."""
    return Licencia.objects.filter(activa=True).first()


def activar_licencia(licencia_texto: str) -> tuple[bool, str, Licencia | None]:
    """
    Activa una nueva licencia.
    Verificacion de seguridad:
    1. Firma HMAC
    2. Nonce unico (previene reuso)
    3. Vencimiento valido
    4. Hash unico (previene duplicados exactos)
    Retorna: (exito, mensaje, licencia)
    """
    # 1. Verificar firma HMAC
    payload = verificar_firma(licencia_texto)
    if payload is None:
        return False, "Licencia invalida - firma incorrecta", None

    # 2. Verificar que no esté ya usada (nonce único)
    nonce = payload.get("nonce")
    existente_nonce = Licencia.objects.filter(nonce=nonce).first()
    if existente_nonce:
        if existente_nonce.activa:
            return False, "Esta licencia ya esta activa", existente_nonce
        return False, "Esta licencia ya fue usada y desactivada anteriormente", None

    # 3. Verificar que el hash no exista (previene re-registro)
    lic_hash = hash_licencia(licencia_texto)
    if Licencia.objects.filter(clave_hash=lic_hash).exists():
        return False, "Esta licencia ya esta registrada en el sistema", None

    # 4. Verificar vencimiento
    es_valida, mensaje = verificar_vencimiento(payload)
    if not es_valida:
        return False, mensaje, None

    # 5. Desactivar licencia anterior si existe
    with transaction.atomic():
        anterior = obtener_licencia_activa()
        if anterior:
            anterior.activa = False
            anterior.fecha_desactivacion = timezone.now()
            anterior.motivo_desactivacion = "Reemplazada por nueva licencia"
            anterior.save(update_fields=["activa", "fecha_desactivacion", "motivo_desactivacion", "actualizada_en"])
            logger.info("Licencia anterior desactivada: %s", anterior)

        # 6. Crear nueva licencia
        vencimiento_str = payload.get("vencimiento")
        fecha_vencimiento = None
        if vencimiento_str:
            fecha_vencimiento = datetime.fromisoformat(vencimiento_str)
            if fecha_vencimiento.tzinfo is None:
                from django.utils import timezone as tz
                fecha_vencimiento = tz.make_aware(fecha_vencimiento)

        try:
            licencia = Licencia.objects.create(
                cliente_nombre=payload["cliente"],
                emisor_nombre=payload["emisor"],
                emisor_ci=payload["ci"],
                tipo=payload["tipo"],
                nonce=nonce,
                clave_hash=lic_hash,
                fecha_activacion=timezone.now(),
                fecha_vencimiento=fecha_vencimiento,
                activa=True,
                ultima_verificacion=timezone.now(),
            )
        except IntegrityError as e:
            if "nonce" in str(e) or "clave_hash" in str(e):
                return False, "Esta licencia ya fue procesada", None
            raise

    logger.info("Nueva licencia activada: %s (%s)", licencia.cliente_nombre, licencia.tipo)
    return True, mensaje, licencia


def verificar_y_actualizar(licencia: Licencia = None) -> tuple[bool, str]:
    """
    Verifica el estado de una licencia activa.
    Detecta manipulación de reloj.
    Retorna: (es_valida, mensaje)
    """
    if licencia is None:
        licencia = obtener_licencia_activa()

    if licencia is None:
        return False, "No hay licencia activa"

    # Reconstruir payload mínimo para verificar vencimiento
    payload = {
        "tipo": licencia.tipo,
        "vencimiento": licencia.fecha_vencimiento.isoformat() if licencia.fecha_vencimiento else None,
    }

    es_valida, mensaje = verificar_vencimiento(payload, licencia.ultima_verificacion)

    # Actualizar última verificación
    licencia.ultima_verificacion = timezone.now()
    licencia.save(update_fields=["ultima_verificacion", "actualizada_en"])

    # Si venció, desactivar
    if not es_valida:
        licencia.activa = False
        licencia.fecha_desactivacion = timezone.now()
        licencia.motivo_desactivacion = "Licencia vencida"
        licencia.save(update_fields=["activa", "fecha_desactivacion", "motivo_desactivacion", "actualizada_en"])
        logger.warning("Licencia desactivada por vencimiento: %s", licencia)

    return es_valida, mensaje


def desactivar_licencia(motivo: str = "Desactivada manualmente") -> bool:
    """Desactiva la licencia activa actual."""
    licencia = obtener_licencia_activa()
    if not licencia:
        return False

    licencia.activa = False
    licencia.fecha_desactivacion = timezone.now()
    licencia.motivo_desactivacion = motivo
    licencia.save(update_fields=["activa", "fecha_desactivacion", "motivo_desactivacion", "actualizada_en"])
    logger.info("Licencia desactivada: %s - Motivo: %s", licencia, motivo)
    return True
