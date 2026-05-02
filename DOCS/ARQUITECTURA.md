# 🏗️ Arquitectura Técnica y Guía de Implementación

## Descripción
Este documento detalla la arquitectura técnica del sistema, patrones de diseño aplicados y guías para desarrollo.

---

## 1. Estructura por Capas

### Capa de Dominio (Models)
**Ubicación:** `{app}/models.py`

**Responsabilidad:** Definir la estructura de datos y reglas de negocio básicas.

**Patrones aplicados:**
- **Active Record**: Cada modelo gestiona su propia persistencia
- **Soft Delete**: Marca `is_active` para eliminación lógica
- **Auditoría**: Campos `created_at`, `updated_at`, `created_by`

**Mejores prácticas:**
```python
class Producto(models.Model):
    # Campos de datos
    nombre = models.CharField(max_length=200)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [...]  # Optimización de consultas
        ordering = ['-created_at']
```

### Capa de Servicios (Services)
**Ubicación:** `{app}/services.py`

**Responsabilidad:** Lógica de negocio compleja y transaccional.

**Patrones aplicados:**
- **Transaction Script**: Operaciones críticas en `@transaction.atomic`
- **Domain Service**: Coordinación entre múltiples agregados

**Ejemplo - Procesar Venta:**
```python
@transaction.atomic
def procesar_venta(*, orden, metodo_pago, items):
    # 1. Validación
    validar_stock(items)
    
    # 2. Creación
    venta = Venta.objects.create(...)
    
    # 3. Efectos secundarios
    for item in items:
        DetalleVenta.objects.create(...)
        descontar_stock(item)
        registrar_movimiento(item)
    
    # 4. Confirmación
    venta.total = calcular_total(venta)
    venta.save()
    
    return venta
```

**Reglas:**
- ✅ Todo en transacción atómica
- ✅ Validar antes de modificar
- ✅ Orden: Leer → Validar → Modificar → Confirmar
- ❌ No usar `save()` con lógica en modelos
- ❌ No llamar a services desde señales

### Capa de Selectores (Queries)
**Ubicación:** `{app}/selectors.py`

**Responsabilidad:** Consultas complejas reutilizables.

**Patrón:** **Repository Pattern**

**Ejemplo:**
```python
def productos_mas_vendidos(fecha_inicio, fecha_fin, limite=10):
    return ProductoFinal.objects.filter(
        ventas__fecha_venta__range=(fecha_inicio, fecha_fin)
    ).annotate(
        total_vendido=Sum('ventas__detalles__cantidad')
    ).order_by('-total_vendido')[:limite]
```

### Capa de Señales (Signals)
**Ubicación:** `{app}/signals.py`

**Responsabilidad:** Efectos secundarios automáticos simples.

**Patrón:** **Observer**

**Uso apropiado:**
```python
@receiver(post_save, sender=MovimientoStock)
def registrar_auditoria_movimiento(sender, instance, created, **kwargs):
    if created:
        Auditoria.objects.create(
            usuario=instance.usuario,
            accion='CREAR_MOVIMIENTO',
            modelo='MovimientoStock',
            referencia_id=instance.id
        )
```

**Reglas:**
- ✅ Solo para logging/auditoría automática
- ✅ No lógica de negocio
- ❌ No modificar datos del modelo actual
- ❌ No llamar a services

### Capa de Presentación (Views/Templates)
**Responsabilidad:** Interfaz de usuario y coordinación.

**Patrón:** **MVC/MVT**

**Reglas:**
- ✅ Vistas en `views.py`
- ✅ Forms en `forms.py`
- ✅ Templates en `templates/`
- ❌ No lógica de negocio en views
- ❌ No queries en templates

---

## 2. Flujo de Operaciones Críticas

### 2.1 Venta de Producto Final

