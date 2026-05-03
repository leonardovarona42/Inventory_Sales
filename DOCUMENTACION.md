# Sistema de Gestion de Ventas e Inventario

## Descripcion

Sistema web para gestionar ventas e inventario de productos categorizados. Diseñado para negocios que necesitan control de stock, punto de venta rapido y reportes de gestion.

## Caracteristicas

### Punto de Venta (POS)
- Interfaz rapida con grid de productos
- Busqueda en tiempo real y filtros por categoria
- Carrito con confirmacion modal
- Metodos de pago: Efectivo, Tarjeta, Transferencia, Otro
- Descuento automatico de stock al confirmar venta
- Generacion de ticket con codigo unico

### Inventario
- Productos organizados por categorias
- Control de stock con alertas de minimo
- Registro de movimientos (entradas/salidas)
- Historial de transacciones por producto

### Categorias
| Categoria | Icono | Descripcion |
|-----------|-------|-------------|
| **Aseo** | fa-soap | Productos de limpieza e higiene |
| **Alimentos** | fa-utensils | Alimentos y productos terminados |
| ↳ Productos Terminados | fa-burger | Articulos listos para venta (ej: Hamburguesa Clasica) |
| **Utiles** | fa-pen-ruler | Material de oficina y escolar |
| **Herramientas** | fa-screwdriver-wrench | Herramientas y equipos |

### Roles y Permisos
| Rol | Acceso |
|-----|--------|
| **Cajero** | Punto de venta, ver sus propias ventas |
| **Administrador** | POS, inventario, productos, anular ventas |
| **Superadmin** | Acceso total + gestion de usuarios y proveedores + reportes |

### Reportes
- Dashboard con KPIs (ventas, ingresos, stock bajo)
- Grafico de ventas ultimos 7 dias
- Top 10 productos mas vendidos
- Resumen por cajero

## Stack Tecnologico

- **Backend**: Python 3.13, Django 6.0.4
- **Base de datos**: PostgreSQL (produccion), SQLite (desarrollo)
- **Frontend**: TailwindCSS, Font Awesome, Chart.js
- **Autenticacion**: Django Auth con grupos

## Instalacion

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos en Inventory_Sales/settings.py
# Por defecto usa PostgreSQL

# Migraciones
python manage.py migrate

# Crear grupos
python manage.py setup_groups

# Crear superusuario
python manage.py createsuperuser

# Poblar categorias y productos de ejemplo
python populate_categories.py

# Ejecutar
python manage.py runserver
```

## Estructura del Proyecto

```
Inventory_Sales/
├── Inventory_Sales/         # Configuracion Django
│   ├── settings.py
│   └── urls.py
├── productos/               # Productos, categorias, proveedores
│   ├── models.py            # Categoria, Proveedor, Producto
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── inventario/              # Movimientos de stock
│   ├── models.py            # MovimientoStock
│   └── views.py
├── ventas/                  # Punto de venta y transacciones
│   ├── models.py            # Venta, DetalleVenta
│   ├── views.py             # POS con AJAX
│   ├── services.py          # Logica transaccional
│   └── urls.py
├── reportes/                # Dashboard y estadisticas
│   └── views.py
├── usuarios/                # Gestion de usuarios y roles
│   ├── models.py            # UsuarioPerfil
│   ├── views.py             # CRUD usuarios, perfil, password
│   ├── forms.py
│   └── management/commands/
│       └── setup_groups.py  # Crea grupos del sistema
├── templates/               # Templates TailwindCSS
│   ├── base.html
│   ├── home.html
│   ├── registration/
│   ├── productos/
│   ├── ventas/
│   ├── inventario/
│   ├── reportes/
│   └── usuarios/
└── populate_categories.py   # Script categorias y productos ejemplo
```

## Flujo de Venta

```
1. Cajero abre POS → selecciona productos → agrega al carrito
2. Confirma venta → metodo de pago → procesar
3. Sistema: crea Venta + DetalleVenta + descuenta stock + registra movimiento
4. Ticket generado automaticamente
5. Admin puede anular venta (revierte stock)
```

## Comandos Utiles

```bash
python manage.py setup_groups        # Crear grupos (Superadmin, Admin, Cajero)
python populate_categories.py        # Poblar categorias y productos
python manage.py createsuperuser     # Crear admin
python manage.py makemigrations      # Generar migraciones
python manage.py migrate             # Aplicar migraciones
```

## Notas

- Los productos tienen stock directo (sin recetas)
- Al vender se descuenta stock del producto vendido
- Las categorias permiten organizacion jerarquica
- Los cajeros solo ven sus propias ventas
- Superadmin tiene acceso completo al sistema

---

© 2026 Inventory Sales System | Django 6.0.4
