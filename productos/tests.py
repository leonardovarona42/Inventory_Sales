from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from inventario.models import MovimientoStock

from .models import Producto, Proveedor


class ProductoUpsertTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="1234", is_staff=True)
        self.client.login(username="admin", password="1234")
        self.proveedor = Proveedor.objects.create(nombre="Prov", contacto="x@test.com")

    def test_crear_producto_existente_suma_stock(self):
        Producto.objects.create(
            nombre="Azucar",
            unidad_medida="kg",
            stock_actual=Decimal("3.00"),
            stock_minimo=Decimal("1.00"),
            precio_costo=Decimal("2.00"),
            proveedor=self.proveedor,
        )
        self.client.post(
            reverse("producto_create"),
            {
                "nombre": "Azucar",
                "unidad_medida": "kg",
                "stock_actual": "2.00",
                "stock_minimo": "1.00",
                "precio_costo": "2.00",
                "proveedor": self.proveedor.id,
            },
        )
        producto = Producto.objects.get(nombre="Azucar")
        self.assertEqual(producto.stock_actual, Decimal("5.00"))
        self.assertTrue(MovimientoStock.objects.filter(producto=producto, tipo="entrada").exists())
