#!/bin/bash
# Script de inicialización FINAL para producción (Neon + Vercel)

echo "=== Configurando Inventory Sales para FULL ACCESS ==="

# 1. Configurar variables de entorno (cargar desde .env)
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 2. Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate

# 3. Crear grupos de usuarios
echo "Creando grupos (Superadmin, Administrador, Cajero)..."
python manage.py setup_groups

# 4. Poblar categorías (opcional)
read -p "¿Poblar categorías y productos ejemplo? (y/n): " confirm
if [ "$confirm" = "y" ]; then
    echo "Poblando categorías..."
    python manage.py populate_categories
fi

# 5. Crear superusuario (interactivo)
echo "=== Creación de Superusuario ==="
python manage.py createsuperuser

echo "=== Inicialización completada ==="
echo "Accede a: https://inventory-sales-liart.vercel.app"
echo "Usa las credenciales que acabas de crear"
