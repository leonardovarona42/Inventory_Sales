# Inventory Sales

Sistema web en Django para gestionar inventario de insumos, recetas de productos finales, ordenes, ventas con POS, precios dinamicos por demanda y reportes operativos.

## Estado actual del proyecto

Implementado (alineado al MVP de `instrucciones.md`):

- Gestion de insumos y proveedores (`productos`).
- Gestion de recetas y productos finales (`recetas`).
- Inventario y movimientos de stock (`inventario`).
- Ordenes y flujo base de POS (`ordenes`).
- Ventas y detalles con descuento automatico de insumos (`ventas`).
- Dashboard con metricas iniciales (`reportes`).
- Roles base por grupos (Cajero, Chef, Administrador, Superadmin) via migracion en `usuarios`.
- Comando de precios dinamicos por demanda: `actualizar_precios_demanda`.
- Servicio transaccional para registrar ventas: `ventas.services.procesar_venta`.

Pendiente / fase futura:

- API REST con DRF.
- Auditoria avanzada con trazabilidad de usuario en todos los modelos.
- Tareas programadas productivas (Celery/Redis o APScheduler).
- Cobertura de pruebas mas amplia (integracion y seguridad).

## Requisitos

- Python 3.13
- Django 6.x
- SQLite (desarrollo)

## Instalacion y ejecucion

1. Crear y activar entorno virtual.
2. Instalar dependencias:

```bash
pip install django pillow
```

3. Aplicar migraciones:

```bash
python manage.py migrate
```

4. Crear superusuario:

```bash
python manage.py createsuperuser
```

5. Ejecutar servidor:

```bash
python manage.py runserver
```

## Apps principales

- `productos`: insumos y proveedores.
- `recetas`: productos finales, recetas y precios dinamicos.
- `inventario`: movimientos y alertas de stock.
- `ordenes`: ordenes operativas y pantalla POS.
- `ventas`: ventas, detalle de venta y servicio transaccional.
- `reportes`: dashboard y reporte de precios dinamicos.
- `usuarios`: perfil y roles.

## Comandos utiles

- Validaciones Django:

```bash
python manage.py check
```

- Ejecutar pruebas:

```bash
python manage.py test
```

- Actualizar precios por demanda:

```bash
python manage.py actualizar_precios_demanda
```