```
┌─────────────────┐
│ 1. Validación   │
│    - Stock OK   │
│    - Receta OK  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│ 2. Transaction  │────▶│ ATOMIC BLOCK     │
│    Inicio       │     │                  │
└────────┬────────┘     └────────┬─────────┘
         │                      │
         ▼                      ▼
┌─────────────────┐     ┌──────────────────┐
│ 3. Crear Venta  │     │ 4. Crear Detalles│
│    (estado=PEND)│     │    con precios   │
└────────┬────────┘     └────────┬─────────┘
         │                      │
         ▼                      ▼
┌─────────────────┐     ┌──────────────────┐
│ 5. Descontar    │◄────┤ 6. Por cada item │
│    Stock        │     │    - Receta      │
│    Producto     │     │    - Cantidad    │
└────────┬────────┘     └────────┬─────────┘
         │                      │
         ▼                      ▼
┌─────────────────┐     ┌──────────────────┐
│ 7. Registrar    │◄────┤ 8. Crear         │
│    Movimiento   │     │    MovimientoStock │
│    (tipo=salida)│     │    - referencia  │
└────────┬────────┘     └────────┬─────────┘
         │                      │
         ▼                      ▼
┌─────────────────┐     ┌──────────────────┐
│ 9. Actualizar   │     │ 10. Confirmar    │
│    Total Venta  │     │    Transaction   │
└────────┬────────┘     └────────┬─────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
            ┌─────────────┐
            │ 11. ÉXITO  │
            │    Venta   │
            └─────────────┘
```

**Rollback automático si:**
- ❌ Stock insuficiente
- ❌ Error en creación
- ❌ Excepción no controlada

### 2.2 Actualización de Precios Dinámicos

```
┌─────────────────┐
│ 1. Trigger      │
│    (Scheduler)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Por cada     │
│    producto     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Calcular     │
│    ventas_24h   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. If demanda   │
│    > umbral?    │
└────────┬────────┘
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────┐
│ 5A. +   │ │ 5B.      │
│    %   │ │ mantener │
└─────────┘ └──────────┘
    │
    ▼
┌─────────────────┐
│ 6. Registrar    │
│    histórico   │
│    de precios   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 7. Notificar    │
│    cambios      │
└─────────────────┘
```

---

## 3. Gestión de Transacciones

### 3.1 Reglas de Atomicidad

**SIEMPRE usar `@transaction.atomic` cuando:**
- ✅ Múltiples modelos se modifican
- ✅ Hay efectos secundarios (movimientos, logs)
- ✅ El usuario espera "todo o nada"

**Ejemplos:**
```python
# VENTA
@transaction.atomic
def procesar_venta(...): ...

# CANCELACIÓN
@transaction.atomic  
def cancelar_venta(venta): ...

# AJUSTE MASIVO
@transaction.atomic
def ajustar_inventario(movimientos): ...
```

**NUNCA usar transacciones anidadas innecesarias:**
```python
# ❌ MAL
@transaction.atomic
def save(self):
    with transaction.atomic():  # ¡NESTED!
        ...

# ✅ BIEN
@transaction.atomic
def procesar_venta(...):
    # Una sola transacción
    ...
```

### 3.2 Manejo de Errores

```python
from django.db import IntegrityError, transaction

def operacion_critica():
    try:
        with transaction.atomic():
            # ... operaciones
            if error:
                raise ValidationError("Motivo")
    except ValidationError as e:
        # Rollback automático
        logger.error(f"Validación falló: {e}")
        raise
    except IntegrityError as e:
        # Rollback
        logger.critical(f"Integridad BD: {e}")
        raise ValueError("Error de base de datos")
```

---

## 4. Seguridad

### 4.1 Protección de Datos

**Campos sensibles:**
```python
class Usuario(AbstractUser):
    # Nunca exponer
    password  # Gestionado por Django
    
    # Validación
    def clean(self):
        validate_password(self.password)
```

**Queries seguras:**
```python
# ✅ BIEN - ORM protege contra SQL injection
Producto.objects.filter(nombre=nombre)

# ❌ MAL - Raw SQL vulnerable
cursor.execute(f"SELECT * FROM app WHERE nombre = '{nombre}'")
```

