# Backup y Restauración

## Backup de la Base de Datos

### PostgreSQL (Producción)
```bash
# Backup completo
pg_dump -h localhost -U postgres -d inventory_sales > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup comprimido
pg_dump -h localhost -U postgres -d inventory_sales | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup automatizado (cron job)
# 0 2 * * * pg_dump -h localhost -U postgres -d inventory_sales | gzip > /backups/inventory_$(date +\%Y\%m\%d).sql.gz
```

### Restauración
```bash
# Restaurar desde SQL
psql -h localhost -U postgres -d inventory_sales < backup_20260305_020000.sql

# Restaurar desde comprimido
gunzip -c backup_20260305_020000.sql.gz | psql -h localhost -U postgres -d inventory_sales
```

## Archivos Media (Imágenes de productos)
```bash
# Backup de imágenes
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Restaurar
tar -xzf media_backup_20260305.tar.gz -C /
```

## Script de Backup Automatizado
Crear `scripts/backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/backups/inventory_sales"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

# DB Backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Media Backup
tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" media/

# Mantener solo los últimos 7 días
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
```

## Monitoreo
- Logs: Ver `django.log` o configurar logging centralizado
- Errores: Usar Sentry o similar en producción
- Métricas: Prometheus + Grafana para monitoreo de DB y servidor
