# 📋 Guía de Flujos de Negocio por Rol

## Sistema de Gestión Integral: Inventario, Recetas, Órdenes y Ventas

---

## 🎫 Rol: CAJERO (Ventas y POS)

### Permisos Principales
- Acceso al Punto de Venta (POS)
- Gestión de órdenes y ventas
- Cambio de estado limitado de órdenes
- Visualización de reportes básicos

### 🔄 Flujo de Trabajo: Registrar una Venta

#### Paso 1: Preparar la Orden
```
POS (Punto de Venta)
  ↓
1. Cliente solicita producto
2. Buscar producto en catálogo
3. Agregar al carrito con cantidad
4. Verificar disponibilidad visual
```

#### Paso 2: Crear Orden de Pedido
```
Órdenes → Nueva Orden
  ↓
1. Ingresar datos del cliente (nombre, teléfono)
2. Estado inicial: "Pendiente"
3. Guardar orden (genera número secuencial: ORD-AAAAMMDD-NNN)
4. Notificar cocina/preparación
```

#### Paso 3: Cambiar Estado de Orden
```
Estados permitidos:
  Pendiente → En preparación → Listo → Entregado
  
1. Ir a lista de órdenes
2. Seleccionar orden
3. Usar formulario "Cambiar Estado"
4. Confirmar transición
```

#### Paso 4: Registrar la Venta (Cobro)
```
Ventas → Registrar Venta
  ↓
1. Seleccionar orden asociada
2. Elegir método de pago:
   - Efectivo
   - Tarjeta
   - Transferencia
   - Otro
3. Confirmar venta
```

**⚠️ IMPORTANTE**: Al registrar la venta:
- ✅ Se descuenta automáticamente el inventario (insumos)
- ✅ Se crean movimientos de stock (tipo: salida)
- ✅ Se registra auditoría
- ✅ Todo en transacción atómica (rollback si falla)

#### Paso 5: Entregar al Cliente
```
1. Verificar estado: "Entregado"
2. Cobrar si no fue prepago
3. Registrar en sistema (si aplica)
4. Cerrar orden
```

### 📊 Reportes Disponibles (Cajero)
- Ventas del día/semana/mes
- Productos más vendidos
- Órdenes pendientes
- Stock crítico (alertas)

### 🚫 Restricciones
- ❌ No puede modificar precios
- ❌ No puede crear/editar recetas
- ❌ No puede hacer ajustes de inventario
- ❌ No puede cancelar ventas ya registradas
- ❌ No puede ver reportes financieros completos

---

## 👨‍🍳 Rol: CHEF (Cocina y Recetas)

### Permisos Principales
- Gestión completa de recetas
- Gestión de productos finales
- Visualización de demanda
- Consulta de inventario disponible

### 🔄 Flujo de Trabajo: Crear/Mantener Receta

#### Paso 1: Verificar Insumos Disponibles
```
Inventario → Movimientos/Stock
  ↓
1. Revisar stock actual de insumos
2. Identificar faltantes
3. Reportar a administrador para compra
```

#### Paso 2: Crear Producto Final
```
Productos → Nuevo Producto
  ↓
1. Nombre del producto (ej: "Hamburguesa Clásica")
2. Descripción
3. Precio base (sujeto a cambios dinámicos)
4. Subir imagen (opcional)
5. Guardar
```

#### Paso 3: Crear Receta
```
Recetas → Nueva Receta
  ↓
1. Seleccionar Producto Final
2. Definir rendimientos (porciones)
3. Agregar insumos:
   - Producto (insumo base)
   - Cantidad necesaria
   - Unidad de medida
4. Calcular costo total
5. Guardar receta
```

#### Paso 4: Actualizar según Demanda
```
Reportes → Demanda por Receta
  ↓
1. Revisar ventas últimos 7/30 días
2. Identificar:
   - Recetas más vendidas
   - Recetas con baja rotación
3. Ajustar:
   - Preparación anticipada
   - Eliminar del menú (baja rotación)
   - Modificar ingredientes (costo)
```

### 📈 Precios Dinámicos (Chef/Admin)

El sistema ajusta precios automáticamente:

```python
if ventas_24h >= umbral_demanda_alta:
    precio_actual = precio_base + incremento
else:
    precio_actual = precio_base
```

**Chef puede**:
- ✅ Ver precios actuales
- ✅ Sugerir ajustes
- ❌ No modificar directamente (requiere Admin)

### 📊 Reportes Disponibles (Chef)
- Demanda por receta
- Costo de producción
- Rotación de menú
- Stock proyectado (para planificación)

---

## 📦 Rol: ADMINISTRADOR (Inventario y Operaciones)

### Permisos Principales
- Gestión completa de inventario
- Productos e insumos
- Proveedores
- Reportes completos
- Precios manuales
- Ajustes de sistema

### 🔄 Flujo de Trabajo: Gestión de Inventario

#### Paso 1: Registrar Compra de Insumos
```
Inventario → Movimientos → Nuevo
  ↓
1. Seleccionar producto (insumo)
2. Tipo: "Entrada"
3. Motivo: "Compra a proveedor"
4. Cantidad
5. Proveedor (referencia)
6. Guardar
  ↓
Resultado: Stock_actual += cantidad
```

#### Paso 2: Entrada por Producción (Merma/Transformación)
```
1. Registrar salida de insumos (receta)
2. Registrar entrada de producto final
3. Motivo: "Transformación/Elaboración"
4. Notas: detalle del proceso
```

