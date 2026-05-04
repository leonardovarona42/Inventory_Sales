"""
Build script for the InventorySales installer.
Creates a single .exe with PyInstaller that bundles the entire project.

Usage:
    python build_installer.py

Requires:
    pip install pyinstaller pywin32
"""
import os
import sys
import shutil
import zipfile
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
DEPLOY_DIR = Path(__file__).parent
BUILD_DIR = Path(__file__).parent / "build_output"
DIST_DIR = Path(__file__).parent / "dist"


def clean():
    """Remove previous build artifacts."""
    for d in [BUILD_DIR, DIST_DIR]:
        if d.exists():
            try:
                shutil.rmtree(d)
            except PermissionError:
                # Files might be locked, skip and overwrite
                pass
    spec_file = DEPLOY_DIR / "setup_wizard.spec"
    if spec_file.exists():
        try:
            spec_file.unlink()
        except PermissionError:
            pass


def create_project_zip():
    """Zip the project files + pip packages + launcher to bundle with the installer."""
    print("[1/4] Creando archivo del proyecto...")
    zip_path = BUILD_DIR / "project_data.zip"

    exclude_dirs = {
        '__pycache__', '.git', 'venv', '.venv', 'node_modules',
        '.vercel', 'deploy', 'build_output', 'dist', 'staticfiles',
        '.pytest_cache', '.mypy_cache', 'htmlcov',
    }
    exclude_files = {
        '.env', '*.log', '*.pyc', '*.pyo', 'Thumbs.db',
    }

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add project files
        for item in PROJECT_ROOT.iterdir():
            if item.name in exclude_dirs:
                continue
            if item.is_file() and any(item.match(p) for p in exclude_files):
                continue
            if item.is_dir():
                for root, dirs, files in os.walk(item):
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    for file in files:
                        file_path = Path(root) / file
                        if any(file_path.match(p) for p in exclude_files):
                            continue
                        arcname = file_path.relative_to(PROJECT_ROOT)
                        zf.write(file_path, arcname)
            elif item.is_file():
                # Root-level files (manage.py, requirements.txt, etc.)
                zf.write(item, item.name)

        # Add pip_packages (offline dependencies)
        pip_dir = DEPLOY_DIR / "pip_packages"
        if pip_dir.exists():
            print(f"  Agregando {len(list(pip_dir.glob('*.whl')))} paquetes pip...")
            for whl in pip_dir.glob("*.whl"):
                zf.write(whl, f"pip_packages/{whl.name}")

        # Add launcher.exe
        launcher = DIST_DIR / "MiNegocio-Launcher.exe"
        if launcher.exists():
            zf.write(launcher, "MiNegocio-Launcher.exe")
            print("  Launcher incluido")

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"  Proyecto empaquetado: {zip_path} ({size_mb:.1f} MB)")
    return zip_path


def build_installer_exe():
    """Build the installer executable with PyInstaller."""
    print("[2/4] Compilando instalador con PyInstaller...")

    # Use forward slashes to avoid escape issues
    deploy_str = str(DEPLOY_DIR).replace('\\', '/')
    build_str = str(BUILD_DIR).replace('\\', '/')
    dist_str = str(DIST_DIR).replace('\\', '/')

    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{deploy_str}/setup_wizard.py'],
    pathex=['{deploy_str}'],
    binaries=[],
    datas=[
        ('{build_str}/project_data.zip', '.'),
    ],
    hiddenimports=['psycopg2', 'psycopg2.extensions'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter.test', 'matplotlib', 'numpy', 'scipy'],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MiNegocio-Instalador',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''

    spec_file = DEPLOY_DIR / "setup_wizard.spec"
    with open(spec_file, 'w') as f:
        f.write(spec_content)

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        str(spec_file),
        '--distpath', dist_str,
        '--workpath', build_str,
        '--clean',
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: PyInstaller fallo")
        print(result.stderr)
        return False

    print(f"  Instalador compilado: {DIST_DIR}")
    return True


def build_launcher_exe():
    """Build the launcher executable."""
    print("[3/4] Compilando launcher...")

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        str(DEPLOY_DIR / 'launcher.py'),
        '--onefile',
        '--windowed',
        '--name', 'MiNegocio-Launcher',
        '--distpath', str(DIST_DIR),
        '--workpath', str(BUILD_DIR / 'launcher'),
        '--clean',
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  WARNING: Launcher no se compilo: {result.stderr[:200]}")
    else:
        print(f"  Launcher compilado")


def package_final():
    """Create final distribution package."""
    print("[4/4] Empaquetando distribucion final...")

    # Copy launcher if built
    launcher_src = DIST_DIR / "MiNegocio-Launcher.exe"
    if launcher_src.exists():
        print("  Launcher incluido")

    # Create a zip of everything
    installer_exe = DIST_DIR / "MiNegocio-Instalador.exe"
    if installer_exe.exists():
        size_mb = installer_exe.stat().st_size / (1024 * 1024)
        print(f"\n{'='*50}")
        print(f"DISTRIBUCION LISTA")
        print(f"{'='*50}")
        print(f"  Instalador: {installer_exe}")
        print(f"  Tamano: {size_mb:.1f} MB")
        print(f"\nInstrucciones de instalacion en PC del cliente:")
        print(f"  1. Instalar Python 3.13 desde python.org")
        print(f"  2. Instalar PostgreSQL")
        print(f"  3. Copiar el .exe a la PC del cliente")
        print(f"  4. Ejecutar MiNegocio-Instalador.exe como Administrador")
        print(f"  5. Seguir el asistente de instalacion")
        print(f"{'='*50}")


def main():
    print("=" * 50)
    print("BUILD - MiNegocio Instalador")
    print("=" * 50)

    # Ensure directories
    BUILD_DIR.mkdir(exist_ok=True)
    DIST_DIR.mkdir(exist_ok=True)

    clean()
    BUILD_DIR.mkdir(exist_ok=True)

    build_launcher_exe()
    create_project_zip()
    build_installer_exe()
    package_final()


if __name__ == "__main__":
    main()
