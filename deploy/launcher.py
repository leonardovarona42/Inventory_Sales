"""
Launcher - Desktop application to start/stop the MiNegocio service.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import threading
import time
from pathlib import Path


def is_frozen():
    return getattr(sys, 'frozen', False)


SERVICE_NAME = "MiNegocioServer"

COLORS = {
    "primary": "#1e40af",
    "primary_dark": "#1e3a8a",
    "success": "#059669",
    "success_light": "#d1fae5",
    "danger": "#dc2626",
    "danger_light": "#fee2e2",
    "warning": "#d97706",
    "warning_light": "#fef3c7",
    "bg": "#f8fafc",
    "card": "#ffffff",
    "text": "#1e293b",
    "text_muted": "#64748b",
    "border": "#e2e8f0",
}


def detect_install_dir():
    running_dir = Path(__file__).parent if not is_frozen() else Path(sys.executable).parent
    if (running_dir / "Inventory_Sales").exists():
        return str(running_dir)
    candidates = [
        Path("C:\\MiNegocio"),
        Path(os.environ.get("MINNEGOCIO_DIR", "")),
    ]
    for p in candidates:
        if p.exists() and (p / "Inventory_Sales").exists():
            return str(p)
    return str(running_dir)


def _read_port(install_dir):
    env_file = os.path.join(install_dir, ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("PORT="):
                    return line.split("=")[1].strip()
    return "8000"


def is_port_listening(port="8000"):
    """Check if ANY process is LISTENING on localhost for the given port."""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr ":{port}"',
            shell=True, capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            stripped = line.strip()
            # Only care about LISTENING on local addresses
            if 'LISTENING' in stripped:
                # Check if it's a local address (0.0.0.0, 127.0.0.1, or local hostname)
                parts = stripped.split()
                if len(parts) >= 2:
                    local_addr = parts[1]
                    if ('0.0.0.0' in local_addr or
                        '127.0.0.1' in local_addr or
                        local_addr.startswith('[')):
                        return True, parts[-1]  # Return PID too
        return False, None
    except Exception:
        return False, None


def check_service_status():
    try:
        install_dir = detect_install_dir()
        port = _read_port(install_dir)
        listening, pid = is_port_listening(port)
        if listening:
            return 'running', port
        # Check if installation exists (task scheduled or files present)
        bat = os.path.join(install_dir, "start_server.bat")
        if os.path.exists(bat):
            return 'stopped', port
        return 'not_installed', port
    except Exception:
        return 'unknown', '8000'


def start_service_async():
    """Start the Django server (called from background thread)."""
    try:
        install_dir = detect_install_dir()
        if not install_dir:
            return False, "No se encontro el directorio de instalacion"
        port = _read_port(install_dir)
        vbs = os.path.join(install_dir, "start_server.vbs")
        bat = os.path.join(install_dir, "start_server.bat")

        if os.path.exists(bat):
            with open(bat) as f:
                content = f.read()
            if f":{port}" not in content:
                import re
                content = re.sub(r':\d+', f':{port}', content)
                with open(bat, 'w') as f:
                    f.write(content)

        if os.path.exists(vbs):
            subprocess.Popen(['wscript.exe', vbs], cwd=install_dir)
        elif os.path.exists(bat):
            subprocess.Popen(
                [bat], shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW, cwd=install_dir
            )
        else:
            return False, "No se encontro el archivo de inicio"

        # Poll for up to 10 seconds
        for _ in range(20):
            time.sleep(0.5)
            listening, _ = is_port_listening(port)
            if listening:
                return True, f"Servicio activo en puerto {port}"

        return False, "El servidor no responde. Revisa service.log"
    except Exception as e:
        return False, f"Error: {str(e)}"


def stop_service_async():
    """Stop the Django server (called from background thread)."""
    try:
        install_dir = detect_install_dir()
        if not install_dir:
            return False, "No se encontro el directorio de instalacion"
        port = _read_port(install_dir)

        listening, pid = is_port_listening(port)
        if listening and pid:
            subprocess.run(
                f'taskkill /F /PID {pid}',
                shell=True, capture_output=True
            )

        stop_bat = os.path.join(install_dir, "stop_server.bat")
        if os.path.exists(stop_bat):
            subprocess.run([stop_bat], shell=True, capture_output=True)

        time.sleep(1)
        listening, _ = is_port_listening(port)
        if listening:
            return False, "No se pudo detener. Intenta de nuevo."
        return True, "Servicio detenido"
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_service_url(port="8000"):
    import socket
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
        return f"http://localhost:{port}  |  http://{ip}:{port}"
    except Exception:
        return f"http://localhost:{port}"


class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MiNegocio - Control")
        self.root.geometry("440x420")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg"])

        # Apply modern style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.busy = False  # Prevent overlapping operations

        self._setup_ui()
        self._update_status()

    def _setup_ui(self):
        # Header bar
        header = tk.Frame(self.root, bg=COLORS["primary"], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="MiNegocio", font=("Segoe UI", 20, "bold"),
                 bg=COLORS["primary"], fg="white").pack(pady=(18, 0))
        tk.Label(header, text="Control de Servicio", font=("Segoe UI", 9),
                 bg=COLORS["primary"], fg="#93c5fd").pack()

        # Main card
        card = tk.Frame(self.root, bg=COLORS["card"], bd=1, relief=tk.SOLID)
        card.pack(fill=tk.X, padx=20, pady=20)

        # Status section
        status_inner = tk.Frame(card, bg=COLORS["card"])
        status_inner.pack(fill=tk.X, padx=20, pady=20)

        self.status_indicator = tk.Canvas(status_inner, width=24, height=24,
                                           bg=COLORS["card"], highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 12), pady=5)

        self.status_label = tk.Label(status_inner, text="Verificando...",
                                      bg=COLORS["card"], font=("Segoe UI", 13, "bold"),
                                      fg=COLORS["text"])
        self.status_label.pack(side=tk.LEFT, pady=5)

        self.port_label = tk.Label(status_inner, text="",
                                    bg=COLORS["card"], font=("Segoe UI", 9),
                                    fg=COLORS["text_muted"])
        self.port_label.pack(side=tk.RIGHT, pady=5)

        # Separator
        tk.Frame(card, height=1, bg=COLORS["border"]).pack(fill=tk.X, padx=20)

        # URL section
        url_inner = tk.Frame(card, bg=COLORS["card"])
        url_inner.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(url_inner, text="URL del sistema", bg=COLORS["card"],
                 font=("Segoe UI", 9), fg=COLORS["text_muted"]).pack(anchor=tk.W)
        self.url_label = tk.Label(url_inner, text="", bg=COLORS["card"],
                                   font=("Consolas", 11), fg=COLORS["primary"])
        self.url_label.pack(anchor=tk.W, pady=(4, 0))

        # Buttons section
        btn_frame = tk.Frame(card, bg=COLORS["card"])
        btn_frame.pack(fill=tk.X, padx=20, pady=15)

        self.btn_start = tk.Button(btn_frame, text="  Iniciar Servicio",
                                    command=self._start, bg=COLORS["success"],
                                    fg="white", font=("Segoe UI", 12, "bold"),
                                    activebackground="#047857", relief=tk.FLAT,
                                    cursor="hand2", bd=0, padx=20, pady=10)
        self.btn_start.pack(fill=tk.X, pady=(0, 8))

        self.btn_stop = tk.Button(btn_frame, text="  Detener Servicio",
                                   command=self._stop, bg=COLORS["danger"],
                                   fg="white", font=("Segoe UI", 12, "bold"),
                                   activebackground="#b91c1c", relief=tk.FLAT,
                                   cursor="hand2", bd=0, padx=20, pady=10)
        self.btn_stop.pack(fill=tk.X)

        # Action buttons
        action_frame = tk.Frame(self.root, bg=COLORS["bg"])
        action_frame.pack(fill=tk.X, padx=20, pady=5)

        actions = [
            ("Abrir en Navegador", self._open_browser),
            ("Abrir Panel Admin", self._open_admin),
            ("Ver Logs", self._view_logs),
        ]
        for label, cmd in actions:
            btn = tk.Button(action_frame, text=label, command=cmd,
                            bg=COLORS["card"], fg=COLORS["text"],
                            font=("Segoe UI", 10), relief=tk.FLAT,
                            cursor="hand2", bd=1, highlightbackground=COLORS["border"],
                            highlightthickness=1, padx=15, pady=8)
            btn.pack(fill=tk.X, pady=2)

    def _draw_indicator(self, color):
        self.status_indicator.delete("all")
        self.status_indicator.create_oval(2, 2, 22, 22, fill=color, outline=color)
        # Pulsing ring for running
        if color == COLORS["success"]:
            self.status_indicator.create_oval(0, 0, 24, 24, outline="#059669", width=1)

    def _set_buttons(self, running):
        if self.busy:
            return
        if running:
            self.btn_start.config(state=tk.DISABLED, bg="#94a3b8",
                                  activebackground="#94a3b8", cursor="")
            self.btn_stop.config(state=tk.NORMAL, bg=COLORS["danger"],
                                 activebackground="#b91c1c", cursor="hand2")
        else:
            self.btn_start.config(state=tk.NORMAL, bg=COLORS["success"],
                                  activebackground="#047857", cursor="hand2")
            self.btn_stop.config(state=tk.DISABLED, bg="#94a3b8",
                                 activebackground="#94a3b8", cursor="")

    def _update_status(self):
        status, port = check_service_status()
        if status == 'running':
            self._draw_indicator(COLORS["success"])
            self.status_label.config(text="Servicio Activo", fg=COLORS["success"])
            self._set_buttons(True)
        elif status == 'stopped':
            self._draw_indicator(COLORS["warning"])
            self.status_label.config(text="Servicio Detenido", fg=COLORS["warning"])
            self._set_buttons(False)
        else:
            self._draw_indicator(COLORS["danger"])
            self.status_label.config(text="No Instalado", fg=COLORS["danger"])
            self.btn_start.config(state=tk.DISABLED, bg="#94a3b8",
                                  activebackground="#94a3b8", cursor="")
            self.btn_stop.config(state=tk.DISABLED, bg="#94a3b8",
                                 activebackground="#94a3b8", cursor="")

        install_dir = detect_install_dir()
        if install_dir:
            self.url_label.config(text=get_service_url(port))
            self.port_label.config(text=f"Puerto: {port}")

    def _start(self):
        if self.busy:
            return
        self.busy = True
        self.btn_start.config(state=tk.DISABLED, text="  Iniciando...", bg="#94a3b8",
                              activebackground="#94a3b8", cursor="")
        self.btn_stop.config(state=tk.DISABLED)

        def _do_start():
            success, msg = start_service_async()
            self.root.after(0, lambda: self._on_start_done(success, msg))

        threading.Thread(target=_do_start, daemon=True).start()

    def _on_start_done(self, success, msg):
        self.busy = False
        self._update_status()
        if success:
            messagebox.showinfo("Exitoso", msg, parent=self.root)
        else:
            messagebox.showerror("Error", msg, parent=self.root)

    def _stop(self):
        if self.busy:
            return
        if not messagebox.askyesno("Confirmar", "¿Detener el servicio?\n"
                                    "El sistema sera inaccesible.", parent=self.root):
            return
        self.busy = True
        self.btn_stop.config(state=tk.DISABLED, text="  Deteniendo...", bg="#94a3b8",
                             activebackground="#94a3b8", cursor="")
        self.btn_start.config(state=tk.DISABLED)

        def _do_stop():
            success, msg = stop_service_async()
            self.root.after(0, lambda: self._on_stop_done(success, msg))

        threading.Thread(target=_do_stop, daemon=True).start()

    def _on_stop_done(self, success, msg):
        self.busy = False
        self._update_status()
        if success:
            messagebox.showinfo("Exitoso", msg, parent=self.root)
        else:
            messagebox.showerror("Error", msg, parent=self.root)

    def _open_browser(self):
        import webbrowser
        url = self.url_label.cget("text").split("  |  ")[0].strip()
        webbrowser.open(url)

    def _view_logs(self):
        install_dir = detect_install_dir()
        if install_dir:
            os.startfile(install_dir)

    def _open_admin(self):
        import webbrowser
        url = self.url_label.cget("text").split("  |  ")[0].strip().rstrip("/") + "/admin/"
        webbrowser.open(url)


def main():
    root = tk.Tk()
    app = LauncherApp(root)
    def refresh():
        if not app.busy:
            app._update_status()
        root.after(5000, refresh)
    root.after(5000, refresh)
    root.mainloop()


if __name__ == "__main__":
    main()
