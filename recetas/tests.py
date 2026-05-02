from django.test import TestCase
from decimal import Decimal
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from ordenes.models import Orden
from productos.models import Producto, Proveedor
from ventas.models import Venta, DetalleVenta
from .models import ProductoFinal, Receta, DetalleReceta


class PrecioDinamicoTests(TestCase):
    def test_calcular_precio_dinamico_aplica_incremento_por_demanda(self):
        producto = ProductoFinal.objects.create(
            nombre="Hamburguesa",
            descripcion="Clasica",
            precio_base=Decimal("10.00"),
            precio_actual=Decimal("10.00"),
            umbral_demanda_alta=3,
            incremento_por_demanda=Decimal("1.50"),
            imagen=SimpleUploadedFile("burger.jpg", b"img", content_type="image/jpeg"),
        )
        proveedor = Proveedor.objects.create(nombre="Proveedor", contacto="test@test.com")
        insumo = Producto.objects.create(
            nombre="Carne",
            unidad_medida="kg",
            stock_actual=Decimal("20.00"),
            stock_minimo=Decimal("2.00"),
            precio_costo=Decimal("5.00"),
            proveedor=proveedor,
        )
        receta = Receta.objects.create(producto_final=producto)
        DetalleReceta.objects.create(receta=receta, producto=insumo, cantidad_necesaria=Decimal("1.00"))
        venta = Venta.objects.create(
            orden=Orden.objects.create(cliente_nombre="Cliente"),
            metodo_pago="efectivo",
            total_pagado=Decimal("30.00"),
        )
        DetalleVenta.objects.create(
            venta=venta,
            id_producto_final=producto,
            cantidad=3,
            precio_unitario=Decimal("10.00"),
        )

        # Forzar ventana de 24h para la prueba
        Venta.objects.filter(pk=venta.pk).update(fecha_venta=timezone.now() - timedelta(hours=1))
        producto.calcular_precio_dinamico()
        producto.refresh_from_db()

        self.assertEqual(producto.precio_actual, Decimal("11.50"))
