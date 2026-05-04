"""
Script para poblar categorias y productos de ejemplo.
Uso: python populate_categories.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventory_Sales.settings')
django.setup()

from decimal import Decimal
from productos.models import Categoria, Proveedor, Producto


def run():
    print('Creando categorias...')

    # Categorias principales
    cats = {
        'Aseo': {'icono': 'fa-soap', 'color': '#06b6d4'},
        'Alimentos': {'icono': 'fa-utensils', 'color': '#f97316'},
        'Utiles': {'icono': 'fa-pen-ruler', 'color': '#8b5cf6'},
        'Herramientas': {'icono': 'fa-screwdriver-wrench', 'color': '#64748b'},
    }

    categorias = {}
    for nombre, datos in cats.items():
        cat, created = Categoria.objects.get_or_create(
            nombre=nombre,
            defaults={'icono': datos['icono'], 'color': datos['color'], 'orden': list(cats.keys()).index(nombre)}
        )
        categorias[nombre] = cat
        if created:
            print(f'  + Categoria: {nombre}')

    # Subcategorias
    subcats = {
        'Productos Terminados': {'padre': 'Alimentos', 'icono': 'fa-burger', 'color': '#ea580c'},
    }

    subcategorias = {}
    for nombre, datos in subcats.items():
        cat, created = Categoria.objects.get_or_create(
            nombre=nombre,
            defaults={'padre': categorias[datos['padre']], 'icono': datos['icono'], 'color': datos['color']}
        )
        subcategorias[nombre] = cat
        if created:
            print(f'  + Subcategoria: {cat}')

    # Proveedor de ejemplo
    proveedor, _ = Proveedor.objects.get_or_create(
        nombre='Proveedor Principal',
        defaults={'contacto': '555-0100'}
    )

    # Productos de ejemplo por categoria
    productos = [
        # Alimentos - Productos Terminados
        {'nombre': 'Hamburguesa Clasica', 'descripcion': 'Pan, carne 150g, lechuga, tomate, queso', 'categoria': 'Productos Terminados', 'precio_venta': 5.50, 'precio_costo': 2.50, 'stock': 50, 'unidad': 'unidad'},
        {'nombre': 'Hamburguesa Doble', 'descripcion': 'Pan, doble carne 150g, lechuga, tomate, queso, bacon', 'categoria': 'Productos Terminados', 'precio_venta': 8.00, 'precio_costo': 4.00, 'stock': 30, 'unidad': 'unidad'},
        {'nombre': 'Hot Dog', 'descripcion': 'Pan, salchicha, mostaza, ketchup, cebolla', 'categoria': 'Productos Terminados', 'precio_venta': 3.00, 'precio_costo': 1.20, 'stock': 80, 'unidad': 'unidad'},
        {'nombre': 'Papas Fritas', 'descripcion': 'Porcion individual de papas fritas', 'categoria': 'Productos Terminados', 'precio_venta': 2.50, 'precio_costo': 0.80, 'stock': 100, 'unidad': 'unidad'},
        {'nombre': 'Refresco 500ml', 'descripcion': 'Bebida gaseosa de 500ml', 'categoria': 'Productos Terminados', 'precio_venta': 1.50, 'precio_costo': 0.60, 'stock': 200, 'unidad': 'unidad'},

        # Alimentos (general)
        {'nombre': 'Pan de Hamburguesa', 'descripcion': 'Paquete de 6 panes', 'categoria': 'Alimentos', 'precio_venta': 3.00, 'precio_costo': 1.50, 'stock': 40, 'unidad': 'paquete'},
        {'nombre': 'Carne Molida kg', 'descripcion': 'Carne molida de res por kilogramo', 'categoria': 'Alimentos', 'precio_venta': 8.00, 'precio_costo': 5.00, 'stock': 20, 'unidad': 'kg'},
        {'nombre': 'Queso Amarillo', 'descripcion': 'Rebanadas de queso amarillo', 'categoria': 'Alimentos', 'precio_venta': 4.00, 'precio_costo': 2.00, 'stock': 30, 'unidad': 'paquete'},
        {'nombre': 'Lechuga', 'descripcion': 'Lechuga fresca por unidad', 'categoria': 'Alimentos', 'precio_venta': 1.00, 'precio_costo': 0.50, 'stock': 50, 'unidad': 'unidad'},
        {'nombre': 'Tomate kg', 'descripcion': 'Tomates frescos por kilogramo', 'categoria': 'Alimentos', 'precio_venta': 2.50, 'precio_costo': 1.20, 'stock': 15, 'unidad': 'kg'},

        # Aseo
        {'nombre': 'Jabon Liquido 500ml', 'descripcion': 'Jabon liquido antibacterial', 'categoria': 'Aseo', 'precio_venta': 3.50, 'precio_costo': 1.80, 'stock': 25, 'unidad': 'unidad'},
        {'nombre': 'Desinfectante 1L', 'descripcion': 'Desinfectante multiusos', 'categoria': 'Aseo', 'precio_venta': 4.00, 'precio_costo': 2.00, 'stock': 20, 'unidad': 'unidad'},
        {'nombre': 'Papel Toalla', 'descripcion': 'Rollo de papel toalla industrial', 'categoria': 'Aseo', 'precio_venta': 2.00, 'precio_costo': 0.80, 'stock': 50, 'unidad': 'unidad'},
        {'nombre': 'Bolsas de Basura', 'descripcion': 'Paquete de 20 bolsas negras', 'categoria': 'Aseo', 'precio_venta': 3.00, 'precio_costo': 1.20, 'stock': 30, 'unidad': 'paquete'},

        # Utiles
        {'nombre': 'Cuaderno Universitario', 'descripcion': 'Cuaderno 100 hojas cuadriculado', 'categoria': 'Utiles', 'precio_venta': 2.50, 'precio_costo': 1.00, 'stock': 60, 'unidad': 'unidad'},
        {'nombre': 'Boli Azul', 'descripcion': 'Boligrafo de tinta azul', 'categoria': 'Utiles', 'precio_venta': 0.50, 'precio_costo': 0.15, 'stock': 200, 'unidad': 'unidad'},
        {'nombre': 'Carpeta Manila', 'descripcion': 'Carpeta manila tamaño carta', 'categoria': 'Utiles', 'precio_venta': 0.30, 'precio_costo': 0.10, 'stock': 150, 'unidad': 'unidad'},
        {'nombre': 'Resma de Papel', 'descripcion': 'Resma papel blanco carta 500 hojas', 'categoria': 'Utiles', 'precio_venta': 5.00, 'precio_costo': 3.00, 'stock': 20, 'unidad': 'paquete'},

        # Herramientas
        {'nombre': 'Martillo', 'descripcion': 'Martillo de acero con mango de madera', 'categoria': 'Herramientas', 'precio_venta': 12.00, 'precio_costo': 6.00, 'stock': 10, 'unidad': 'unidad'},
        {'nombre': 'Destornillador Phillips', 'descripcion': 'Destornillador estrella punta Phillips', 'categoria': 'Herramientas', 'precio_venta': 5.00, 'precio_costo': 2.00, 'stock': 15, 'unidad': 'unidad'},
        {'nombre': 'Cinta Metrica 5m', 'descripcion': 'Cinta metrica de 5 metros', 'categoria': 'Herramientas', 'precio_venta': 4.00, 'precio_costo': 1.50, 'stock': 12, 'unidad': 'unidad'},
        {'nombre': 'Alicate Universal', 'descripcion': 'Alicate universal 8 pulgadas', 'categoria': 'Herramientas', 'precio_venta': 8.00, 'precio_costo': 3.50, 'stock': 8, 'unidad': 'unidad'},
    ]

    print('\nCreando productos...')
    for p in productos:
        cat_name = p.pop('categoria')
        precio_venta = p.pop('precio_venta')
        precio_costo = p.pop('precio_costo')
        stock = p.pop('stock')
        unidad = p.pop('unidad')
        
        cat = categorias.get(cat_name) or subcategorias.get(cat_name)
        if not cat:
            print(f'  ! Categoria no encontrada: {cat_name}')
            continue

        prod, created = Producto.objects.get_or_create(
            nombre=p['nombre'],
            defaults={
                'descripcion': p.get('descripcion', ''),
                'unidad_medida': unidad,
                'stock_actual': Decimal(str(stock)),
                'stock_minimo': Decimal(str(max(5, stock // 4))),
                'precio_costo': Decimal(str(precio_costo)),
                'precio_venta': Decimal(str(precio_venta)),
                'proveedor': proveedor,
            }
        )
        prod.categorias.add(cat)
        if created:
            print(f'  + {prod.nombre} -> {cat} (${precio_venta})')
        else:
            print(f'  ~ {prod.nombre} (ya existe)')

    print(f'\nTotal categorias: {Categoria.objects.count()}')
    print(f'Total productos: {Producto.objects.count()}')
    print('Listo!')


if __name__ == '__main__':
    run()
