from django.test import TestCase
from django.contrib.auth.models import User, Group
from decimal import Decimal
from productos.models import Producto, Categoria, Proveedor
from ventas.models import Venta, DetalleVenta
from ventas.services import procesar_venta, cancelar_venta


class VentaServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cajero', password='test123')
        Group.objects.create(name='Cajero')
        self.categoria = Categoria.objects.create(nombre='Alimentos')
        self.proveedor = Proveedor.objects.create(nombre='Test', contacto='555-0000')
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            stock_actual=Decimal('100'),
            stock_minimo=Decimal('10'),
            precio_costo=Decimal('5.00'),
            precio_venta=Decimal('10.00'),
            proveedor=self.proveedor,
        )
        self.producto.categorias.add(self.categoria)

    def test_procesar_venta_exitosa(self):
        venta = procesar_venta(
            metodo_pago='efectivo',
            items=[{'producto': self.producto, 'cantidad': 2}],
            cajero='cajero'
        )
        self.assertIsNotNone(venta.id)
        self.assertEqual(venta.detalles.count(), 1)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal('98'))

    def test_procesar_venta_sin_stock(self):
        self.producto.stock_actual = Decimal('1')
        self.producto.save()
        with self.assertRaises(Exception):
            procesar_venta(
                metodo_pago='efectivo',
                items=[{'producto': self.producto, 'cantidad': 5}],
                cajero='cajero'
            )

    def test_cancelar_venta_revierte_stock(self):
        venta = procesar_venta(
            metodo_pago='efectivo',
            items=[{'producto': self.producto, 'cantidad': 3}],
            cajero='cajero'
        )
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal('97'))

        cancelar_venta(venta_id=venta.id)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, Decimal('100'))

    def test_total_venta_correcto(self):
        venta = procesar_venta(
            metodo_pago='tarjeta',
            items=[{'producto': self.producto, 'cantidad': 5}],
            cajero='cajero'
        )
        self.assertEqual(venta.total_pagado, Decimal('50.00'))
