# 🏪 Sistema de Gestión Integral de Inventario, Recetas, Órdenes y Ventas

## 📄 Descripción del Proyecto

**Inventory Sales** es una solución empresarial completa diseñada para negocios del sector gastronómico, retail y producción que requieren control preciso de inventario compuesto, gestión de recetas, seguimiento de órdenes y registro de ventas con precios dinámicos.

Desarrollado con **Django 6+** y **Bootstrap 5**, este sistema ofrece una arquitectura escalable, segura y modular que permite a negocios como restaurantes, panaderías, dark kitchens y producción alimentaria gestionar operaciones críticas con trazabilidad completa y protección de datos.

---

## ✨ Características Principales

### 🎯 Core Business Features
- **Gestión de Inventario Compuesto**: Control de insumos y materias primas con trazabilidad completa
- **Recetas y Fórmulas**: Gestión de productos finales con cálculo automático de costos
- **Punto de Venta (POS)**: Interfaz rápida para registro de pedidos y ventas
- **Órdenes de Trabajo**: Flujo de estados (pendiente → preparando → listo → entregado)
- **Ventas con Métodos de Pago**: Efectivo, tarjeta, transferencia
- **Precios Dinámicos**: Ajuste automático basado en demanda
- **Movimientos de Stock**: Registro detallado de entradas/salidas por cada transacción

### 🔒 Seguridad y Auditoría
- **Transacciones Atómicas**: Rollback automático en operaciones críticas
- **Control de Roles**: Cajero, Chef, Administrador, Superadmin
- **Registro Completo**: Trazabilidad de todos los cambios en el sistema
- **Soft Delete**: Borrado lógico para preservar histórico
- **CSRF Protection**: Seguridad integrada Django

### 📊 Reporting & Analytics
- Dashboard con KPIs principales
- Productos más vendidos
- Alertas de stock crítico
- Valor de inventario
- Reportes por rangos de fecha
- Gráficos interactivos con Chart.js

---

## 🏗️ Arquitectura del Sistema

```
inventory_sales/
├── config/                          # Configuración Django
│   ├── settings.py                  # Settings
│   ├── urls.py                      # Rutas principales
│   └── wsgi.py                      # WSGI
├── DOCS/                            # 🆕 Documentación de procesos
│   ├── FLUJOS_ROLES.md             # Guías por rol de usuario
│   └── ARQUITECTURA.md             # Detalles técnicos
├── productos/                       # Insumos y materias primas
│   ├── models.py                    # Modelo Producto
│   └── ...
├── recetas/                         # Productos finales y fórmulas
│   ├── models.py                    # ProductoFinal, DetalleReceta
│   └── ...
├── inventario/                      # Movimientos y stock
│   ├── models.py                    # MovimientoStock
│   └── ...
├── ordenes/                         # Órdenes de pedido
│   ├── models.py                    # Orden (estados: pendiente→entregado)
│   ├── views.py                     # POS, lista, creación
│   └── ...
├── ventas/                          # Transacciones de venta
│   ├── models.py                    # Venta, DetalleVenta
│   ├── services.py                  # 🆕 Lógica de negocio (transaccional)
│   └── ...
├── usuarios/                        # Gestión de usuarios y roles
│   ├── views.py                     # Registro, autenticación
│   └── ...
├── templates/                       # Templates base y componentes
│   ├── base.html                    # Layout principal
│   ├── registration/                # Login, logout
│   └── ...
└── DOCS/                            # 📚 Documentación
    ├── FLUJOS_ROLES.md             # Procesos por rol
    └── README.md                    # Este archivo
```

---

## 🔐 Modelo de Datos Principal

### Entidades Clave

**Producto** (Insumo/Materia Prima)
- Stock actual
- Unidad de medida
- Proveedor
- Historial de precios

**ProductoFinal** (Artículo vendible)
- Receta asociada
- Precio actual (dinámico)
- Imagen
- Descripción

**Orden** (Pedido)
- Número secuencial único
- Cliente (nombre, teléfono)
- Estado: pendiente → preparando → listo → entregado → cancelado
- Total

**Venta** (Transacción)
- Método de pago
- Total pagado
- Items (DetalleVenta)
- UnaOrden (OneToOne)

**MovimientoStock** (Auditoría)
- Entrada/Salida
- Cantidad
- Motivo (compra, venta, ajuste, merma)
- Referencia (orden/venta)

---

## 🎭 Roles y Permisos

| Rol | Permisos | Acceso Especial |
|-----|----------|-----------------|
| **Cajero** | POS, Ventas, Órdenes (estado limitado) | - |
| **Chef** | Recetas, ProductosFinal, Dashboard | Demanda, costos |
| **Administrador** | TODO + Inventario, Precios, Reportes | Ajustes, proveedores |
| **Superadmin** | TODO + Usuarios, Config, Logs | Sistema completo |

---

## 🚀 Stack Tecnológico

