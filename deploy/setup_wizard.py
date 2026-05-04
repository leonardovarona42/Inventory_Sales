"""
Setup Wizard - Installer GUI for InventorySales.
Entry point for the installer executable.
"""
import os
import sys
import subprocess
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
import threading
import json
import time
import winreg


# Determine if running as PyInstaller bundle
def is_frozen():
    return getattr(sys, 'frozen', False)


def get_python_exe():
    """Get the system Python executable path (works in frozen mode)."""
    if not is_frozen():
        return sys.executable
    candidates = [
        r"C:\Users\SysAdmin\AppData\Local\Programs\Python\Python313\python.exe",
        r"C:\Python313\python.exe",
        r"C:\Program Files\Python313\python.exe",
        r"C:\Program Files (x86)\Python313\python.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def get_bundle_dir():
    """Get the directory where bundled data files are located."""
    if is_frozen():
        # PyInstaller extracts bundled data to _MEIPASS
        return Path(getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)))
    # In dev mode, the zip is in deploy/build_output/
    return Path(__file__).parent / "build_output"


INSTALL_DIR_DEFAULT = "C:\\MiNegocio"
SERVICE_NAME = "MiNegocioServer"
SUPERUSER_USERNAME = "leonardo.varona"
SUPERUSER_EMAIL = "leonardovarona42@gmail.com"
SUPERUSER_PASSWORD = "00020875302"


# Modern color palette
COLORS = {
    "primary": "#6366f1",
    "primary_dark": "#4f46e5",
    "primary_light": "#818cf8",
    "primary_bg": "#eef2ff",
    "success": "#10b981",
    "success_bg": "#d1fae5",
    "error": "#ef4444",
    "error_bg": "#fee2e2",
    "warning": "#f59e0b",
    "warning_bg": "#fef3c7",
    "surface": "#ffffff",
    "surface_alt": "#f8fafc",
    "border": "#e2e8f0",
    "text_primary": "#0f172a",
    "text_secondary": "#475569",
    "text_muted": "#94a3b8",
    "bg": "#f1f5f9",
}


