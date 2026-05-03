from django.test import TestCase
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Group, User
from django.urls import reverse

from inventario.models import MovimientoStock
from productos.models import Producto, Proveedor
from recetas.models import Receta, DetalleReceta
from .services import procesar_venta


class ProcesarVentaServiceTests(TestCase):
    def setUp(self):
        self.proveedor = Proveedor.objects.create(nombre="Proveedor 1", contacto="proveedor@test.com")
        self.insumo = Producto.objects.create(
            nombre="Harina",
            tipo_producto='insumo',
            unidad_medida="kg",
            stock_actual=Decimal("10.00"),
            stock_minimo=Decimal("2.00"),
            precio_costo=Decimal("4.00"),
            proveedor=self.proveedor,
        )
        self.producto_final = Producto.objects.create(
            nombre="Pizza",
            tipo_producto='final',
            descripcion="Pizza familiar",
            precio_base=Decimal("20.00"),
            precio_actual=Decimal("20.00"),
            umbral_demanda_alta=5,
            incremento_por_demanda=Decimal("2.00"),
        )
        receta = Receta.objects.create(producto_final=self.producto_final)
        DetalleReceta.objects.create(
            receta=receta,
            producto=self.insumo,
            cantidad_necesaria=Decimal("1.00"),
        )

    def test_procesar_venta_descuenta_stock_y_crea_movimiento(self):
        venta = procesar_venta(
            metodo_pago="efectivo",
            cajero="caja1",
            items=[{"producto_final": self.producto_final, "cantidad": 2}],
        )

        self.insumo.refresh_from_db()
        self.assertEqual(self.insumo.stock_actual, Decimal("8.00"))
        self.assertEqual(venta.total_pagado, Decimal("40.00"))
        self.assertTrue(venta.codigo_ticket.startswith("V-"))
        self.assertEqual(MovimientoStock.objects.filter(motivo="venta").count(), 1)


class POSAjaxTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cajero", password="1234")
        self.group = Group.objects.create(name="Cajero")
        self.user.groups.add(self.group)
        self.client.login(username="cajero", password="1234")

        proveedor = Proveedor.objects.create(nombre="Proveedor", contacto="a@a.com")
        producto = Producto.objects.create(
            nombre="Queso",
            tipo_producto='insumo',
            unidad_medida="kg",
            stock_actual=Decimal("5.00"),
            stock_minimo=Decimal("1.00"),
            precio_costo=Decimal("2.00"),
            proveedor=proveedor,
        )
        self.producto_final = Producto.objects.create(
            nombre="Arepa",
            tipo_producto='final',
            descripcion="Arepa simple",
            precio_base=Decimal("3.00"),
            precio_actual=Decimal("3.00"),
        )
        receta = Receta.objects.create(producto_final=self.producto_final)
        DetalleReceta.objects.create(receta=receta, producto=producto, cantidad_necesaria=Decimal("1.00"))

    def test_confirmar_venta_vacia_carrito(self):
        self.client.post(reverse("ajax_agregar_carrito"), {"producto_id": self.producto_final.id, "cantidad": 1}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        response = self.client.post(reverse("ajax_procesar_venta"), {"metodo_pago": "efectivo"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)
        self.assertEqual(self.client.session.get("carrito"), {})