### 4.2 Control de Acceso

**Decorators:**
```python
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Vistas basadas en función
@login_required
def mi_vista(request):
    ...

# Vistas basadas en clase
class MiVista(LoginRequiredMixin, View):
    ...
```

**Permisos personalizados:**
```python
class IsCajero(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Cajero').exists()
```

---

## 5. Testing Estratégico

### 5.1 Prioridades

| Tipo | Cobertura | Ejemplo |
|------|-----------|----------|
| **Unit** | 70% | Cálculo de stock |
| **Integration** | 50% | Flujo venta completa |
| **E2E** | 30% | UI POS |

### 5.2 Ejemplos de Tests

```python
from django.test import TestCase
from django.db import IntegrityError

class VentaTestCase(TestCase):
    
    def setUp(self):
        self.producto = ProductoFinal.objects.create(...)
        self.orden = Orden.objects.create(...)
    
    def test_venta_desconta_stock(self):
        """Verifica que la venta reduzca inventario"""
        stock_inicial = self.producto.stock_actual
        
        venta = procesar_venta(
            orden=self.orden,
            metodo_pago='efectivo',
            items=[{'producto_final': self.producto, 'cantidad': 2}]
        )
        
        self.producto.refresh_from_db()
        self.assertLess(
            self.producto.stock_actual, 
            stock_inicial
        )
    
    def test_venta_stock_insuficiente_falla(self):
        """Verifica rollback si no hay stock"""
        with self.assertRaises(ValidationError):
            procesar_venta(
                orden=self.orden,
                metodo_pago='efectivo',
                items=[{'producto_final': self.producto, 'cantidad': 9999}]
            )
```

---

## 6. Optimización

### 6.1 Queries

**Problema: N+1**
```python
# ❌ MAL - N+1 queries
for venta in Venta.objects.all():
    for item in venta.detalles.all():  # ¡QUERY por cada venta!
        print(item.producto.nombre)

# ✅ BIEN - select_related/prefetch_related
for venta in Venta.objects.prefetch_related(
    'detalles__id_producto_final'
).all():
    for item in venta.detalles.all():
        print(item.id_producto_final.nombre)
```

### 6.2 Caché

```python
from django.core.cache import cache

def obtener_reporte_diario():
    key = 'reporte_diario_' + str(date.today())
    
    reporte = cache.get(key)
    if reporte is None:
        reporte = calcular_reporte()  # Costoso
        cache.set(key, reporte, timeout=86400)  # 24h
    
    return reporte
```

---

## 7. Logging y Monitoreo

### 7.1 Configuración

```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/inventory/errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
        },
        'ventas': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### 7.2 Uso

```python
import logging
logger = logging.getLogger('ventas')

def procesar_venta(...):
    logger.info(f"Iniciando venta para orden {orden.id}")
    try:
        ...
        logger.info(f"Venta {venta.id} procesada exitosamente")
    except Exception as e:
        logger.error(f"Error en venta: {e}", exc_info=True)
        raise
```

---

## 8. Despliegue

### 8.1 Checklist Producción

- [ ] DEBUG = False
- [ ] SECRET_KEY en variable de entorno
- [ ] ALLOWED_HOSTS configurado
- [ ] HTTPS habilitado
- [ ] Base de datos PostgreSQL
- [ ] STATIC_ROOT configurado
- [ ] Media en S3/Cloud
- [ ] Backups automáticos
- [ ] Monitoreo activo
- [ ] Logs centralizados

### 8.2 Comandos Útiles

```bash
# Migraciones
python manage.py makemigrations
python manage.py migrate

# Tests
python manage.py test --keepdb

# Collect static
python manage.py collectstatic --noinput

# Superusuario
python manage.py createsuperuser

# Check
python manage.py check --deploy
```

---

## 9. Referencias

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Design Patterns](https://djangobook.com/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

*Versión 1.0 | Actualizado 2026*