"""
Windows Service Manager for MiNegocio.
Handles installation, starting, stopping, and removal of the service.
Uses NSSM (Non-Sucking Service Manager) as the service wrapper.
"""
import os
import subprocess
import sys
from pathlib import Path


SERVICE_NAME = "MiNegocioServer"
SERVICE_DISPLAY_NAME = "MiNegocio Server"
SERVICE_DESCRIPTION = "Sistema de Gestion de Inventario y Ventas"


def find_nssm(install_dir=None):
    """NSSM is optional. Returns None to use schtasks fallback."""
    return None


def install_service(python_exe, manage_py, project_dir, port="8000", bind_address="0.0.0.0"):
    """Install the Django server as a Windows service."""
    nssm = find_nssm(project_dir)

    if nssm:
        return _install_with_nssm(nssm, python_exe, manage_py, project_dir, port, bind_address)
    else:
        return _install_with_schtasks(python_exe, manage_py, project_dir, port, bind_address)


def _install_with_nssm(nssm, python_exe, manage_py, project_dir, port, bind_address):
    """Install using NSSM."""
    try:
        # Remove existing service if any
        subprocess.run([nssm, "remove", SERVICE_NAME, "confirm"],
                      capture_output=True)

        # Install service
        subprocess.run([
            nssm, "install", SERVICE_NAME, python_exe,
            manage_py, "runserver", f"{bind_address}:{port}", "--noreload"
        ], capture_output=True, check=True)

        # Configure service
        configs = [
            ("AppDirectory", project_dir),
            ("DisplayName", SERVICE_DISPLAY_NAME),
            ("Description", SERVICE_DESCRIPTION),
            ("Start", "SERVICE_AUTO_START"),
            ("AppStdout", os.path.join(project_dir, "service.log")),
            ("AppStderr", os.path.join(project_dir, "service_error.log")),
        ]

        for key, value in configs:
            subprocess.run([nssm, "set", SERVICE_NAME, key, value],
                          capture_output=True, check=True)

        # Set environment variables for the service
        env_vars = [
            ("PYTHONUNBUFFERED", "1"),
            ("DJANGO_SETTINGS_MODULE", "Inventory_Sales.settings"),
        ]

        for key, value in env_vars:
            subprocess.run([nssm, "set", SERVICE_NAME, "AppEnvironmentExtra",
                           f"{key}={value}"], capture_output=True)

        return True, "Servicio instalado con NSSM"

    except subprocess.CalledProcessError as e:
        return False, f"Error NSSM: {e}"


def _install_with_schtasks(python_exe, manage_py, project_dir, port, bind_address):
    """Fallback: Install as a scheduled task that runs at startup."""
    try:
        bat_content = f"""@echo off
cd /d "{project_dir}"
set DJANGO_SETTINGS_MODULE=Inventory_Sales.settings
set PYTHONPATH={project_dir}
set PYTHONUNBUFFERED=1
"{python_exe}" "{manage_py}" runserver {bind_address}:{port} --noreload >> "{project_dir}\\service.log" 2>&1
"""
        bat_path = os.path.join(project_dir, "run_service.bat")
        with open(bat_path, 'w') as f:
            f.write(bat_content)

        # Create scheduled task
        task_cmd = (
            f'schtasks /create /tn "{SERVICE_NAME}" /tr "{bat_path}" '
            f'/sc onstart /rl highest /f'
        )
        subprocess.run(task_cmd, shell=True, capture_output=True, check=True)

        return True, "Servicio instalado como Scheduled Task"

    except Exception as e:
        return False, f"Error schtasks: {e}"


def start_service():
    """Start the service."""
    nssm = find_nssm()
    if nssm:
        result = subprocess.run([nssm, "start", SERVICE_NAME], capture_output=True)
        return result.returncode == 0
    else:
        result = subprocess.run(
            f'net start "{SERVICE_NAME}"', shell=True, capture_output=True
        )
        if result.returncode != 0:
            # Try scheduled task
            result = subprocess.run(
                f'schtasks /run /tn "{SERVICE_NAME}"', shell=True, capture_output=True
            )
        return result.returncode == 0


def stop_service():
    """Stop the service."""
    nssm = find_nssm()
    if nssm:
        result = subprocess.run([nssm, "stop", SERVICE_NAME], capture_output=True)
        return result.returncode == 0
    else:
        result = subprocess.run(
            f'net stop "{SERVICE_NAME}"', shell=True, capture_output=True
        )
        return result.returncode == 0


def remove_service():
    """Remove the service."""
    nssm = find_nssm()
    if nssm:
        result = subprocess.run(
            [nssm, "remove", SERVICE_NAME, "confirm"], capture_output=True
        )
        return result.returncode == 0
    else:
        result = subprocess.run(
            f'schtasks /delete /tn "{SERVICE_NAME}" /f', shell=True, capture_output=True
        )
        return result.returncode == 0


def get_status():
    """Get service status."""
    nssm = find_nssm()
    if nssm:
        result = subprocess.run(
            [nssm, "status", SERVICE_NAME], capture_output=True, text=True
        )
        output = result.stdout.strip()
        if "SERVICE_RUNNING" in output:
            return "running"
        elif "SERVICE_STOPPED" in output:
            return "stopped"
        return "unknown"
    else:
        result = subprocess.run(
            f'schtasks /query /tn "{SERVICE_NAME}" /fo csv /nh',
            shell=True, capture_output=True, text=True
        )
        if result.returncode == 0 and "Running" in result.stdout:
            return "running"
        return "stopped"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python service_manager.py [install|start|stop|remove|status]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "install":
        python_exe = sys.argv[2] if len(sys.argv) > 2 else sys.executable
        project_dir = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()
        manage_py = os.path.join(project_dir, "manage.py")
        port = sys.argv[4] if len(sys.argv) > 4 else "8000"
        bind = sys.argv[5] if len(sys.argv) > 5 else "0.0.0.0"

        success, msg = install_service(python_exe, manage_py, project_dir, port, bind)
        print(msg)
        sys.exit(0 if success else 1)

    elif command == "start":
        success = start_service()
        print("Servicio iniciado" if success else "Error al iniciar")
        sys.exit(0 if success else 1)

    elif command == "stop":
        success = stop_service()
        print("Servicio detenido" if success else "Error al detener")
        sys.exit(0 if success else 1)

    elif command == "remove":
        success = remove_service()
        print("Servicio eliminado" if success else "Error al eliminar")
        sys.exit(0 if success else 1)

    elif command == "status":
        status = get_status()
        print(f"Estado: {status}")
        sys.exit(0)

    else:
        print(f"Comando desconocido: {command}")
        sys.exit(1)
