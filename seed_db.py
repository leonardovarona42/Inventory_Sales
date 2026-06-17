import os
import sys
import requests
from decimal import Decimal

MEDIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'productos')
os.makedirs(MEDIA_DIR, exist_ok=True)

PRODUCT_IMAGES = {
    'default': 'https://picsum.photos/seed/default/400/400',
    'Hamburguesa Clasica': 'https://picsum.photos/seed/burger1/400/400',
    'Hamburguesa Doble': 'https://picsum.photos/seed/burger2/400/400',
    'Hot Dog': 'https://picsum.photos/seed/hotdog/400/400',
    'Papas Fritas': 'https://picsum.photos/seed/fries/400/400',
    'Refresco 500ml': 'https://picsum.photos/seed/soda/400/400',
    'Pan de Hamburguesa': 'https://picsum.photos/seed/bun/400/400',
    'Carne Molida kg': 'https://picsum.photos/seed/meat/400/400',
    'Queso Amarillo': 'https://picsum.photos/seed/cheese/400/400',
    'Lechuga': 'https://picsum.photos/seed/lettuce/400/400',
    'Tomate kg': 'https://picsum.photos/seed/tomato/400/400',
    'Jabon Liquido 500ml': 'https://picsum.photos/seed/soap/400/400',
    'Desinfectante 1L': 'https://picsum.photos/seed/disinfectant/400/400',
    'Papel Toalla': 'https://picsum.photos/seed/towel/400/400',
    'Bolsas de Basura': 'https://picsum.photos/seed/trash/400/400',
    'Cuaderno Universitario': 'https://picsum.photos/seed/notebook/400/400',
    'Boli Azul': 'https://picsum.photos/seed/pen/400/400',
    'Carpeta Manila': 'https://picsum.photos/seed/folder/400/400',
    'Resma de Papel': 'https://picsum.photos/seed/paper/400/400',
    'Martillo': 'https://picsum.photos/seed/hammer/400/400',
    'Destornillador Phillips': 'https://picsum.photos/seed/screwdriver/400/400',
    'Cinta Metrica 5m': 'https://picsum.photos/seed/tape/400/400',
    'Alicate Universal': 'https://picsum.photos/seed/pliers/400/400',
}


def download_image(url, name):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            ext = 'jpg'
            fname = f'{name.lower().replace(" ", "_")}.{ext}'
            path = os.path.join(MEDIA_DIR, fname)
            with open(path, 'wb') as f:
                f.write(r.content)
            print(f'  + Imagen: {fname}')
            return f'productos/{fname}'
    except Exception as e:
        print(f'  ! Error descargando {name}: {e}')
    return None


# Download ALL images BEFORE connecting to DB
print('=== DESCARGANDO IMAGENES ===')
product_images = {}
for pdata in [
    {'nombre': 'Hamburguesa Clasica'},
    {'nombre': 'Hamburguesa Doble'},
    {'nombre': 'Hot Dog'},
    {'nombre': 'Papas Fritas'},
    {'nombre': 'Refresco 500ml'},
    {'nombre': 'Pan de Hamburguesa'},
    {'nombre': 'Carne Molida kg'},
    {'nombre': 'Queso Amarillo'},
    {'nombre': 'Lechuga'},
    {'nombre': 'Tomate kg'},
    {'nombre': 'Jabon Liquido 500ml'},
    {'nombre': 'Desinfectante 1L'},
    {'nombre': 'Papel Toalla'},
    {'nombre': 'Bolsas de Basura'},
    {'nombre': 'Cuaderno Universitario'},
    {'nombre': 'Boli Azul'},
    {'nombre': 'Carpeta Manila'},
    {'nombre': 'Resma de Papel'},
    {'nombre': 'Martillo'},
    {'nombre': 'Destornillador Phillips'},
    {'nombre': 'Cinta Metrica 5m'},
    {'nombre': 'Alicate Universal'},
]:
    url = PRODUCT_IMAGES.get(pdata['nombre'], PRODUCT_IMAGES['default'])
    img_path = download_image(url, pdata['nombre'])
    product_images[pdata['nombre']] = img_path

print('Imagenes descargadas. Conectando a BD...\n')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventory_Sales.settings')
django.setup()

