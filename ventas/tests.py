from django.test import TestCase
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile

from inventario.models import MovimientoStock
from ordenes.models import Orden
from productos.models import Producto, Proveedor
from recetas.models import ProductoFinal, Receta, DetalleReceta
from .services import procesar_venta


class ProcesarVentaServiceTests(TestCase):
    def setUp(self):
        self.proveedor = Proveedor.objects.create(nombre="Proveedor 1", contacto="proveedor@test.com")
        self.insumo = Producto.objects.create(
            nombre="Harina",
            unidad_medida="kg",
            stock_actual=Decimal("10.00"),
            stock_minimo=Decimal("2.00"),
            precio_costo=Decimal("4.00"),
            proveedor=self.proveedor,
        )
        self.producto_final = ProductoFinal.objects.create(
            nombre="Pizza",
            descripcion="Pizza familiar",
            precio_base=Decimal("20.00"),
            precio_actual=Decimal("20.00"),
            umbral_demanda_alta=5,
            incremento_por_demanda=Decimal("2.00"),
            imagen=SimpleUploadedFile("pizza.jpg", b"img", content_type="image/jpeg"),
        )
        receta = Receta.objects.create(producto_final=self.producto_final)
        DetalleReceta.objects.create(
            receta=receta,
            producto=self.insumo,
            cantidad_necesaria=Decimal("1.00"),
        )

    def test_procesar_venta_descuenta_stock_y_crea_movimiento(self):
        orden = Orden.objects.create(cliente_nombre="Cliente test")
        venta = procesar_venta(
            orden=orden,
            metodo_pago="efectivo",
            items=[{"producto_final": self.producto_final, "cantidad": 2}],
        )

        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.stock_actual, Decimal("8.00"))
        self.assertEqual(venta.total_pagado, Decimal("40.00"))
        self.assertEqual(MovimientoStock.objects.filter(motivo="venta").count(), 1)
