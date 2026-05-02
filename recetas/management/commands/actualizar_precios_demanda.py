from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from recetas.models import ProductoFinal, HistorialPrecioProducto
from ventas.models import DetalleVenta
from django.db.models import Sum


class Command(BaseCommand):
    help = 'Actualiza los precios de productos finales según la demanda de las últimas 24 horas'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando actualización de precios dinámicos...')
        
        ahora = timezone.now()
        hace_24h = ahora - timedelta(hours=24)
        
        productos = ProductoFinal.objects.all()
        actualizados = 0
        sin_cambios = 0
        
        for producto in productos:
            # Contar ventas en las últimas 24 horas
            ventas_24h = DetalleVenta.objects.filter(
                id_producto_final=producto,
                venta__fecha_venta__gte=hace_24h
            ).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
            
            precio_anterior = producto.precio_actual
            
            # Aplicar lógica de precio dinámico
            if ventas_24h >= producto.umbral_demanda_alta:
                nuevo_precio = producto.precio_base + producto.incremento_por_demanda
            else:
                nuevo_precio = producto.precio_base
            
            # Guardar cambio si el precio varió
            if nuevo_precio != precio_anterior:
                producto.precio_actual = nuevo_precio
                producto.save()
                
                # Registrar en historial
                HistorialPrecioProducto.objects.create(
                    producto=producto,
                    precio_anterior=precio_anterior,
                    precio_nuevo=nuevo_precio,
                    razon='demanda' if ventas_24h >= producto.umbral_demanda_alta else 'manual'
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ {producto.nombre}: ${precio_anterior} → ${nuevo_precio} '
                        f'(ventas 24h: {ventas_24h})'
                    )
                )
                actualizados += 1
            else:
                sin_cambios += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Actualización completada: {actualizados} productos modificados, '
                f'{sin_cambios} sin cambios'
            )
        )