class SetupWizard:
    def __init__(self, root):
        self.root = root
        self.root.title("MiNegocio - Instalador")
        self.root.geometry("780x600")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg"])

        # Custom styling
        self._apply_styles()

        self.step = 0
        self.config = {
            "install_dir": INSTALL_DIR_DEFAULT,
            "cliente_nombre": "",
            "db_host": "localhost",
            "db_port": "5432",
            "db_name": "inventory_sales",
            "db_user": "postgres",
            "db_password": "",
            "license_key": "",
            "license_later": False,
            "allowed_hosts": "localhost,127.0.0.1,*",
            "port": "8000",
            "bind_address": "0.0.0.0",
            "csrf_origins": "http://localhost:8000,http://127.0.0.1:8000",
        }

        self._setup_ui()
        self._show_step()

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("TProgressbar",
                       troughcolor=COLORS["border"],
                       background=COLORS["primary"],
                       borderwidth=0,
                       thickness=8)

        style.configure("Primary.TButton",
                       background=COLORS["primary"],
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none",
                       padding=(20, 10))
        style.map("Primary.TButton",
                 background=[("active", COLORS["primary_dark"]),
                            ("pressed", COLORS["primary_dark"])])

        style.configure("Secondary.TButton",
                       background=COLORS["surface"],
                       foreground=COLORS["text_secondary"],
                       borderwidth=1,
                       focuscolor="none",
                       padding=(20, 10),
                       relief="flat")
        style.map("Secondary.TButton",
                 background=[("active", COLORS["surface_alt"])])

        style.configure("Success.TButton",
                       background=COLORS["success"],
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none",
                       padding=(20, 10))
        style.map("Success.TButton",
                 background=[("active", "#059669")])

        style.configure("Card.TFrame",
                       background=COLORS["surface"],
                       borderwidth=0)

        style.configure("TRadiobutton",
                       background=COLORS["surface"],
                       foreground=COLORS["text_primary"],
                       indicatorbackground=COLORS["surface"],
                       indicatorforeground=COLORS["primary"])

        style.configure("TCheckbutton",
                       background=COLORS["surface"],
                       foreground=COLORS["text_primary"])

        style.configure("Header.TLabel",
                       background=COLORS["primary"],
                       foreground="white",
                       font=("Segoe UI", 16, "bold"))

        style.configure("TLabel",
                       background=COLORS["surface"],
                       foreground=COLORS["text_primary"])

    def _setup_ui(self):
        # Header with gradient effect
        header = tk.Frame(self.root, bg=COLORS["primary"], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="MiNegocio", font=("Segoe UI", 18, "bold"),
                 bg=COLORS["primary"], fg="white").pack(side=tk.LEFT, padx=25, pady=15)
        tk.Label(header, text="Instalador del Sistema", font=("Segoe UI", 12),
                 bg=COLORS["primary"], fg=COLORS["primary_light"]).pack(side=tk.LEFT, pady=18)

        # Step indicators
        steps_frame = tk.Frame(self.root, bg=COLORS["bg"], height=40)
        steps_frame.pack(fill=tk.X, padx=30, pady=(15, 5))
        steps_frame.pack_propagate(False)

        self.step_indicators = []
        self.step_labels = []
        step_names = ["Inicio", "Directorio", "BD", "Red", "Licencia", "Instalar", "Fin"]

        for i, name in enumerate(step_names):
            frame = tk.Frame(steps_frame, bg=COLORS["bg"])
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Circle
            circle = tk.Canvas(frame, width=24, height=24, bg=COLORS["bg"],
                              highlightthickness=0)
            circle.place(relx=0.5, rely=0.1, anchor="n")
            self.step_indicators.append(circle)

            # Label
            label = tk.Label(frame, text=name, font=("Segoe UI", 8),
                           bg=COLORS["bg"], fg=COLORS["text_muted"])
            label.place(relx=0.5, rely=0.65, anchor="n")
            self.step_labels.append(label)

            # Connector line
            if i < len(step_names) - 1:
                line = tk.Canvas(frame, height=2, bg=COLORS["bg"],
                                highlightthickness=0, width=30)
                line.place(relx=0.95, rely=0.35, anchor="e")

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.root, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=30, pady=(5, 10))

        # Content area with card style
        card = tk.Frame(self.root, bg=COLORS["surface"], bd=0, relief=tk.FLAT)
        card.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 10))

        self.content_frame = card

        # Navigation buttons
        btn_frame = tk.Frame(self.root, bg=COLORS["bg"])
        btn_frame.pack(fill=tk.X, padx=30, pady=(0, 20))

        self.btn_back = tk.Button(btn_frame, text="← Atras", command=self._prev_step,
                                  bg=COLORS["surface"], fg=COLORS["text_secondary"],
                                  font=("Segoe UI", 10, "bold"),
                                  bd=1, relief=tk.FLAT,
                                  width=14, cursor="hand2",
                                  activebackground=COLORS["surface_alt"])
        self.btn_back.pack(side=tk.LEFT)
        self.btn_back.config(state=tk.DISABLED)

        self.btn_next = tk.Button(btn_frame, text="Siguiente →", command=self._next_step,
                                  bg=COLORS["primary"], fg="white",
                                  font=("Segoe UI", 10, "bold"),
                                  bd=0, relief=tk.FLAT,
                                  width=16, cursor="hand2",
                                  activebackground=COLORS["primary_dark"])
        self.btn_next.pack(side=tk.RIGHT)

    def _update_progress(self):
        total = 6
        self.progress_bar['value'] = (self.step / total) * 100

        for i, (circle, label) in enumerate(zip(self.step_indicators, self.step_labels)):
            if i <= self.step:
                circle.delete("all")
                circle.create_oval(2, 2, 22, 22, fill=COLORS["primary"], outline=COLORS["primary"])
                if i < self.step:
                    circle.create_text(12, 12, text="✓", fill="white", font=("Segoe UI", 10, "bold"))
                elif i == self.step:
                    circle.create_text(12, 12, text=str(i + 1), fill="white", font=("Segoe UI", 9, "bold"))
                label.config(fg=COLORS["text_primary"], font=("Segoe UI", 8, "bold"))
            else:
                circle.delete("all")
                circle.create_oval(2, 2, 22, 22, fill=COLORS["border"], outline=COLORS["border"])
                circle.create_text(12, 12, text=str(i + 1), fill=COLORS["text_muted"], font=("Segoe UI", 9))
                label.config(fg=COLORS["text_muted"], font=("Segoe UI", 8))

    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _show_step(self):
        self._clear_content()
        self._update_progress()

        if self.step == 0:
            self._step_welcome()
        elif self.step == 1:
            self._step_install_dir()
        elif self.step == 2:
            self._step_db_config()
        elif self.step == 3:
            self._step_network()
        elif self.step == 4:
            self._step_license()
        elif self.step == 5:
            self._step_install()
        elif self.step == 6:
            self._step_finish()

    def _create_card_section(self, parent, title, description=""):
        """Create a card-style section with title and optional description."""
        frame = tk.Frame(parent, bg=COLORS["surface"])
        frame.pack(fill=tk.X, padx=30, pady=15)

        tk.Label(frame, text=title, font=("Segoe UI", 14, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text_primary"]).pack(anchor=tk.W)

        if description:
            tk.Label(frame, text=description, font=("Segoe UI", 10),
                     bg=COLORS["surface"], fg=COLORS["text_secondary"],
                     justify=tk.LEFT).pack(anchor=tk.W, pady=(2, 0))

        return frame

    def _create_input_row(self, parent, label_text, var, width=40, show=None, hint=""):
        """Create a modern input row."""
        row = tk.Frame(parent, bg=COLORS["surface"])
        row.pack(fill=tk.X, pady=4)

        tk.Label(row, text=label_text, bg=COLORS["surface"],
                 font=("Segoe UI", 10, "bold"), fg=COLORS["text_secondary"],
                 width=14, anchor=tk.W).pack(side=tk.LEFT)

        entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10),
                        width=width, show=show, bd=1, relief=tk.SOLID,
                        bg=COLORS["surface_alt"], fg=COLORS["text_primary"])
        entry.pack(side=tk.LEFT, padx=10)

        # Focus effects
        entry.bind("<FocusIn>", lambda e: entry.config(bd=2, highlightbackground=COLORS["primary"]))
        entry.bind("<FocusOut>", lambda e: entry.config(bd=1, highlightbackground=COLORS["border"]))

        if hint:
            tk.Label(row, text=hint, bg=COLORS["surface"],
                     font=("Segoe UI", 8), fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=5)

        return entry

    def _step_welcome(self):
        frame = tk.Frame(self.content_frame, bg=COLORS["surface"])
        frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Icon
        icon_canvas = tk.Canvas(frame, width=64, height=64, bg=COLORS["surface"],
                               highlightthickness=0)
        icon_canvas.pack(pady=(10, 15))
        icon_canvas.create_oval(4, 4, 60, 60, fill=COLORS["primary_bg"], outline=COLORS["primary"], width=2)
        icon_canvas.create_text(32, 32, text="📦", font=("Segoe UI Emoji", 28))

        tk.Label(frame, text="Bienvenido al Instalador", font=("Segoe UI", 20, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text_primary"]).pack(pady=(0, 8))

        tk.Label(frame, text="Este asistente instalara el Sistema de Gestion de Inventario y Ventas.\n"
                 "Se configurara automaticamente como un servicio de Windows.",
                 font=("Segoe UI", 11), bg=COLORS["surface"], fg=COLORS["text_secondary"],
                 justify=tk.CENTER).pack(pady=(0, 20))

        # Requirements card
        req_frame = tk.LabelFrame(frame, text="  Requisitos previos  ", bg=COLORS["surface"],
                                  fg=COLORS["text_primary"],
                                  font=("Segoe UI", 10, "bold"), padx=20, pady=15,
                                  relief=tk.FLAT, bd=0)
        req_frame.configure(highlightbackground=COLORS["border"], highlightthickness=1)
        req_frame.pack(fill=tk.X, pady=10)

        py_ok = self._check_python()

        items = [
            ("Python 3.13", "Detectado" if py_ok else "No detectado", py_ok),
            ("PostgreSQL", "Verifique que el servicio este corriendo", True),
        ]

        for name, status, ok in items:
            item_frame = tk.Frame(req_frame, bg=COLORS["surface"])
            item_frame.pack(fill=tk.X, pady=4)

            status_icon = "✅" if ok else "⚠️"
            status_color = COLORS["success"] if ok else COLORS["warning"]

            tk.Label(item_frame, text=status_icon, bg=COLORS["surface"], font=("Segoe UI", 12)).pack(side=tk.LEFT)
            tk.Label(item_frame, text=name, bg=COLORS["surface"],
                     font=("Segoe UI", 10, "bold"), fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=8)
            tk.Label(item_frame, text=status, bg=COLORS["surface"],
                     font=("Segoe UI", 9), fg=status_color).pack(side=tk.LEFT)

    def _check_python(self):
        try:
            if is_frozen():
                # Check via Windows registry
                paths_to_check = [
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Python\PythonCore\3.13\InstallPath"),
                    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Python\PythonCore\3.13\InstallPath"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Python\PythonCore\3.12\InstallPath"),
                    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Python\PythonCore\3.12\InstallPath"),
                ]
                for hive, path in paths_to_check:
                    try:
                        key = winreg.OpenKey(hive, path)
                        winreg.QueryValueEx(key, "")
                        winreg.CloseKey(key)
                        return True
                    except Exception:
                        pass
                return False

            result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
            return '3.13' in result.stdout or '3.12' in result.stdout
        except Exception:
            return False

    def _step_install_dir(self):
        self._create_card_section(self.content_frame,
                                  "Directorio de Instalacion",
                                  "Seleccione donde se instalara el sistema.")

        frame = tk.Frame(self.content_frame, bg=COLORS["surface"])
        frame.pack(fill=tk.X, padx=40, pady=10)

        self.dir_var = tk.StringVar(value=self.config["install_dir"])

        row = tk.Frame(frame, bg=COLORS["surface"])
        row.pack(fill=tk.X, pady=10)

        tk.Entry(row, textvariable=self.dir_var, font=("Segoe UI", 10),
                 width=45, bd=1, relief=tk.SOLID, bg=COLORS["surface_alt"]).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(row, text="📁 Examinar...", command=self._browse_dir,
                  bg=COLORS["surface"], fg=COLORS["text_secondary"],
                  font=("Segoe UI", 9), bd=1, relief=tk.SOLID,
                  cursor="hand2", activebackground=COLORS["surface_alt"]).pack(side=tk.LEFT)

        tk.Label(frame, text="Se creara una carpeta con todos los archivos del sistema.",
                 bg=COLORS["surface"], fg=COLORS["text_muted"],
                 font=("Segoe UI", 9)).pack(anchor=tk.W, pady=5)

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir="C:\\")
        if d:
            self.config["install_dir"] = os.path.join(d, "MiNegocio")
            self.dir_var.set(self.config["install_dir"])

    def _step_db_config(self):
        self._create_card_section(self.content_frame,
                                  "Configuracion de Base de Datos",
                                  "Ingrese los datos de conexion a PostgreSQL.")

        frame = tk.Frame(self.content_frame, bg=COLORS["surface"])
        frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=5)

        fields = [
            ("Host:", "db_host", "localhost"),
            ("Puerto:", "db_port", "5432"),
            ("Nombre BD:", "db_name", "inventory_sales"),
            ("Usuario:", "db_user", "postgres"),
            ("Contrasena:", "db_password", ""),
        ]

        self.db_vars = {}
        for label, key, default in fields:
            var = tk.StringVar(value=self.config.get(key, default))
            self.db_vars[key] = var
            show_char = "*" if key == "db_password" else None
            self._create_input_row(frame, label, var, width=35, show=show_char)

        # Test button
        btn_row = tk.Frame(frame, bg=COLORS["surface"])
        btn_row.pack(fill=tk.X, pady=15)

        tk.Button(btn_row, text="🔌 Probar Conexion", command=self._test_db,
                  bg=COLORS["success"], fg="white",
                  font=("Segoe UI", 10, "bold"), bd=0, relief=tk.FLAT,
                  width=20, cursor="hand2",
                  activebackground="#059669").pack(side=tk.LEFT)

        self.db_status = tk.Label(btn_row, text="", bg=COLORS["surface"],
                                  font=("Segoe UI", 10), fg=COLORS["text_secondary"])
        self.db_status.pack(side=tk.LEFT, padx=15)

        self.db_tested = False

    def _test_db(self):
        host = self.db_vars["db_host"].get()
        port = self.db_vars["db_port"].get()
        name = self.db_vars["db_name"].get()
        user = self.db_vars["db_user"].get()
        password = self.db_vars["db_password"].get()

        self.db_status.config(text="Conectando...", fg=COLORS["warning"])
        self.root.update()

        # Test using subprocess with system python + psycopg2
        # This avoids issues with bundled psycopg2 in frozen exe
        test_script = f"""
import sys
try:
    import psycopg2
    conn = psycopg2.connect(
        host='{host}', port={port}, dbname='{name}',
        user='{user}', password='{password}', connect_timeout=5
    )
    conn.close()
    print("OK")
except ImportError:
    print("NO_PSYCOPG2")
except Exception as e:
    print(f"ERROR: {{e}}")
"""
        try:
            python_path = get_python_exe()
            if python_path:
                result = subprocess.run(
                    [python_path, "-c", test_script],
                    capture_output=True, text=True, timeout=10
                )
                output = result.stdout.strip()

                if output == "OK":
                    self.db_status.config(text="✅ Conexion exitosa!", fg=COLORS["success"])
                    self.db_tested = True
                    for key, var in self.db_vars.items():
                        self.config[key] = var.get()
                elif "NO_PSYCOPG2" in output:
                    self.db_status.config(text="⚠️ psycopg2 no instalado, se hara durante la instalacion",
                                         fg=COLORS["warning"])
                    self.db_tested = True
                    for key, var in self.db_vars.items():
                        self.config[key] = var.get()
                else:
                    err_msg = output.replace("ERROR: ", "")[:60]
                    self.db_status.config(text=f"❌ {err_msg}", fg=COLORS["error"])
                    self.db_tested = False
            else:
                # No python found, fallback to skip
                self.db_status.config(text="⚠️ Python no detectado, se verificara durante la instalacion",
                                     fg=COLORS["warning"])
                self.db_tested = True
                for key, var in self.db_vars.items():
                    self.config[key] = var.get()

        except subprocess.TimeoutExpired:
            self.db_status.config(text="❌ Timeout - PostgreSQL no responde", fg=COLORS["error"])
            self.db_tested = False
        except Exception as e:
            self.db_status.config(text=f"⚠️ {str(e)[:40]}", fg=COLORS["warning"])
            self.db_tested = True
            for key, var in self.db_vars.items():
                self.config[key] = var.get()

    def _step_network(self):
        self._create_card_section(self.content_frame,
                                  "Configuracion de Red",
                                  "Configure como se accedera al sistema desde la red.")

        frame = tk.Frame(self.content_frame, bg=COLORS["surface"])
        frame.pack(fill=tk.X, padx=40, pady=5)

        # Bind address
        bind_frame = tk.Frame(frame, bg=COLORS["surface"])
        bind_frame.pack(fill=tk.X, pady=10)

        tk.Label(bind_frame, text="Direccion:", bg=COLORS["surface"],
                 font=("Segoe UI", 10, "bold"), fg=COLORS["text_secondary"],
                 width=12, anchor=tk.W).pack(side=tk.LEFT)

        self.bind_var = tk.StringVar(value="0.0.0.0")
        ttk.Radiobutton(bind_frame, text="Todas (0.0.0.0) - Acceso en red",
                        variable=self.bind_var, value="0.0.0.0").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(bind_frame, text="Solo local (127.0.0.1)",
                        variable=self.bind_var, value="127.0.0.1").pack(side=tk.LEFT)

        # Port
        port_frame = tk.Frame(frame, bg=COLORS["surface"])
        port_frame.pack(fill=tk.X, pady=8)
        tk.Label(port_frame, text="Puerto:", bg=COLORS["surface"],
                 font=("Segoe UI", 10, "bold"), fg=COLORS["text_secondary"],
                 width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value="8000")
        tk.Entry(port_frame, textvariable=self.port_var, font=("Segoe UI", 10),
                 width=10, bd=1, relief=tk.SOLID, bg=COLORS["surface_alt"]).pack(side=tk.LEFT, padx=10)

        # Allowed hosts
        hosts_frame = tk.Frame(frame, bg=COLORS["surface"])
        hosts_frame.pack(fill=tk.X, pady=8)
        tk.Label(hosts_frame, text="Allowed Hosts:", bg=COLORS["surface"],
                 font=("Segoe UI", 10, "bold"), fg=COLORS["text_secondary"],
                 width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.hosts_var = tk.StringVar(value="localhost,127.0.0.1,*")
        tk.Entry(hosts_frame, textvariable=self.hosts_var, font=("Segoe UI", 10),
                 width=40, bd=1, relief=tk.SOLID, bg=COLORS["surface_alt"]).pack(side=tk.LEFT, padx=10)

        # CSRF origins
        origins_frame = tk.Frame(frame, bg=COLORS["surface"])
        origins_frame.pack(fill=tk.X, pady=8)
        tk.Label(origins_frame, text="CSRF Origins:", bg=COLORS["surface"],
                 font=("Segoe UI", 10, "bold"), fg=COLORS["text_secondary"],
                 width=12, anchor=tk.W).pack(side=tk.LEFT)
        self.origins_var = tk.StringVar(value="http://localhost:8000,http://127.0.0.1:8000")
        tk.Entry(origins_frame, textvariable=self.origins_var, font=("Segoe UI", 10),
                 width=40, bd=1, relief=tk.SOLID, bg=COLORS["surface_alt"]).pack(side=tk.LEFT, padx=10)

        # Info box
        info_frame = tk.Frame(frame, bg=COLORS["primary_bg"], bd=0, relief=tk.FLAT)
        info_frame.pack(fill=tk.X, pady=15)
        info_frame.configure(highlightbackground=COLORS["primary_light"], highlightthickness=1)

        tk.Label(info_frame, text="💡 Para acceso en red use 0.0.0.0 y agregue la IP del servidor\n"
                 "   a Allowed Hosts. Ej: localhost,127.0.0.1,192.168.1.100",
                 bg=COLORS["primary_bg"], fg=COLORS["primary_dark"],
                 font=("Segoe UI", 9), justify=tk.LEFT).pack(padx=15, pady=10, anchor=tk.W)

    def _step_license(self):
        self._create_card_section(self.content_frame,
                                  "Activacion de Licencia",
                                  "Introduzca la clave proporcionada por su proveedor.")

        frame = tk.Frame(self.content_frame, bg=COLORS["surface"])
        frame.pack(fill=tk.X, padx=40, pady=5)

        self.license_text = tk.Text(frame, width=50, height=4,
                                    font=("Consolas", 10), bd=1, relief=tk.SOLID,
                                    bg=COLORS["surface_alt"], fg=COLORS["text_primary"])
        self.license_text.pack(fill=tk.X, pady=10)
        self.license_text.insert("1.0", "LIC-")

        # Skip option
        self.skip_var = tk.BooleanVar(value=False)
        tk.Checkbutton(frame, text="Activar licencia despues (el sistema se bloqueara)",
                       variable=self.skip_var, bg=COLORS["surface"],
                       font=("Segoe UI", 10), fg=COLORS["text_secondary"],
                       command=self._toggle_license_skip,
                       activebackground=COLORS["surface"]).pack(anchor=tk.W, pady=5)

    def _toggle_license_skip(self):
        state = tk.DISABLED if self.skip_var.get() else tk.NORMAL
        self.license_text.config(state=state)

    def _step_install(self):
        frame = tk.Frame(self.content_frame, bg=COLORS["surface"])
        frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        tk.Label(frame, text="Instalando Sistema...", font=("Segoe UI", 14, "bold"),
                 bg=COLORS["surface"], fg=COLORS["text_primary"]).pack(pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(frame, width=70, height=18,
                                                   font=("Consolas", 9), bd=1, relief=tk.SOLID,
                                                   bg=COLORS["surface_alt"], fg=COLORS["text_primary"])
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.btn_next.config(state=tk.DISABLED)
        self.btn_back.config(state=tk.DISABLED)

        threading.Thread(target=self._run_installation, daemon=True).start()

    def _log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        # Also write to install log file
        install_dir = self.config["install_dir"]
        log_file = os.path.join(install_dir, "install.log")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] {message}\n")
        except Exception:
            pass
        self.root.update()

    def _run_installation(self):
        install_dir = self.config["install_dir"]
        venv_path = os.path.join(install_dir, "venv")
        project_dir = install_dir  # manage.py is at install root, not in subfolder
        install_log = os.path.join(install_dir, "install.log")

        try:
            self._log("[1/8] Creando directorio...")
            os.makedirs(install_dir, exist_ok=True)

            self._log("[2/8] Copiando archivos...")
            if is_frozen():
                self._extract_bundle(install_dir)
            else:
                self._copy_project(Path(__file__).parent.parent, install_dir)

            self._log("[3/8] Creando entorno virtual...")
            python_path = get_python_exe()
            if python_path:
                subprocess.run([python_path, "-m", "venv", venv_path],
                              check=True, capture_output=True)
            else:
                subprocess.run(['py', '-3', '-m', 'venv', venv_path],
                              check=True, capture_output=True)

            python_exe = os.path.join(venv_path, "Scripts", "python.exe")
            pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")

            self._log("[4/8] Instalando dependencias (offline)...")
            req_file = os.path.join(project_dir, "requirements.txt")
            pip_dir = os.path.join(install_dir, "pip_packages")

            # Kill any lingering python processes that might lock .pyd files
            subprocess.run('taskkill /F /IM python.exe /FI "STATUS eq UNKNOWN"', shell=True, capture_output=True)
            import time
            time.sleep(2)

            # Delete problematic .pyd files that often get locked
            site_pkgs = os.path.join(venv_path, "Lib", "site-packages")
            if os.path.exists(site_pkgs):
                for root, dirs, files in os.walk(site_pkgs):
                    for f in files:
                        if f.endswith('.pyd'):
                            try:
                                os.remove(os.path.join(root, f))
                            except Exception:
                                pass

            pip_ok = False
            for attempt in range(3):
                if attempt > 0:
                    self._log(f"  Reintento {attempt + 1}/3...")
                    time.sleep(2)
                    extra_args = ["--force-reinstall", "--no-cache-dir"]
                else:
                    extra_args = []

                if os.path.exists(pip_dir) and len(os.listdir(pip_dir)) > 0:
                    self._log(f"  Instalando desde {len(os.listdir(pip_dir))} paquetes locales...")
                    cmd = [pip_exe, "install", "--no-index", "--find-links", pip_dir, "-r", req_file] + extra_args
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                else:
                    self._log("  ⚠️ Paquetes locales no encontrados, intentando descarga...")
                    cmd = [pip_exe, "install", "-r", req_file] + extra_args
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                if result.returncode == 0:
                    pip_ok = True
                    self._log("  ✅ Todas las dependencias instaladas")
                    break
                else:
                    error_msg = result.stderr.strip()[-200:]
                    self._log(f"  ⚠️ pip error: {error_msg}")

            if not pip_ok:
                self._log("\n❌ ERROR CRITICO: No se pudieron instalar las dependencias.")
                self._log("La instalacion no puede continuar.")
                self.btn_next.config(state=tk.NORMAL, command=self.root.destroy,
                                     text="Finalizar", bg=COLORS["error"])
                self.step = 6
                return

            self._log("[5/8] Configurando .env...")
            self._create_env_file(project_dir)

            self._log("[6/8] Ejecutando migraciones...")
            migrate_result = self._run_django_cmd_verbose(python_exe, project_dir, "migrate", "--verbosity", "2")
            if migrate_result:
                self._log("  ✅ Migraciones completadas")
            else:
                self._log("  ⚠️ Migraciones con warnings")

            self._log("[7/8] Creando administrador...")
            self._create_superuser(python_exe, project_dir)

            if self.config.get("license_key") and not self.config.get("license_later"):
                self._log("[8/9] Activando licencia...")
                self._activate_license(python_exe, project_dir, self.config["license_key"])
            else:
                self._log("[8/9] Licencia: activar mas tarde desde el sistema")

            self._log("[9/9] Configurando servicio Windows...")
            self._create_service(install_dir, venv_path, project_dir)

            self._create_desktop_shortcut(install_dir)

            self._log("")
            self._log("✅ INSTALACION COMPLETADA")
            self._log(f"📁 Directorio: {install_dir}")
            self._log(f"🌐 URL: http://localhost:{self.config['port']}")
            self._log("")
            self._log("⚠️ Credenciales de administrador guardadas de forma segura.")

        except Exception as e:
            self._log(f"\n❌ ERROR: {str(e)}")
            import traceback
            self._log(traceback.format_exc())
        finally:
            self.btn_next.config(state=tk.NORMAL, command=self.root.destroy,
                                 text="Finalizar ✓", bg=COLORS["success"])
            self.step = 7

    def _extract_bundle(self, install_dir):
        import zipfile
        bundle_dir = get_bundle_dir()
        bundle_zip = os.path.join(bundle_dir, "project_data.zip")

        if not os.path.exists(bundle_zip):
            try:
                contents = os.listdir(bundle_dir)
                raise RuntimeError(
                    f"No se encontraron datos del proyecto.\n"
                    f"Buscado en: {bundle_dir}\n"
                    f"Contenido: {', '.join(contents[:20])}"
                )
            except Exception:
                raise RuntimeError(f"No se encontraron datos del proyecto en {bundle_dir}")

        with zipfile.ZipFile(bundle_zip, 'r') as z:
            z.extractall(install_dir)

        # Fix corrupted empty __init__.py files (null bytes from zip)
        for root, dirs, files in os.walk(install_dir):
            for fname in files:
                if fname == '__init__.py':
                    fpath = os.path.join(root, fname)
                    with open(fpath, 'rb') as f:
                        content = f.read()
                    if b'\x00' in content or len(content.strip()) == 0:
                        with open(fpath, 'wb') as f:
                            f.write(b'# ')

        # Copy launcher.exe from bundle to install dir root
        launcher_in_zip = os.path.join(install_dir, "MiNegocio-Launcher.exe")
        if os.path.exists(launcher_in_zip):
            shutil.move(launcher_in_zip, os.path.join(install_dir, "MiNegocio_service.exe"))

    def _copy_project(self, source, dest):
        exclude = {'__pycache__', '.git', 'venv', 'node_modules', '.venv', 'deploy', 'staticfiles'}
        for item in source.iterdir():
            if item.name in exclude:
                continue
            dest_item = Path(dest) / item.name
            if item.is_dir():
                shutil.copytree(item, dest_item, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            else:
                shutil.copy2(item, dest_item)

    def _create_env_file(self, project_dir):
        env_content = f"""# Django settings
DJANGO_SECRET_KEY={self._generate_secret_key()}
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS={self.config['allowed_hosts']}
PORT={self.config['port']}

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME={self.config['db_name']}
DB_USER={self.config['db_user']}
DB_PASSWORD={self.config['db_password']}
DB_HOST={self.config['db_host']}
DB_PORT={self.config['db_port']}

# Security
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
CSRF_COOKIE_HTTPONLY=True
CSRF_TRUSTED_ORIGINS={self.config.get('csrf_origins', 'http://localhost:8000,http://127.0.0.1:8000')}

# Session
SESSION_COOKIE_AGE=3600
DJANGO_ALLOW_DEBUG_FALLBACK=True

# License
LICENSE_SECRET=a5887f7ced21082e5f10865dc59cb85857757dcabb8d9b4fd8eb3b34ae217d8c

# Upload limits
DATA_UPLOAD_MAX_MEMORY_SIZE=5242880

# Axes
AXES_ENABLED=True
AXES_FAILURE_LIMIT=5
AXES_COOLOFF_TIME=1
"""
        with open(os.path.join(project_dir, '.env'), 'w', encoding='utf-8') as f:
            f.write(env_content)

    def _generate_secret_key(self):
        import secrets
        return secrets.token_hex(32)

    def _run_django_cmd(self, python_exe, project_dir, cmd):
        manage_py = os.path.join(project_dir, 'manage.py')
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'Inventory_Sales.settings'
        env['PYTHONPATH'] = project_dir

        result = subprocess.run(
            [python_exe, manage_py, cmd],
            capture_output=True, text=True,
            cwd=project_dir, env=env
        )

        if result.stdout:
            self._log(f"  {result.stdout[:200]}")
        if result.returncode != 0 and result.stderr:
            self._log(f"  ⚠️ {result.stderr[:200]}")
        return result.returncode == 0

    def _run_django_cmd_verbose(self, python_exe, project_dir, cmd, *args):
        manage_py = os.path.join(project_dir, 'manage.py')
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'Inventory_Sales.settings'
        env['PYTHONPATH'] = project_dir

        cmd_args = [python_exe, manage_py, cmd] + list(args)
        result = subprocess.run(
            cmd_args,
            capture_output=True, text=True,
            cwd=project_dir, env=env, timeout=120
        )

        # Log the full output to see each migration applied
        for line in (result.stdout + result.stderr).splitlines():
            if line.strip():
                self._log(f"  {line}")

        return result.returncode == 0

    def _create_superuser(self, python_exe, project_dir):
        manage_py = os.path.join(project_dir, 'manage.py')
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'Inventory_Sales.settings'
        env['PYTHONPATH'] = project_dir

        script = f"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventory_Sales.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='{SUPERUSER_USERNAME}').exists():
    User.objects.create_superuser('{SUPERUSER_USERNAME}', '{SUPERUSER_EMAIL}', '{SUPERUSER_PASSWORD}')
    print('Superuser creado')
else:
    print('Ya existe')
"""
        result = subprocess.run(
            [python_exe, manage_py, 'shell', '-c', script],
            capture_output=True, text=True,
            cwd=project_dir, env=env
        )
        if result.stdout:
            self._log(f"  {result.stdout.strip()}")

    def _activate_license(self, python_exe, project_dir, license_key):
        manage_py = os.path.join(project_dir, 'manage.py')
        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = 'Inventory_Sales.settings'
        env['PYTHONPATH'] = project_dir

        # Escape single quotes in license key for the shell script
        safe_key = license_key.replace("'", "'\"'\"'")

        script = f"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Inventory_Sales.settings')
django.setup()
from licencias.services import activar_licencia
exito, mensaje, licencia = activar_licencia('{safe_key}')
if exito:
    print(f'Licencia activada: {{mensaje}}')
else:
    print(f'WARNING: {{mensaje}}')
"""
        result = subprocess.run(
            [python_exe, manage_py, 'shell', '-c', script],
            capture_output=True, text=True,
            cwd=project_dir, env=env
        )
        if result.stdout:
            self._log(f"  {result.stdout.strip()}")
        if result.returncode != 0:
            self._log(f"  ⚠️ Error activando: {result.stderr[:200]}")

    def _create_service(self, install_dir, venv_path, project_dir):
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
        manage_py = os.path.join(project_dir, "manage.py")

        bat_content = f"""@echo off
cd /d "{project_dir}"
set DJANGO_SETTINGS_MODULE=Inventory_Sales.settings
set PYTHONPATH={project_dir}
set PYTHONUNBUFFERED=1
"{python_exe}" "{manage_py}" runserver {self.config['bind_address']}:{self.config['port']} --noreload >> "{project_dir}\\service.log" 2>&1
"""
        bat_path = os.path.join(install_dir, "start_server.bat")
        with open(bat_path, 'w') as f:
            f.write(bat_content)

        # Use vbs to run batch hidden
        vbs_content = f"""Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "{bat_path}" & Chr(34), 0
Set WshShell = Nothing
"""
        vbs_path = os.path.join(install_dir, "start_server.vbs")
        with open(vbs_path, 'w') as f:
            f.write(vbs_content)

        stop_bat = os.path.join(install_dir, "stop_server.bat")
        with open(stop_bat, 'w') as f:
            f.write(f'@echo off\nfor /f "tokens=5" %%%%a in (\'netstat -ano ^| findstr ":{self.config["port"]}.*LISTENING"\') do taskkill /F /PID %%%%a 2>nul\n')

        # Create scheduled task to run on login
        task_cmd = (
            f'schtasks /create /tn "{SERVICE_NAME}" /tr "wscript.exe \\"{vbs_path}\\"" '
            f'/sc onlogon /rl highest /f'
        )
        result = subprocess.run(task_cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            self._log("  ✅ Servicio programado en inicio")
            # Start immediately
            subprocess.Popen(['wscript.exe', vbs_path], cwd=install_dir)
            self._log("  ✅ Servicio iniciado")
        else:
            self._log(f"  ⚠️ schtasks: {result.stderr.strip()}")
            self._log("  ⚠️ Usa el launcher para iniciar manualmente")

    def _create_desktop_shortcut(self, install_dir):
        try:
            desktop = subprocess.run(
                ['powershell', '-Command', '[Environment]::GetFolderPath("Desktop")'],
                capture_output=True, text=True
            ).stdout.strip()

            service_exe = os.path.join(install_dir, "MiNegocio_service.exe")

            ps_cmd = f"""
$WshShell = New-Object -comObject WScript.Shell

# Shortcut to service control
if (Test-Path "{service_exe}") {{
    $Shortcut = $WshShell.CreateShortcut("{desktop}\\MiNegocio Servicio.lnk")
    $Shortcut.TargetPath = "{service_exe}"
    $Shortcut.WorkingDirectory = "{install_dir}"
    $Shortcut.Description = "Iniciar o Detener el servicio MiNegocio"
    $Shortcut.Save()
}}

# Shortcut to web app
$Shortcut2 = $WshShell.CreateShortcut("{desktop}\\MiNegocio Web.lnk")
$Shortcut2.TargetPath = "http://localhost:{self.config['port']}"
$Shortcut2.Description = "Abrir MiNegocio en el navegador"
$Shortcut2.Save()
"""
            subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True)
            self._log("  ✅ Atajos de escritorio creados")
        except Exception as e:
            self._log(f"  ⚠️ Atajo: {e}")

    def _step_finish(self):
        frame = tk.Frame(self.content_frame, bg=COLORS["surface"])
        frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Success icon
        icon = tk.Canvas(frame, width=80, height=80, bg=COLORS["surface"], highlightthickness=0)
        icon.pack(pady=(10, 15))
        icon.create_oval(4, 4, 76, 76, fill=COLORS["success_bg"], outline=COLORS["success"], width=2)
        icon.create_text(40, 40, text="✓", fill=COLORS["success"], font=("Segoe UI", 36, "bold"))

        tk.Label(frame, text="Instalacion Completada", font=("Segoe UI", 20, "bold"),
                 bg=COLORS["surface"], fg=COLORS["success"]).pack(pady=(0, 5))

        tk.Label(frame, text="El sistema esta listo para usar.",
                 bg=COLORS["surface"], font=("Segoe UI", 12), fg=COLORS["text_secondary"]).pack(pady=(0, 20))

        # Access info card
        info_frame = tk.Frame(frame, bg=COLORS["primary_bg"], bd=0)
        info_frame.pack(fill=tk.X, pady=10)
        info_frame.configure(highlightbackground=COLORS["primary_light"], highlightthickness=1)

        info_frame_inner = tk.Frame(info_frame, bg=COLORS["primary_bg"])
        info_frame_inner.pack(padx=20, pady=15)

        info_items = [
            ("🌐 URL local:", f"http://localhost:{self.config['port']}"),
            ("🌐 URL red:", f"http://<IP-servidor>:{self.config['port']}"),
        ]

        for label, value in info_items:
            row = tk.Frame(info_frame_inner, bg=COLORS["primary_bg"])
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label, bg=COLORS["primary_bg"],
                     font=("Segoe UI", 10, "bold"), fg=COLORS["primary_dark"]).pack(side=tk.LEFT)
            tk.Label(row, text=value, bg=COLORS["primary_bg"],
                     font=("Consolas", 10), fg=COLORS["text_primary"]).pack(side=tk.LEFT, padx=10)

        tk.Label(frame, text="Credenciales de administrador: usuario y contrasena configurados por defecto.",
                 bg=COLORS["surface"], fg=COLORS["text_muted"],
                 font=("Segoe UI", 9)).pack(pady=10)

        tk.Label(frame, text="El servicio se iniciara automaticamente al encender la PC.",
                 bg=COLORS["surface"], fg=COLORS["text_muted"],
                 font=("Segoe UI", 9)).pack(pady=5)

        self.btn_next.config(text="Cerrar", command=self.root.destroy, bg=COLORS["success"])
        self.btn_back.config(state=tk.DISABLED)

    def _next_step(self):
        if self.step == 6:
            self.root.destroy()
            return

        if self.step == 1:
            self.config["install_dir"] = self.dir_var.get()
            if not self.config["install_dir"]:
                messagebox.showerror("Error", "Seleccione un directorio de instalacion.")
                return

        if self.step == 2:
            if not self.db_tested:
                resp = messagebox.askyesno("Advertencia",
                                           "No ha probado la conexion a la base de datos.\n"
                                           "¿Desea continuar de todos modos?")
                if not resp:
                    return
            for key, var in self.db_vars.items():
                self.config[key] = var.get()

        if self.step == 3:
            self.config["bind_address"] = self.bind_var.get()
            self.config["port"] = self.port_var.get()
            self.config["allowed_hosts"] = self.hosts_var.get()
            self.config["csrf_origins"] = self.origins_var.get()

        if self.step == 4:
            if not self.skip_var.get():
                key = self.license_text.get("1.0", tk.END).strip()
                if not key or key == "LIC-":
                    messagebox.showerror("Error", "Introduzca una clave de licencia valida.")
                    return
                self.config["license_key"] = key
            else:
                self.config["license_later"] = True

        self.step += 1
        self.btn_back.config(state=tk.NORMAL)
        self._show_step()

    def _prev_step(self):
        if self.step > 0:
            self.step -= 1
            if self.step == 0:
                self.btn_back.config(state=tk.DISABLED)
            self._show_step()


def main():
    root = tk.Tk()

    # High DPI support
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = SetupWizard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
