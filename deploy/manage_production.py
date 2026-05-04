"""
Production Django server runner.
Handles network binding, allowed hosts, and license verification.
"""
import os
import sys
import socket
from pathlib import Path

# Ensure project is in path
PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventory_Sales.settings')


def get_local_ip():
    """Get the local IP address for network access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def check_license():
    """Verify license before starting server."""
    try:
        import django
        django.setup()

        from licencias.services import obtener_licencia_activa, verificar_y_actualizar

        licencia = obtener_licencia_activa()
        if licencia is None:
            print("=" * 60)
            print("WARNING: No hay licencia activa.")
            print("El sistema estara bloqueado hasta que se active una licencia.")
            print("Visite: http://localhost:{port}/activar-licencia/")
            print("=" * 60)
            return

        es_valida, mensaje = verificar_y_actualizar(licencia)
        if not es_valida:
            print("=" * 60)
            print(f"WARNING: Licencia no valida - {mensaje}")
            print("El sistema estara bloqueado.")
            print("=" * 60)
        else:
            print(f"Licencia: {licencia.cliente_nombre} ({licencia.tipo}) - {mensaje}")

    except Exception as e:
        print(f"Warning: No se pudo verificar licencia: {e}")


def main():
    import django
    from django.core.management import execute_from_command_line

    # Verify license
    check_license()

    # Get configuration from .env
    from dotenv import load_dotenv
    load_dotenv(PROJECT_DIR / '.env')

    bind_address = os.environ.get('BIND_ADDRESS', '0.0.0.0')
    port = os.environ.get('PORT', '8000')

    # Update allowed hosts dynamically
    allowed_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
    if '*' not in allowed_hosts:
        local_ip = get_local_ip()
        if local_ip not in allowed_hosts:
            allowed_hosts += f",{local_ip}"
            os.environ['DJANGO_ALLOWED_HOSTS'] = allowed_hosts

    print("=" * 60)
    print("  MiNegocio - Sistema de Gestion")
    print("=" * 60)
    print(f"  Vinculado a: {bind_address}:{port}")
    print(f"  URL local:   http://localhost:{port}")
    print(f"  URL red:     http://{get_local_ip()}:{port}")
    print("=" * 60)
    print()

    # Run server
    argv = [
        'manage.py',
        'runserver',
        f'{bind_address}:{port}',
        '--noreload',
    ]

    execute_from_command_line(argv)


if __name__ == '__main__':
    main()