from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import close_old_connections
from productos.models import Categoria, Proveedor, Producto
from ventas.models import Cliente, Venta, DetalleVenta, ConfiguracionSistema
from inventario.models import MovimientoStock
from django.contrib.auth import get_user_model

User = get_user_model()

PRODUCT_IMAGES = {
    'default': 'https://picsum.photos/seed/default/400/400',
    'Hamburguesa Clasica': 'https://picsum.photos/seed/burger1/400/400',
    'Hamburguesa Doble': 'https://picsum.photos/seed/burger2/400/400',
    'Hot Dog': 'https://picsum.photos/seed/hotdog/400/400',
    'Papas Fritas': 'https://picsum.photos/seed/fries/400/400',
    'Refresco 500ml': 'https://picsum.photos/seed/soda/400/400',
    'Pan de Hamburguesa': 'https://picsum.photos/seed/bun/400/400',
    'Carne Molida kg': 'https://picsum.photos/seed/meat/400/400',
    'Queso Amarillo': 'https://picsum.photos/seed/cheese/400/400',
    'Lechuga': 'https://picsum.photos/seed/lettuce/400/400',
    'Tomate kg': 'https://picsum.photos/seed/tomato/400/400',
    'Jabon Liquido 500ml': 'https://picsum.photos/seed/soap/400/400',
    'Desinfectante 1L': 'https://picsum.photos/seed/disinfectant/400/400',
    'Papel Toalla': 'https://picsum.photos/seed/towel/400/400',
    'Bolsas de Basura': 'https://picsum.photos/seed/trash/400/400',
    'Cuaderno Universitario': 'https://picsum.photos/seed/notebook/400/400',
    'Boli Azul': 'https://picsum.photos/seed/pen/400/400',
    'Carpeta Manila': 'https://picsum.photos/seed/folder/400/400',
    'Resma de Papel': 'https://picsum.photos/seed/paper/400/400',
    'Martillo': 'https://picsum.photos/seed/hammer/400/400',
    'Destornillador Phillips': 'https://picsum.photos/seed/screwdriver/400/400',
    'Cinta Metrica 5m': 'https://picsum.photos/seed/tape/400/400',
    'Alicate Universal': 'https://picsum.photos/seed/pliers/400/400',
}


def download_image(url, name):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            ext = 'jpg'
            fname = f'{name.lower().replace(" ", "_")}.{ext}'
            path = os.path.join(MEDIA_DIR, fname)
            with open(path, 'wb') as f:
                f.write(r.content)
            print(f'  + Imagen: {fname}')
            return f'productos/{fname}'
    except Exception as e:
        print(f'  ! Error descargando {name}: {e}')
    return None


