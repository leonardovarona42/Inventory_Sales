from django.db import models


class Licencia(models.Model):
    """
    Almacena las licencias activas e historial.
    NUNCA se guarda la licencia en texto plano, solo su hash.
    """
    TIPO_CHOICES = [
        ("trimestral", "Trimestral (90 días)"),
        ("semestral", "Semestral (180 días)"),
        ("perpetua", "Perpetua"),
    ]

    cliente_nombre = models.CharField(max_length=200)
    cliente_contacto = models.CharField(max_length=150, blank=True)

    # Hash SHA256 de la licencia completa, nunca texto plano
    clave_hash = models.CharField(max_length=64, unique=True, db_index=True)

    # Datos extraídos del payload
    emisor_nombre = models.CharField(max_length=150)
    emisor_ci = models.CharField(max_length=20)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    nonce = models.CharField(max_length=36, unique=True, db_index=True)

    fecha_activacion = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)

    activa = models.BooleanField(default=False, db_index=True)
    fecha_desactivacion = models.DateTimeField(null=True, blank=True)
    motivo_desactivacion = models.CharField(max_length=200, blank=True)

    # Protección anti-reloj
    ultima_verificacion = models.DateTimeField(null=True, blank=True)

    # Auditoría
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creada_en"]
        verbose_name = "Licencia"
        verbose_name_plural = "Licencias"

    def __str__(self):
        estado = "ACTIVA" if self.activa else "INACTIVA"
        return f"{self.cliente_nombre} - {self.tipo} [{estado}]"
