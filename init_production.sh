#!/bin/bash
# Script de inicialización para producción
echo "Configurando base de datos..."

# Ejecutar migraciones
python manage.py migrate

# Crear grupos
python manage.py setup_groups

# Crear superusuario (interactivo)
echo "Creando superusuario..."
python manage.py createsuperuser

# Poblar categorías (opcional)
read -p "¿Poblar categorías y productos ejemplo? (y/n): " confirm
if [ "$confirm" = "y" ]; then
    python manage.py populate_categories
fi

echo "¡Inicialización completada!"
