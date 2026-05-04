from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from .models import Licencia


class EstadoLicenciaFilter(SimpleListFilter):
    title = "Estado"
    parameter_name = "estado"

    def lookups(self, request, model_admin):
        return (
            ("activa", "Activa"),
            ("vencida", "Vencida"),
            ("revocada", "Revocada"),
            ("perpetua", "Perpetua"),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        now = timezone.now()
        if self.value() == "activa":
            return queryset.filter(activa=True, fecha_vencimiento__gt=now)
        if self.value() == "vencida":
            return queryset.filter(activa=False, fecha_vencimiento__lt=now,
                                   fecha_desactivacion__isnull=False,
                                   motivo_desactivacion="Licencia vencida")
        if self.value() == "revocada":
            return queryset.filter(activa=False, fecha_desactivacion__isnull=False).exclude(motivo_desactivacion="Licencia vencida")
        if self.value() == "perpetua":
            return queryset.filter(tipo="perpetua", activa=True)


@admin.register(Licencia)
class LicenciaAdmin(admin.ModelAdmin):
    list_display = ["cliente_nombre", "tipo", "estado_display", "fecha_vencimiento", "creada_en"]
    list_filter = [EstadoLicenciaFilter, "tipo"]
    search_fields = ["cliente_nombre", "emisor_nombre", "emisor_ci", "nonce"]
    date_hierarchy = "creada_en"

    # TODOS los campos son de solo lectura - nadie puede modificar la licencia via admin
    readonly_fields = [
        "cliente_nombre", "cliente_contacto",
        "clave_hash", "nonce", "tipo",
        "emisor_nombre", "emisor_ci",
        "activa", "fecha_activacion", "fecha_vencimiento",
        "fecha_desactivacion", "motivo_desactivacion",
        "ultima_verificacion", "creada_en", "actualizada_en",
    ]

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

    # Deshabilitar agregar, editar y eliminar desde admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def estado_display(self, obj):
        from django.utils import timezone
        if obj.activa:
            if obj.fecha_vencimiento and obj.fecha_vencimiento < timezone.now():
                return "VENCIDA"
            if obj.tipo == "perpetua":
                return "PERPETUA"
            return "ACTIVA"
        if obj.motivo_desactivacion == "Licencia vencida":
            return "VENCIDA"
        return "REVOCADA"
    estado_display.short_description = "Estado"
