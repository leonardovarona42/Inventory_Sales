"""
Build script for KeyManagement (license generator desktop app).

Usage:
    python build_keygen.py
"""
import os
import sys
import subprocess
from pathlib import Path


KM_DIR = Path(__file__).parent.parent.parent / "KeyManagement"
DIST_DIR = Path(__file__).parent / "dist"


def build_keygen():
    """Build KeyManagement as a standalone .exe."""
    print("=" * 50)
    print("BUILD - KeyManagement (Generador de Licencias)")
    print("=" * 50)

    DIST_DIR.mkdir(exist_ok=True)

    # Use forward slashes and proper Windows separator for --add-data
    sep = ";"
    km_str = str(KM_DIR).replace('\\', '/')

    cmd = [
        sys.executable, '-m', 'PyInstaller',
        str(KM_DIR / 'main.py'),
        '--onefile',
        '--windowed',
        '--name', 'KeyManagement',
        '--distpath', str(DIST_DIR),
        '--workpath', str(Path(__file__).parent / 'build_output' / 'keygen'),
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'tkinter.scrolledtext',
        '--hidden-import', 'tkinter.messagebox',
        '--hidden-import', 'tkinter.filedialog',
        '--clean',
    ]

    print("Compilando KeyManagement...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return False

    exe_path = DIST_DIR / "KeyManagement.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n{'='*50}")
        print(f"KEYMANAGEMENT LISTO")
        print(f"{'='*50}")
        print(f"  Ejecutable: {exe_path}")
        print(f"  Tamano: {size_mb:.1f} MB")
        print(f"\nInstrucciones:")
        print(f"  1. Copie KeyManagement.exe a su PC")
        print(f"  2. Cree un archivo .env junto al .exe con:")
        print(f"     LICENSE_SECRET=<tu clave secreta>")
        print(f"     EMISOR_NOMBRE=<tu nombre>")
        print(f"     EMISOR_CI=<tu CI>")
        print(f"  3. Ejecute KeyManagement.exe")
        print(f"{'='*50}")
    else:
        print("ERROR: No se encontro el ejecutable")
        return False

    return True


if __name__ == "__main__":
    build_keygen()
