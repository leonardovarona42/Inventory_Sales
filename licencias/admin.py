from django.contrib import admin
from .models import Licencia


@admin.register(Licencia)
class LicenciaAdmin(admin.ModelAdmin):
    list_display = ["cliente_nombre", "tipo", "activa", "fecha_vencimiento", "creada_en"]
    list_filter = ["activa", "tipo"]
    search_fields = ["cliente_nombre", "emisor_nombre", "emisor_ci", "nonce"]
    readonly_fields = ["clave_hash", "nonce", "creada_en", "actualizada_en"]
    date_hierarchy = "creada_en"

    fieldsets = (
        ("Cliente", {
            "fields": ("cliente_nombre", "cliente_contacto")
        }),
        ("Emisor", {
            "fields": ("emisor_nombre", "emisor_ci")
        }),
        ("Licencia", {
            "fields": ("clave_hash", "nonce", "tipo", "fecha_activacion", "fecha_vencimiento")
        }),
        ("Estado", {
            "fields": ("activa", "fecha_desactivacion", "motivo_desactivacion")
        }),
        ("Auditoria", {
            "fields": ("ultima_verificacion", "creada_en", "actualizada_en"),
            "classes": ("collapse",)
        }),
    )
