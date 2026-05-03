# 🏪 Inventory Sales — Sistema de Gestión de Inventario y Punto de Venta

> Sistema web moderno para gestión de inventario, ventas y punto de venta (POS). Diseñado para negocios que necesitan control de stock, ventas rápidas y gestión de usuarios con una interfaz limpia y responsiva.

<div align="center">

![Django](https://img.shields.io/badge/Django-6.0-0C4B33?logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0-06B6D4?logo=tailwindcss&logoColor=white)
![License](https://img.shields.io/badge/License-Proprietary-red)

</div>

---

## ✨ Características

### 🛒 Punto de Venta (POS)
- Interfaz rápida con búsqueda en tiempo real y filtros por categoría
- Carrito de compras con actualización instantánea
- Múltiples métodos de pago: efectivo, tarjeta, transferencia
- Diseño responsivo: funciona en desktop, tablet y móvil
- Descuento automático de stock al confirmar venta

### 📦 Inventario
- Categorías jerárquicas (categoría principal → subcategorías)
- Control de stock actual y stock mínimo con alertas
- Registro de movimientos de entrada y salida
- Trazabilidad completa de cada transacción

### 👥 Gestión de Usuarios
- **Superadmin**: acceso total, reportes, gestión de usuarios
- **Administrador**: inventario, productos, proveedores, movimientos
- **Cajero**: punto de venta y registro de ventas

### 📊 Dashboard
- Ventas del día y métricas principales
- Productos más vendidos
- Alertas de stock bajo
- Reportes por rango de fechas

### 📱 Responsivo
- Sidebar colapsable en móvil con overlay
- POS optimizado para pantallas táctiles
- Carrito móvil como bottom sheet deslizable
- Grid de productos adaptativo (2-3-4 columnas)

---

## 🏗️ Estructura del Proyecto

```
Inventory_Sales/
├── Inventory_Sales/          # Configuración principal
│   ├── settings.py           # Settings (DB, apps, middleware)
│   ├── urls.py               # Rutas globales
│   └── wsgi.py               # WSGI config
├── productos/                # Productos y categorías
│   ├── models.py             # Producto, Categoria, Proveedor
│   ├── forms.py              # Formularios con widgets estilizados
│   └── admin.py              # Admin registrado
├── inventario/               # Movimientos de stock
│   ├── models.py             # MovimientoStock
│   └── views.py              # Listado y filtros
├── ventas/                   # Punto de venta y ventas
│   ├── models.py             # Venta, DetalleVenta
│   ├── services.py           # Lógica transaccional de venta
│   ├── views.py              # POS, AJAX, listados
│   └── tests.py              # Tests unitarios
├── usuarios/                 # Autenticación y gestión
│   ├── models.py             # UsuarioPerfil
│   ├── forms.py              # UsuarioForm, CambiarPasswordForm
│   └── views.py              # CRUD de usuarios, perfil
├── templates/                # Templates HTML
│   ├── base.html             # Layout principal con sidebar
│   ├── ventas/pos.html       # Interfaz del punto de venta
│   └── ...
└── populate_categories.py    # Script de seeding inicial
```

---

## 🚀 Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| **Backend** | Python 3.13, Django 6.0 |
| **Base de datos** | PostgreSQL (producción) / SQLite (dev) |
| **Frontend** | TailwindCSS (CDN), Font Awesome 6, Vanilla JS |
| **Auth** | Django Authentication, Groups & Permissions |
| **Testing** | Django TestCase |

---

## 📦 Instalación Rápida

### 1. Clonar y preparar
```bash
git clone https://github.com/leonardovarona42/Inventory_Sales.git
cd Inventory_Sales
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

### 2. Configurar base de datos
Edita `Inventory_Sales/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventory_sales',
        'USER': 'postgres',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Migrar y poblar
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py populate_categories   # Categorías y productos ejemplo
python manage.py setup_groups          # Roles: Superadmin, Admin, Cajero
python manage.py createsuperuser       # Usuario administrador
```

### 4. Ejecutar
```bash
python manage.py runserver
```
Abre [http://localhost:8000](http://localhost:8000)

---

## 🎯 Flujo de Uso

```
1. Superadmin crea usuarios y asigna roles
2. Admin gestiona productos, categorías y proveedores
3. Cajero abre el POS, busca productos y crea ventas
4. Al confirmar: stock se descuenta automáticamente
5. Dashboard muestra métricas en tiempo real
```

---

## 🧪 Tests

```bash
python manage.py test ventas --verbosity=2
```

Cobertura actual:
- ✅ Procesar venta exitosa
- ✅ Validación de stock insuficiente
- ✅ Cancelar venta revierte stock
- ✅ Cálculo correcto del total

---

## 📱 Capturas de Funcionalidad

### POS (Desktop)
- Búsqueda full width arriba
- Categorías con scroll horizontal
- Grid de productos 3-4 columnas
- Carrito lateral derecho fijo

### POS (Móvil)
- Productos en grid de 2 columnas
- Botón flotante verde para abrir carrito
- Carrito como bottom sheet deslizable
- Confirmación de venta en modal

---

## 🔧 Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `python manage.py runserver` | Servidor de desarrollo |
| `python manage.py migrate` | Aplicar migraciones |
| `python manage.py makemigrations` | Crear migraciones |
| `python manage.py createsuperuser` | Crear admin |
| `python manage.py populate_categories` | Poblar datos ejemplo |
| `python manage.py setup_groups` | Crear roles |
| `python manage.py test` | Ejecutar tests |

---

## 📈 Roadmap

- [ ] API REST con Django REST Framework
- [ ] Impresión de tickets/reportes
- [ ] Exportar reportes a PDF/Excel
- [ ] Multi-sucursal
- [ ] Dashboard en tiempo real con WebSockets
- [ ] App móvil (React Native / Flutter)

---

## 🤝 Contribuir

1. Haz fork del repositorio
2. Crea una rama feature: `git checkout -b feature/nombre`
3. Commit: `git commit -m 'feat: descripción'`
4. Push: `git push origin feature/nombre`
5. Abre un Pull Request

---

## 📄 Licencia

Propietaria. Todos los derechos reservados.

---

<div align="center">

**Inventory Sales v4.0** — Construido con Django y TailwindCSS

---

Desarrollado por **Leonardo L. Varona Tabares**

[![Email](https://img.shields.io/badge/Email-leonardovarona42@gmail.com-D14836?logo=gmail&logoColor=white)](mailto:leonardovarona42@gmail.com)
[![Phone](https://img.shields.io/badge/Phone-%2B53%205800%203511-25D366?logo=whatsapp&logoColor=white)](tel:+5358003511)

Hecho con ❤️ para negocios que necesitan control real

</div>