### Backend
- **Python 3.13**
- **Django 6.0.4** (Framework web)
- **Django ORM** (Base de datos)
- **PostgreSQL** (Producción) / SQLite (Dev)

### Frontend
- **Bootstrap 5** (UI/UX)
- **Chart.js** (Visualización)
- **Vanilla JS** (Interactividad)

### Seguridad
- **Django Auth** (Autenticación)
- **CSRF Tokens** (Protección)
- **Password Validators** (Seguridad)
- **HTTPS Ready** (Producción)

---

## 📦 Instalación y Configuración

### Requisitos Previos
```bash
# Python 3.13+
# PostgreSQL (recomendado)
# Git
```

### Pasos de Instalación

#### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd Inventory_Sales
```

#### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

#### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4. Configurar base de datos
```python
# Inventory_Sales/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventory_sales',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### 5. Aplicar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Crear superusuario
```bash
python manage.py createsuperuser
```

#### 7. Correr servidor de desarrollo
```bash
python manage.py runserver
```

#### 8. Acceder al sistema
```
http://localhost:8000
```

---

## 🏭 Flujo de Negocio Principal

### 1. Configurar Productos e Insumos
```
Admin → Productos → Añadir insumos
Admin → Recetas → Crear productos finales con fórmulas
```

### 2. Tomar Pedidos (POS)
```
Cajero → POS → Seleccionar productos → Agregar al carrito
         → Crear orden → Estado: Pendiente
```

### 3. Preparar Ordenes
```
Chef → Órdenes → Cambiar estado: Preparando → Listo
      → Notificar a Cajero
```

### 4. Registrar Venta
```
Cajero → Ventas → Seleccionar orden → Método de pago
        → Confirmar
        ↓
        ✅ Stock descontado automáticamente
        ✅ Movimientos registrados
        ✅ Venta confirmada
```

### 5. Entregar al Cliente
```
Cajero/Chef → Cambiar estado: Entregado
           → Cerrar orden
```

---

## 🎯 Casos de Uso Principales

### 🍔 Restaurante / Cafetería
- Menú con precios dinámicos
- Gestión de recetas
- Control de porciones
- Pedidos en barra/mesa

### 🥐 Panadería
- Producción programada
- Mermas controladas
- Venta por peso/unidad
- Stock de insumos (harina, levadura)

### 🏬 Tienda Retail
- Productos simples
- Control de stock básico
- Venta directa
- Reportes de rotación

### 🍱 Dark Kitchen
- Solo delivery
- Preparación por recetas
- Control de tiempos
- Costeo preciso

---

## 🔧 Personalización

### Ajustar Umbral de Precios Dinámicos
```python
# config/settings.py
PRECIO_DINAMICO_UMBRAL = 10  # unidades/24h
PRECIO_DINAMICO_INCREMENTO = 0.15  # 15%
```

### Modificar Roles y Permisos
```python
# usuarios/groups.py
from django.contrib.auth.models import Group, Permission

cajeros = Group.objects.create(name='Cajero')
permisos = Permission.objects.filter(
    codename__in=['add_orden', 'change_venta', 'view_producto']
)
cajeros.permissions.set(permisos)
```

### Agregar Nuevos Motivos de Movimiento
```python
# inventario/models.py
class MovimientoStock(models.Model):
    MOTIVOS = (
        ('compra', 'Compra a proveedor'),
        ('venta', 'Venta'),
        ('ajuste', 'Ajuste de inventario'),
        ('merma', 'Merma/Pérdida'),
        ('devolucion', 'Devolución'),
        # Añadir nuevos aquí
    )
```

---

## 📈 Roadmap Futuro

### Q3 2026 (Fase 2)
- ✅ Dashboard avanzado
- 🔄 API REST con DRF
- 🔄 Multi-sucursal
- 🔄 Integración facturación electrónica

### Q4 2026 (Fase 3)
- 🔄 App móvil (Flutter)
- 🔄 E-commerce frontend
- 🔄 Webhooks (WooCommerce, Shopify)
- 🔄 Inteligencia artificial para demanda

---

## 🤝 Contribución

1. Fork el proyecto
2. Crea rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Añade: descripción'`)
4. Push a rama (`git push origin feature/nueva-funcionalidad`)
5. Abre Pull Request

---

## 📄 Licencia

Desarrollado para Pyme de Inventario y Ventas.

Distribuido bajo licencia propietaria.

---

## 📞 Soporte

Para soporte y documentación detallada, ver:
- [DOCS/FLUJOS_ROLES.md](DOCS/FLUJOS_ROLES.md) - Guías por rol
- [DOCS/ARQUITECTURA.md](DOCS/ARQUITECTURA.md) - Detalles técnicos

---

## ⭐ Agradecimientos

- Django Community
- Bootstrap Team
- PostgreSQL

---

**© 2026 Inventory Sales System v3.0 | Construido para escalar**