#### Paso 3: Ajuste de Inventario
```
Inventario → Ajuste
  ↓
1. Realizar conteo físico
2. Identificar diferencias:
   - Sobrantes
   - Faltantes
3. Registrar ajuste:
   - Motivo: "Ajuste por conteo"
   - Cantidad corregida
4. Guardar movimiento
  ↓
Resultado: Stock_actual = nuevo valor
```

#### Paso 4: Manejar Mermas
```
Inventario → Movimiento
  ↓
1. Seleccionar producto
2. Tipo: "Salida"
3. Motivo: "Merma/Pérdida"
   - Caducidad
   - Daño
   - Contaminación
4. Cantidad
5. Notas: descripción detallada
6. Guardar
```

### 🔄 Flujo de Trabajo: Modificación de Precios

#### Paso 1: Análisis de Costos
```
Reportes → Costos y Margen
  ↓
1. Revisar costo actual insumos
2. Calcular costo por receta
3. Identificar margen actual
```

#### Paso 2: Decisión de Ajuste
```
if margen < minimo_aceptable:
    # Aumentar precio
    precio_nuevo = costo / (1 - margen_deseado)
elif demanda_baja:
    # Reducir precio para incentivar
    precio_nuevo = precio_actual * 0.9
else:
    # Mantener precio
    precio_nuevo = precio_actual
```

#### Paso 3: Actualizar Precio
```
Productos → Editar
  ↓
1. Modificar precio_actual
2. Guardar (se registra histórico)
3. Notificar cambios al equipo
```

### 🔄 Flujo de Trabajo: Cancelación de Orden/Venta

**Solo para problemas críticos:**

```
1. Verificar estado actual
2. Si venta registrada:
   - Revertir movimiento de stock
   - Crear movimiento inverso
   - Anular venta (is_active = False)
3. Si solo orden:
   - Cambiar estado a "Cancelado"
4. Registrar motivo
5. Guardar auditoría
```

### 📊 Reportes Disponibles (Admin)
- Valor total de inventario
- Costos y márgenes
- Historial de precios
- Movimientos detallados
- Proveedores (pendientes por pagar)
- Eficiencia (órdenes/hora)

---

## 👑 Rol: SUPERADMIN (Gestión Total)

### Permisos Principales
- TODO lo de Administrador
- Gestión de usuarios y roles
- Configuración global
- Backups y sistema
- Logs y auditoría
- Tareas automáticas

### 🔄 Flujo de Trabajo: Gestión de Usuarios

#### Paso 1: Crear Nuevo Usuario
```
Admin → Usuarios → Nuevo
  ↓
1. Datos personales
2. Username y password
3. Asignar grupos/roles:
   - Cajero
   - Chef
   - Administrador
4. Activar cuenta
5. Guardar
```

#### Paso 2: Modificar Permisos
```
Admin → Grupos → Editar
  ↓
1. Seleccionar grupo
2. Añadir/quitar permisos:
   - add_orden
   - change_venta
   - delete_movimiento
   - etc.
3. Guardar
4. Los usuarios del grupo heredan cambios
```

#### Paso 3: Auditoría de Acciones
```
Admin → Logs
  ↓
1. Filtrar por:
   - Usuario
   - Fecha
   - Acción
   - Modelo
2. Revisar cambios críticos
3. Exportar reporte
```

### 🔄 Flujo de Trabajo: Configuración Automática

#### Paso 1: Tareas Programadas
```
Admin → Scheduler
  ↓
1. Configurar tareas:
   - Actualizar precios (cada 4h)
   - Alertas stock crítico (diario)
   - Backup base de datos (semanal)
   - Limpiar logs (mensual)
2. Activar/desactivar
3. Ver historial
```

#### Paso 2: Backup y Restauración
```
Admin → Sistema → Backup
  ↓
1. Crear backup:
   - Base de datos
   - Archivos media
2. Descargar
3. Almacenar en seguro
4. Verificar integridad
```

### 📊 Reportes Disponibles (Superadmin)
- TODO reporte existente
- Logs de sistema completos
- Trazabilidad total
- Métricas de rendimiento
- Uso por usuario

---

## 📑 Registro de Auditoría (Todos los Roles)

**Toda acción crítica genera registro:**

```
Modelo: Venta
Acción: CREATE
Usuario: cajero@empresa.com
Fecha: 2026-05-02 12:30:00
IP: 192.168.1.100
Detalle: Venta #123 - Orden ORD-20260502-001
         Productos: 3
         Total: $45,500
         Stock descontado: OK
```

**Campos registrados:**
- created_at / updated_at
- created_by / updated_by
- is_active (soft delete)
- Referencia cruzada (orden/venta)

---

## 🚨 Protocolo de Errores

### Error: "Stock Insuficiente" (Venta)
```
1. Sistema bloquea la venta
2. Muestra detalle de faltantes
3. Cajero verifica con Chef
4. Opciones:
   - Esperar reposición
   - Modificar receta temporal
   - Cancelar orden
5. Registrar incidencia
```

### Error: "Pago Rechazado" (Venta)
```
1. Mantener orden en "Pendiente"
2. Notificar a Cajero
3. Intentar método alternativo
4. Si persiste: Cancelar
5. Registrar motivo
```

### Error: "Falla Sistema" (Todos)
```
1. No perder datos en curso
2. Notificar Superadmin
3. Usar modo offline si disponible
4. Registrar incidente
5. Restaurar servicio
```

---

## 📞 Contacto y Soporte

- **Incidencias críticas**: Superadmin
- **Problemas de inventario**: Administrador
- **Recetas/Calidad**: Chef
- **Ventas/Pagos**: Cajero

---

*Documentación versión 1.0 | Sistema de Gestión Integral v3.0*