def run():
    close_old_connections()
    print('=== POBLANDO BASE DE DATOS ===\n')

    # 1. Configuracion del sistema
    cfg, created = ConfiguracionSistema.objects.get_or_create(pk=1, defaults={
        'nombre_negocio': 'Inventory Sales',
        'rnc_negocio': '123-456789-0',
        'direccion': 'Calle Principal #42, Santo Domingo',
        'telefono': '809-555-0100',
        'email': 'info@inventorysales.com',
        'simbolo_moneda': 'RD$',
        'tasa_impuesto': Decimal('18.00'),
        'pie_pagina': 'Gracias por su compra',
    })
    if created:
        print('+ Configuracion del sistema creada')

    # 2. Categorias principales
    cats_data = {
        'Aseo': {'icono': 'fa-soap', 'color': '#06b6d4', 'orden': 0},
        'Alimentos': {'icono': 'fa-utensils', 'color': '#f97316', 'orden': 1},
        'Utiles': {'icono': 'fa-pen-ruler', 'color': '#8b5cf6', 'orden': 2},
        'Herramientas': {'icono': 'fa-screwdriver-wrench', 'color': '#64748b', 'orden': 3},
    }

    categorias = {}
    for nombre, datos in cats_data.items():
        cat, created = Categoria.objects.get_or_create(
            nombre=nombre,
            defaults={
                'icono': datos['icono'],
                'color': datos['color'],
                'orden': datos['orden'],
            }
        )
        categorias[nombre] = cat
        print(f'{ "+" if created else "~"} Categoria: {nombre}')

    # 3. Subcategorias
    subcats_data = {
        'Productos Terminados': {'padre': 'Alimentos', 'icono': 'fa-burger', 'color': '#ea580c'},
        'Limpieza': {'padre': 'Aseo', 'icono': 'fa-broom', 'color': '#0891b2'},
    }

    subcategorias = {}
    for nombre, datos in subcats_data.items():
        cat, created = Categoria.objects.get_or_create(
            nombre=nombre,
            defaults={
                'padre': categorias[datos['padre']],
                'icono': datos['icono'],
                'color': datos['color'],
            }
        )
        subcategorias[nombre] = cat
        print(f'{ "+" if created else "~"} Subcategoria: {nombre}')

    # 4. Proveedores
    proveedores_data = [
        {'nombre': 'Distribuidora Alimenticia SRL', 'contacto': '809-555-0200'},
        {'nombre': 'Suministros de Oficina SA', 'contacto': '809-555-0300'},
        {'nombre': 'Ferreteria Industrial', 'contacto': '809-555-0400'},
        {'nombre': 'Productos de Limpieza Profesional', 'contacto': '809-555-0500'},
        {'nombre': 'Proveedor Principal', 'contacto': '555-0100'},
    ]

    proveedores = {}
    for pdata in proveedores_data:
        prov, created = Proveedor.objects.get_or_create(
            nombre=pdata['nombre'],
            defaults={'contacto': pdata['contacto']}
        )
        proveedores[prov.nombre] = prov
        print(f'{ "+" if created else "~"} Proveedor: {prov.nombre}')

    # 5. Productos
    productos_data = [
        # Alimentos - Productos Terminados
        {'nombre': 'Hamburguesa Clasica', 'descripcion': 'Pan, carne 150g, lechuga, tomate, queso', 'categoria': 'Productos Terminados', 'precio_venta': 5.50, 'precio_costo': 2.50, 'stock': 50, 'unidad': 'unidad', 'proveedor': 'Distribuidora Alimenticia SRL', 'codigo': 'ALI-001'},
        {'nombre': 'Hamburguesa Doble', 'descripcion': 'Pan, doble carne 150g, lechuga, tomate, queso, bacon', 'categoria': 'Productos Terminados', 'precio_venta': 8.00, 'precio_costo': 4.00, 'stock': 30, 'unidad': 'unidad', 'proveedor': 'Distribuidora Alimenticia SRL', 'codigo': 'ALI-002'},
        {'nombre': 'Hot Dog', 'descripcion': 'Pan, salchicha, mostaza, ketchup, cebolla', 'categoria': 'Productos Terminados', 'precio_venta': 3.00, 'precio_costo': 1.20, 'stock': 80, 'unidad': 'unidad', 'proveedor': 'Distribuidora Alimenticia SRL', 'codigo': 'ALI-003'},
        {'nombre': 'Papas Fritas', 'descripcion': 'Porcion individual de papas fritas', 'categoria': 'Productos Terminados', 'precio_venta': 2.50, 'precio_costo': 0.80, 'stock': 100, 'unidad': 'unidad', 'proveedor': 'Distribuidora Alimenticia SRL', 'codigo': 'ALI-004'},
        {'nombre': 'Refresco 500ml', 'descripcion': 'Bebida gaseosa de 500ml', 'categoria': 'Productos Terminados', 'precio_venta': 1.50, 'precio_costo': 0.60, 'stock': 200, 'unidad': 'unidad', 'proveedor': 'Distribuidora Alimenticia SRL', 'codigo': 'ALI-005'},

        # Alimentos (general)
        {'nombre': 'Pan de Hamburguesa', 'descripcion': 'Paquete de 6 panes', 'categoria': 'Alimentos', 'precio_venta': 3.00, 'precio_costo': 1.50, 'stock': 40, 'unidad': 'paquete', 'proveedor': 'Distribuidora Alimenticia SRL', 'codigo': 'ALI-006'},
        {'nombre': 'Carne Molida kg', 'descripcion': 'Carne molida de res por kilogramo', 'categoria': 'Alimentos', 'precio_venta': 8.00, 'precio_costo': 5.00, 'stock': 20, 'unidad': 'kg', 'proveedor': 'Distribuidora Alimenticia SRL', 'codigo': 'ALI-007'},
        {'nombre': 'Queso Amarillo', 'descripcion': 'Rebanadas de queso amarillo', 'categoria': 'Alimentos', 'precio_venta': 4.00, 'precio_costo': 2.00, 'stock': 30, 'unidad': 'paquete', 'proveedor': 'Distribuidora Alimenticia SRL', 'codigo': 'ALI-008'},
        {'nombre': 'Lechuga', 'descripcion': 'Lechuga fresca por unidad', 'categoria': 'Alimentos', 'precio_venta': 1.00, 'precio_costo': 0.50, 'stock': 50, 'unidad': 'unidad', 'proveedor': 'Distribuidora Alimenticia SRL', 'codigo': 'ALI-009'},
        {'nombre': 'Tomate kg', 'descripcion': 'Tomates frescos por kilogramo', 'categoria': 'Alimentos', 'precio_venta': 2.50, 'precio_costo': 1.20, 'stock': 15, 'unidad': 'kg', 'proveedor': 'Distribuidora Alimenticia SRL', 'codigo': 'ALI-010'},

        # Aseo
        {'nombre': 'Jabon Liquido 500ml', 'descripcion': 'Jabon liquido antibacterial', 'categoria': 'Limpieza', 'precio_venta': 3.50, 'precio_costo': 1.80, 'stock': 25, 'unidad': 'unidad', 'proveedor': 'Productos de Limpieza Profesional', 'codigo': 'ASE-001'},
        {'nombre': 'Desinfectante 1L', 'descripcion': 'Desinfectante multiusos', 'categoria': 'Limpieza', 'precio_venta': 4.00, 'precio_costo': 2.00, 'stock': 20, 'unidad': 'unidad', 'proveedor': 'Productos de Limpieza Profesional', 'codigo': 'ASE-002'},
        {'nombre': 'Papel Toalla', 'descripcion': 'Rollo de papel toalla industrial', 'categoria': 'Limpieza', 'precio_venta': 2.00, 'precio_costo': 0.80, 'stock': 50, 'unidad': 'unidad', 'proveedor': 'Productos de Limpieza Profesional', 'codigo': 'ASE-003'},
        {'nombre': 'Bolsas de Basura', 'descripcion': 'Paquete de 20 bolsas negras', 'categoria': 'Limpieza', 'precio_venta': 3.00, 'precio_costo': 1.20, 'stock': 30, 'unidad': 'paquete', 'proveedor': 'Productos de Limpieza Profesional', 'codigo': 'ASE-004'},

        # Utiles
        {'nombre': 'Cuaderno Universitario', 'descripcion': 'Cuaderno 100 hojas cuadriculado', 'categoria': 'Utiles', 'precio_venta': 2.50, 'precio_costo': 1.00, 'stock': 60, 'unidad': 'unidad', 'proveedor': 'Suministros de Oficina SA', 'codigo': 'UTL-001'},
        {'nombre': 'Boli Azul', 'descripcion': 'Boligrafo de tinta azul', 'categoria': 'Utiles', 'precio_venta': 0.50, 'precio_costo': 0.15, 'stock': 200, 'unidad': 'unidad', 'proveedor': 'Suministros de Oficina SA', 'codigo': 'UTL-002'},
        {'nombre': 'Carpeta Manila', 'descripcion': 'Carpeta manila tamaño carta', 'categoria': 'Utiles', 'precio_venta': 0.30, 'precio_costo': 0.10, 'stock': 150, 'unidad': 'unidad', 'proveedor': 'Suministros de Oficina SA', 'codigo': 'UTL-003'},
        {'nombre': 'Resma de Papel', 'descripcion': 'Resma papel blanco carta 500 hojas', 'categoria': 'Utiles', 'precio_venta': 5.00, 'precio_costo': 3.00, 'stock': 20, 'unidad': 'paquete', 'proveedor': 'Suministros de Oficina SA', 'codigo': 'UTL-004'},

        # Herramientas
        {'nombre': 'Martillo', 'descripcion': 'Martillo de acero con mango de madera', 'categoria': 'Herramientas', 'precio_venta': 12.00, 'precio_costo': 6.00, 'stock': 10, 'unidad': 'unidad', 'proveedor': 'Ferreteria Industrial', 'codigo': 'HRR-001'},
        {'nombre': 'Destornillador Phillips', 'descripcion': 'Destornillador estrella punta Phillips', 'categoria': 'Herramientas', 'precio_venta': 5.00, 'precio_costo': 2.00, 'stock': 15, 'unidad': 'unidad', 'proveedor': 'Ferreteria Industrial', 'codigo': 'HRR-002'},
        {'nombre': 'Cinta Metrica 5m', 'descripcion': 'Cinta metrica de 5 metros', 'categoria': 'Herramientas', 'precio_venta': 4.00, 'precio_costo': 1.50, 'stock': 12, 'unidad': 'unidad', 'proveedor': 'Ferreteria Industrial', 'codigo': 'HRR-003'},
        {'nombre': 'Alicate Universal', 'descripcion': 'Alicate universal 8 pulgadas', 'categoria': 'Herramientas', 'precio_venta': 8.00, 'precio_costo': 3.50, 'stock': 8, 'unidad': 'unidad', 'proveedor': 'Ferreteria Industrial', 'codigo': 'HRR-004'},
    ]

    close_old_connections()
    
    print('\nCreando productos...')
    cajero_user = User.objects.filter(is_superuser=True).first()

    for p in productos_data:
        cat_name = p.pop('categoria')
        precio_venta = p.pop('precio_venta')
        precio_costo = p.pop('precio_costo')
        stock = p.pop('stock')
        unidad = p.pop('unidad')
        prov_name = p.pop('proveedor')
        codigo = p.pop('codigo')
        img_path = p.pop('imagen_path', None)

        img_path = product_images.get(p['nombre'])

        cat = categorias.get(cat_name) or subcategorias.get(cat_name)
        if not cat:
            print(f'  ! Categoria no encontrada: {cat_name}')
            continue

        defaults = {
            'descripcion': p.get('descripcion', ''),
            'unidad_medida': unidad,
            'stock_actual': Decimal(str(stock)),
            'stock_minimo': Decimal(str(max(5, stock // 4))),
            'precio_costo': Decimal(str(precio_costo)),
            'precio_venta': Decimal(str(precio_venta)),
            'proveedor': proveedores.get(prov_name),
            'codigo_barras': codigo,
        }

        prod, created = Producto.objects.get_or_create(
            nombre=p['nombre'],
            defaults=defaults,
        )
        if created:
            if img_path:
                with open(os.path.join(MEDIA_DIR, os.path.basename(img_path)), 'rb') as f:
                    prod.imagen.save(os.path.basename(img_path), ContentFile(f.read()))
                prod.save()
            prod.categorias.add(cat)
            print(f'  + {prod.nombre} -> {cat} (${precio_venta})')
        else:
            for key, val in defaults.items():
                setattr(prod, key, val)
            if img_path and not prod.imagen:
                with open(os.path.join(MEDIA_DIR, os.path.basename(img_path)), 'rb') as f:
                    prod.imagen.save(os.path.basename(img_path), ContentFile(f.read()))
            prod.save()
            if not prod.categorias.filter(pk=cat.pk).exists():
                prod.categorias.add(cat)
            print(f'  ~ {prod.nombre} (actualizado)')

    # 6. Movimientos de stock inicial
    print('\nCreando movimientos de stock...')
    for p in productos_data:
        prod = Producto.objects.filter(nombre=p['nombre']).first()
        if prod:
            existing = MovimientoStock.objects.filter(
                producto=prod, tipo='entrada', motivo='compra'
            ).exists()
            if not existing:
                MovimientoStock.objects.create(
                    producto=prod,
                    tipo='entrada',
                    cantidad=prod.stock_actual,
                    motivo='compra',
                    notas='Stock inicial',
                )
                print(f'  + Movimiento: {prod.nombre} ({prod.stock_actual})')

    # 7. Clientes
    close_old_connections()
    clientes_data = [
        {'nombre': 'Juan Perez', 'telefono': '809-555-1001', 'email': 'juan@email.com', 'rnc': '001-0000001-0'},
        {'nombre': 'Maria Garcia', 'telefono': '809-555-1002', 'email': 'maria@email.com', 'rnc': '001-0000002-0'},
        {'nombre': 'Carlos Lopez', 'telefono': '809-555-1003', 'email': 'carlos@email.com', 'rnc': '001-0000003-0'},
        {'nombre': 'Ana Martinez', 'telefono': '809-555-1004', 'email': 'ana@email.com'},
        {'nombre': 'Pedro Rodriguez', 'telefono': '809-555-1005', 'email': 'pedro@email.com'},
    ]

    clientes = {}
    for cdata in clientes_data:
        cli, created = Cliente.objects.get_or_create(
            nombre=cdata['nombre'],
            defaults={
                'telefono': cdata.get('telefono', ''),
                'email': cdata.get('email', ''),
                'rnc': cdata.get('rnc', ''),
            }
        )
        clientes[cli.nombre] = cli
        print(f'{ "+" if created else "~"} Cliente: {cli.nombre}')

    # 8. Ventas de ejemplo
    if cajero_user:
        Venta.objects.filter(codigo_ticket__startswith='SEED-').delete()
        Venta.objects.filter(codigo_ticket='').delete()
        print('\nCreando ventas de ejemplo...')
        ventas_data = [
            {'cliente': 'Juan Perez', 'metodo': 'efectivo', 'items': [('Hamburguesa Clasica', 2), ('Refresco 500ml', 2)], 'dias_atras': 1},
            {'cliente': 'Maria Garcia', 'metodo': 'tarjeta', 'items': [('Hot Dog', 1), ('Papas Fritas', 2), ('Refresco 500ml', 1)], 'dias_atras': 2},
            {'cliente': 'Carlos Lopez', 'metodo': 'efectivo', 'items': [('Martillo', 1), ('Cinta Metrica 5m', 1)], 'dias_atras': 3},
            {'cliente': 'Ana Martinez', 'metodo': 'transferencia', 'items': [('Cuaderno Universitario', 3), ('Boli Azul', 5), ('Resma de Papel', 1)], 'dias_atras': 5},
            {'cliente': 'Pedro Rodriguez', 'metodo': 'efectivo', 'items': [('Hamburguesa Doble', 1), ('Papas Fritas', 1), ('Refresco 500ml', 1)], 'dias_atras': 7},
            {'cliente': 'Juan Perez', 'metodo': 'tarjeta', 'items': [('Jabon Liquido 500ml', 2), ('Desinfectante 1L', 1), ('Papel Toalla', 3)], 'dias_atras': 10},
        ]

        for vdata in ventas_data:
            cliente = clientes.get(vdata['cliente'])
            items = []
            total = Decimal('0')
            skip = False

            for item_name, qty in vdata['items']:
                prod = Producto.objects.filter(nombre=item_name).first()
                if not prod:
                    print(f'  ! Producto no encontrado: {item_name}')
                    skip = True
                    break
                if prod.stock_actual < qty:
                    print(f'  ! Stock insuficiente: {item_name} (disp: {prod.stock_actual}, req: {qty})')
                    skip = True
                    break
                items.append((prod, qty))
                total += prod.precio_venta * Decimal(str(qty))

            if skip or not items:
                continue

            fecha = timezone.now() - timezone.timedelta(days=vdata['dias_atras'])
            ticket_num = Venta.objects.count() + 1
            venta = Venta.objects.create(
                codigo_ticket=f'SEED-{ticket_num:04d}',
                cajero_user=cajero_user,
                cajero=cajero_user.get_full_name() or cajero_user.username,
                cliente=cliente,
                metodo_pago=vdata['metodo'],
                total_pagado=total,
                fecha_venta=fecha,
            )

            for prod, qty in items:
                DetalleVenta.objects.create(
                    venta=venta,
                    id_producto=prod,
                    cantidad=qty,
                    precio_unitario=prod.precio_venta,
                )
                MovimientoStock.objects.create(
                    producto=prod,
                    tipo='salida',
                    cantidad=qty,
                    motivo='venta',
                    notas=f'Venta #{venta.codigo_ticket}',
                )
                prod.stock_actual -= Decimal(str(qty))
                prod.save(update_fields=['stock_actual'])

            print(f'  + Venta #{venta.codigo_ticket}: {cliente.nombre if cliente else "Mostrador"} - ${total}')

    print(f'\n=== RESUMEN ===')
    print(f'Categorias: {Categoria.objects.count()}')
    print(f'Proveedores: {Proveedor.objects.count()}')
    print(f'Productos: {Producto.objects.count()}')
    print(f'Clientes: {Cliente.objects.count()}')
    print(f'Ventas: {Venta.objects.count()}')
    print(f'Movimientos: {MovimientoStock.objects.count()}')
    print('==============')


if __name__ == '__main__':
    run()
