from .models import ConfiguracionSistema


def configuracion_sistema(request):
    """Hacer la configuracion del sistema disponible en todos los templates."""
    config = ConfiguracionSistema.cargar()
    return {
        'config': {
            'nombre_negocio': config.nombre_negocio,
            'rnc_negocio': config.rnc_negocio,
            'direccion': config.direccion,
            'telefono': config.telefono,
            'email': config.email,
            'simbolo_moneda': config.simbolo_moneda,
            'tasa_impuesto': config.tasa_impuesto,
            'mensaje_recibo_superior': config.mensaje_recibo_superior,
            'mensaje_recibo_inferior': config.mensaje_recibo_inferior,
            'pie_pagina': config.pie_pagina,
            'logo_url': config.logo.url if config.logo else None,
        },
    }
