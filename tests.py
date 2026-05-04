import pytest
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from productos.models import Producto, Categoria, Proveedor
from ventas.models import Venta

@pytest.mark.django_db
def test_crear_producto():
    """Prueba básica para crear un producto"""
    cat = Categoria.objects.create(nombre='Test Cat')
    prov = Proveedor.objects.create(nombre='Test Prov')
    prod = Producto.objects.create(
        nombre='Producto Test',
        stock_actual=10,
        stock_minimo=5,
        precio_costo=10.00,
        precio_venta=15.00,
        proveedor=prov
    )
    prod.categorias.add(cat)
    assert prod.nombre == 'Producto Test'
    assert prod.stock_actual == 10
    assert prod.precio_venta == 15.00


@pytest.mark.django_db
def test_crear_venta():
    """Prueba básica para crear una venta"""
    user = User.objects.create_user(username='testuser', password='testpass123')
    cat = Categoria.objects.create(nombre='Test Cat')
    prov = Proveedor.objects.create(nombre='Test Prov')
    prod = Producto.objects.create(
        nombre='Producto Test',
        stock_actual=10,
        stock_minimo=5,
        precio_costo=10.00,
        precio_venta=15.00,
        proveedor=prov
    )
    prod.categorias.add(cat)
    
    venta = Venta.objects.create(
        cajero='testuser',
        cajero_user=user,
        metodo_pago='efectivo',
        total_pagado=15.00
    )
    assert venta.total_pagado == 15.00
    assert venta.metodo_pago == 'efectivo'


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        # Create user with superuser permissions to bypass all checks
        self.user = User.objects.create_superuser(
            username='testadmin', 
            email='test@test.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        self.cat = Categoria.objects.create(nombre='Test Cat')
        self.prov = Proveedor.objects.create(nombre='Test Prov')
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            stock_actual=10,
            stock_minimo=5,
            precio_costo=10.00,
            precio_venta=15.00,
            proveedor=self.prov
        )
        self.producto.categorias.add(self.cat)
    
    def test_producto_list_view(self):
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, 200)
    
    def test_producto_create_view(self):
        response = self.client.get('/products/create/')
        self.assertEqual(response.status_code, 200)
    
    def test_pos_view(self):
        response = self.client.get('/sales/pos/')
        self.assertEqual(response.status_code, 200)
    
    def test_producto_create_view(self):
        response = self.client.get('/products/create/')
        print(f"Create Status: {response.status_code}")
        self.assertEqual(response.status_code, 200)

    
    def test_producto_create_view(self):
        response = self.client.get('/productos/create/')
        self.assertEqual(response.status_code, 200)
    
    def test_pos_view(self):
        response = self.client.get('/pos/')
        self.assertEqual(response.status_code, 200)
