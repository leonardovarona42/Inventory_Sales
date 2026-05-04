# MiNegocio - Guia de Despliegue

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    PC del Cliente                        │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│  │  PostgreSQL  │◄──►│  Django App  │◄──►│  Browser  │  │
│  │  (local)     │    │  (servicio)  │    │  (cliente)│  │
│  └──────────────┘    └──────┬───────┘    └───────────┘  │
│                             │                            │
│                    ┌────────▼────────┐                    │
│                    │  License Check  │                    │
│                    │  (middleware)   │                    │
│                    └─────────────────┘                    │
└─────────────────────────────────────────────────────────┘
         ▲
         │ Tu PC (con KeyManagement)
         │ Generas licencias → se las entregas al cliente
```

## Flujo de Despliegue

### 1. En TU computadora (desarrollo)

```bash
# Instalar dependencias del build
pip install pyinstaller pywin32 psycopg2-binary

# Configurar LICENSE_SECRET (debe ser el mismo en KeyManagement)
# Genera uno: python -c "import secrets; print(secrets.token_hex(32))"

# Descargar NSSM (https://nssm.cc/release) y colocar en:
deploy/nssm/nssm.exe

# Construir el instalador
cd deploy
python build_installer.py

# Resultado en deploy/dist/:
#   MiNegocio-Instalador.exe  (el instalador)
#   MiNegocio-Launcher.exe    (control de escritorio)
#   nssm.exe                  (gestor de servicio)
```

### 2. En la PC del Cliente

**Requisitos previos:**
- Python 3.13 instalado desde python.org
- PostgreSQL instalado y corriendo

**Instalacion:**
1. Copiar toda la carpeta `dist` a la PC del cliente (USB, red, etc.)
2. Ejecutar `MiNegocio-Instalador.exe` como Administrador
3. Segir el asistente:
   - Paso 1: Bienvenida (verifica Python)
   - Paso 2: Directorio (default: C:\MiNegocio)
   - Paso 3: Configuracion PostgreSQL (host, user, pass, test de conexion)
   - Paso 4: Configuracion de red (0.0.0.0 para acceso en red, puerto, allowed hosts)
   - Paso 5: Licencia (introducir ahora o despues)
   - Paso 6: Instalacion automatica:
     - Copia archivos
     - Crea venv
     - Instala dependencias
     - Configura .env
     - Ejecuta migraciones
     - Crea superuser (leonardo.varona)
     - Instala servicio Windows
     - Crea atajos de escritorio
   - Paso 7: Finalizado con credenciales

### 3. Post-Instalacion

El cliente puede:
- Acceder via browser: `http://<IP-servidor>:8000`
- Usar `MiNegocio-Launcher.exe` para iniciar/detener el servicio
- Ver logs en `C:\MiNegocio\Inventory_Sales\service.log`

### 4. Gestion de Licencias

**Tu (proveedor):**
```bash
# En tu PC con KeyManagement
cd KeyManagement
python main.py

# Generar licencia → copiar clave → enviar al cliente
```

**Cliente:**
- Si no introdujo licencia durante la instalacion:
  - Al abrir el browser ve la pantalla de bloqueo
  - Introduce la clave que tu le diste
  - Sistema se desbloquea

## Estructura de Archivos

```
deploy/
├── setup_wizard.py          # GUI del instalador (PyInstaller entry)
├── launcher.py              # App de escritorio para iniciar/detener
├── service_manager.py       # Gestion de servicio Windows (NSSM)
├── build_installer.py       # Script de build con PyInstaller
├── build.bat                # Batch para construir todo
├── manage_production.py     # Runner de produccion con license check
├── installer_requirements.txt
├── DEPLOY.md                # Este archivo
├── __init__.py
├── nssm/
│   └── nssm.exe             # Descargar de https://nssm.cc/release
├── resources/
└── dist/                    # Generado por el build
    ├── MiNegocio-Instalador.exe
    ├── MiNegocio-Launcher.exe
    └── nssm.exe
```

## Configuracion de Red

### Acceso en red local

1. Bind address: `0.0.0.0` (todas las interfaces)
2. Allowed Hosts: `localhost,127.0.0.1,192.168.1.100` (IP del servidor)
3. CSRF Origins: `http://192.168.1.100:8000`
4. Abrir puerto en firewall de Windows:

```powershell
# PowerShell como Administrador
New-NetFirewallRule -DisplayName "MiNegocio" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Acceso desde otras PCs

Los clientes en la red acceden via:
```
http://192.168.1.100:8000
```

Donde `192.168.1.100` es la IP del servidor.

## Credenciales por Defecto

| Campo | Valor |
|-------|-------|
| Usuario | leonardo.varona |
| Email | leonardovarona42@gmail.com |
| Contrasena | 00020875302 |

**IMPORTANTE:** Cambiar la contrasena despues de la primera instalacion.

## Troubleshooting

### El servicio no inicia
```powershell
# Ver logs
Get-Content C:\MiNegocio\Inventory_Sales\service.log

# Verificar Python
C:\MiNegocio\venv\Scripts\python.exe --version

# Reiniciar servicio con NSSM
C:\MiNegocio\nssm.exe restart MiNegocioServer
```

### Base de datos no conecta
```bash
# Test de conexion
python -c "import psycopg2; psycopg2.connect(host='localhost', dbname='inventory_sales', user='postgres', password='TU_PASSWORD')"
```

### Licencia no valida
- Verificar que `LICENSE_SECRET` en `.env` sea el mismo que en KeyManagement
- Verificar que la clave no tenga caracteres extra al copiar

### Puerto ocupado
```powershell
# Ver que usa el puerto
netstat -ano | findstr :8000
# Cambiar puerto en .env: PORT=8001
```
