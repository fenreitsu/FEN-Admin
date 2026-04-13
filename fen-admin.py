#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FENAdmin - Gestor de Usuarios y Grupos v1.2
Creador: @fenreitsu
Compatibilidad: Linux (Kali Linux, Ubuntu, Debian, etc.)
Mejoras: Terminal interactiva inferior, sin panel de actividad, desbloqueo corregido
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog, scrolledtext
import subprocess
import pwd
import grp
import os
import sys
import re
import datetime
import random
import string
import secrets
import threading
import queue
from functools import partial

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE LOGOS
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

LOGO_LIGHT = os.path.join(SCRIPT_DIR, "resources", "logo", "fenreitsu.png")
LOGO_DARK = os.path.join(SCRIPT_DIR, "resources", "logo", "fenreitsu-white.png")

LOGO_SIZE = (48, 48)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES DE TEMA
# ─────────────────────────────────────────────────────────────────────────────

THEMES = {
    "dark": {
        "bg":           "#0d1117",
        "bg2":          "#161b22",
        "bg3":          "#21262d",
        "border":       "#30363d",
        "accent":       "#58a6ff",
        "accent2":      "#1f6feb",
        "success":      "#3fb950",
        "warning":      "#d29922",
        "danger":       "#f85149",
        "info":         "#79c0ff",
        "text":         "#e6edf3",
        "text2":        "#8b949e",
        "text3":        "#484f58",
        "select_bg":    "#1f6feb",
        "select_fg":    "#ffffff",
        "header_bg":    "#161b22",
        "row_odd":      "#0d1117",
        "row_even":     "#161b22",
        "button_bg":    "#21262d",
        "button_fg":    "#e6edf3",
        "button_hover": "#30363d",
        "entry_bg":     "#0d1117",
        "entry_fg":     "#e6edf3",
        "label_fg":     "#e6edf3",
        "disabled_fg":  "#484f58",
        "tag_sys":      "#161b22",
        "tag_sys_fg":   "#8b949e",
        "scrollbar":    "#30363d",
        "terminal_bg":  "#0a0e12",
        "terminal_fg":  "#00ff00",
        "terminal_error": "#ff4444",
    },
    "light": {
        "bg":           "#f6f8fa",
        "bg2":          "#ffffff",
        "bg3":          "#eaeef2",
        "border":       "#d0d7de",
        "accent":       "#0969da",
        "accent2":      "#218bff",
        "success":      "#1a7f37",
        "warning":      "#9a6700",
        "danger":       "#cf222e",
        "info":         "#0550ae",
        "text":         "#1f2328",
        "text2":        "#656d76",
        "text3":        "#afb8c1",
        "select_bg":    "#0969da",
        "select_fg":    "#ffffff",
        "header_bg":    "#f6f8fa",
        "row_odd":      "#ffffff",
        "row_even":     "#f6f8fa",
        "button_bg":    "#f6f8fa",
        "button_fg":    "#1f2328",
        "button_hover": "#eaeef2",
        "entry_bg":     "#ffffff",
        "entry_fg":     "#1f2328",
        "notif_bg":     "#ffffff",
        "notif_border": "#0969da",
        "label_fg":     "#1f2328",
        "disabled_fg":  "#afb8c1",
        "tag_sys":      "#eaeef2",
        "tag_sys_fg":   "#656d76",
        "scrollbar":    "#d0d7de",
        "terminal_bg":  "#f0f0f0",
        "terminal_fg":  "#006600",
        "terminal_error": "#cc0000",
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES DE SISTEMA
# ─────────────────────────────────────────────────────────────────────────────

def normalize_expire_date(date_str):
    """Convierte 'Jul 10, 2026' a '2026-07-10' o devuelve '' para never"""
    if not date_str or date_str.lower() == 'never':
        return ''
    # Si ya está en formato YYYY-MM-DD, devolverlo
    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
        return date_str
    # Intentar parsear 'Mon DD, YYYY'
    try:
        dt = datetime.datetime.strptime(date_str, '%b %d, %Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return date_str

def run_cmd(cmd, shell=True):
    try:
        result = subprocess.run(
            cmd, shell=shell, capture_output=True, text=True
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def is_root():
    return os.geteuid() == 0

def validate_password(password):
    if not password:
        return False, "La contraseña no puede estar vacía."
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una letra mayúscula."
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una letra minúscula."
    if not re.search(r'[0-9]', password):
        return False, "La contraseña debe contener al menos un número."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "La contraseña debe contener al menos un carácter especial."
    weak_patterns = ['password', '123456', 'qwerty', 'abc123', 'admin', 'root', 'toor', 'iloveyou', 'monkey', 'dragon', 'master', 'sunshine']
    if password.lower() in weak_patterns:
        return False, "La contraseña es demasiado común o débil."
    if re.search(r'(.)\1{3,}', password):
        return False, "Evite secuencias repetitivas de caracteres."
    return True, "OK"

def generate_password(length=16, use_special=True):
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?" if use_special else ""
    all_chars = uppercase + lowercase + digits + special
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
    ]
    if use_special:
        password.append(secrets.choice(special))
    password.extend(secrets.choice(all_chars) for _ in range(length - len(password)))
    random.shuffle(password)
    return ''.join(password)

def save_password_to_file(password, username=""):
    root = tk._default_root
    if root:
        root.lift()
        root.focus_force()
    filename = filedialog.asksaveasfilename(
        title="Guardar contraseña",
        defaultextension=".txt",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
        initialfile=f"password_{username}.txt" if username else "password.txt"
    )
    if filename:
        try:
            with open(filename, 'w') as f:
                f.write(f"Usuario: {username}\n" if username else "")
                f.write(f"Contraseña: {password}\n")
                f.write(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n")
                f.write("¡Mantén esta contraseña en un lugar seguro!\n")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")
            return False
    return False

def get_all_groups():
    groups = []
    for g in grp.getgrall():
        groups.append({
            "name":    g.gr_name,
            "gid":     g.gr_gid,
            "members": list(g.gr_mem),
            "passwd":  g.gr_passwd,
            "system":  g.gr_gid < 1000,
        })
    return sorted(groups, key=lambda g: g["gid"])

def get_user_privileges(username):
    privileges = {}
    try:
        p = pwd.getpwnam(username)
        privileges['uid'] = p.pw_uid
        privileges['gid'] = p.pw_gid
        privileges['gecos'] = p.pw_gecos
        privileges['home'] = p.pw_dir
        privileges['shell'] = p.pw_shell
    except KeyError:
        pass
    out, _, _ = run_cmd(f"groups {username}")
    privileges['groups'] = out.split(':')[1].strip().split() if ':' in out else out.strip().split()
    privileges['is_sudoer'] = 'sudo' in privileges['groups'] or 'wheel' in privileges['groups']
    out, _, _ = run_cmd(f"chage -l {username} 2>/dev/null | grep 'Account expires'")
    raw_expires = out.split(':')[1].strip() if out and ':' in out else 'never'
    privileges['expires'] = normalize_expire_date(raw_expires)
    out, _, _ = run_cmd(f"chage -l {username} 2>/dev/null | grep 'Password expires'")
    privileges['passwd_expires'] = out.split(':')[1].strip() if out and ':' in out else 'never'
    out, _, _ = run_cmd(f"chage -l {username} 2>/dev/null | grep 'Inactive'")
    privileges['inactive_days'] = out.split(':')[1].strip() if out and ':' in out else 'never'
    return privileges

def get_users():
    users = []
    for p in pwd.getpwall():
        is_system = p.pw_uid < 1000
        locked = False
        try:
            with open('/etc/shadow', 'r') as f:
                for line in f:
                    if line.startswith(p.pw_name + ':'):
                        shadow_pw = line.split(':')[1]
                        if shadow_pw.startswith('!') or shadow_pw.startswith('*'):
                            locked = True
                        break
        except Exception:
            out, _, _ = run_cmd(f"passwd -S {p.pw_name} 2>/dev/null")
            if out and 'L' in out.split()[1] if len(out.split()) > 1 else False:
                locked = True
        users.append({
            "name":    p.pw_name,
            "uid":     p.pw_uid,
            "gid":     p.pw_gid,
            "gecos":   p.pw_gecos,
            "home":    p.pw_dir,
            "shell":   p.pw_shell,
            "system":  is_system,
            "locked":  locked,
        })
    return sorted(users, key=lambda u: u["uid"])

def get_user_groups(username):
    try:
        out, _, _ = run_cmd(f"groups {username}")
        if ':' in out:
            groups = out.split(':')[1].strip().split()
        else:
            groups = out.strip().split()
        return groups
    except Exception:
        return []

def get_available_shells():
    """Obtiene lista de shells disponibles desde /etc/shells"""
    shells = []
    try:
        with open('/etc/shells', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if os.path.exists(line):
                        shells.append(line)
    except Exception:
        shells = ['/bin/bash', '/bin/sh', '/bin/dash', '/bin/zsh', '/bin/fish',
                  '/sbin/nologin', '/usr/sbin/nologin', '/bin/rbash']
    return shells if shells else ['/usr/bin/zsh']

# ─────────────────────────────────────────────────────────────────────────────
# TERMINAL INTERACTIVA
# ─────────────────────────────────────────────────────────────────────────────

class InteractiveTerminal:
    def __init__(self, parent, theme, fire_warning):
        self.parent = parent
        self.theme = theme
        self.fire_warning = fire_warning
        self.process = None
        self.history = []
        self.history_index = 0

        self.frame = ttk.LabelFrame(parent, text="📟 Terminal Interactiva", padding="5")

        self.output_area = scrolledtext.ScrolledText(
            self.frame,
            height=12,
            bg=theme["terminal_bg"],
            fg=theme["terminal_fg"],
            font=('Courier New', 9),
            wrap=tk.WORD,
            state='disabled'
        )
        self.output_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.output_area.tag_config('error', foreground=theme["terminal_error"])
        self.output_area.tag_config('success', foreground=theme["success"])
        self.output_area.tag_config('warning', foreground=theme["warning"])
        self.output_area.tag_config('info', foreground=theme["info"])
        self.output_area.tag_config('command', foreground=theme["accent"])
        input_frame = tk.Frame(self.frame)
        input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.prompt_label = tk.Label(
            input_frame,
            text="$> ",
            font=('Courier New', 10, 'bold'),
            fg=theme["accent"],
            bg=theme["bg"]
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.command_entry = tk.Entry(
            input_frame,
            font=('Courier New', 10),
            bg=theme["entry_bg"],
            fg=theme["entry_fg"],
            insertbackground=theme["accent"],
            relief=tk.FLAT
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.command_entry.bind('<Return>', self.execute_command)
        self.command_entry.bind('<Up>', self.history_up)
        self.command_entry.bind('<Down>', self.history_down)

        self.exec_btn = tk.Button(
            input_frame,
            text="▶ Ejecutar",
            font=('Courier New', 9, 'bold'),
            bg=theme["accent2"],
            fg="#fff",
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: self.execute_command()
        )
        self.exec_btn.pack(side=tk.RIGHT, padx=(5, 0))

        self.clear_btn = tk.Button(
            input_frame,
            text="🗑 Limpiar",
            font=('Courier New', 9),
            bg=theme["button_bg"],
            fg=theme["button_fg"],
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_output
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=(5, 0))

        self.current_directory = os.getcwd()

        self._write_output("=" * 60, "info")
        self._write_output("  FENAdmin Terminal Interactiva v1.2", "success")
        self._write_output("  Escribe comandos del sistema y presiona Enter", "info")
        self._write_output(f"  Directorio actual: {self.current_directory}", "info")
        self._write_output("  Usa 'clear' para limpiar la pantalla", "info")
        self._write_output("=" * 60, "info")
        self._write_output("")

    def apply_theme(self, theme):
        self.theme = theme
        self.output_area.configure(bg=theme["terminal_bg"], fg=theme["terminal_fg"])
        self.output_area.tag_config('error', foreground=theme["terminal_error"])
        self.output_area.tag_config('success', foreground=theme["success"])
        self.output_area.tag_config('warning', foreground=theme["warning"])
        self.output_area.tag_config('info', foreground=theme["info"])
        self.output_area.tag_config('command', foreground=theme["accent"])
        self.prompt_label.configure(fg=theme["accent"], bg=theme["bg"])
        self.command_entry.configure(bg=theme["entry_bg"], fg=theme["entry_fg"])
        self.clear_btn.configure(bg=theme["button_bg"], fg=theme["button_fg"])

    def _write_output(self, text, tag=None):
        self.output_area.configure(state='normal')
        if tag and tag in self.output_area.tag_names():
            self.output_area.insert(tk.END, text + "\n", tag)
        else:
            self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.configure(state='disabled')

    def execute_command(self, event=None):
        command = self.command_entry.get().strip()
        if not command:
            return

    # 👇 Bloquear comandos peligrosos sobre nobody/nogroup
        command_lower = command.lower()
        dangerous_patterns = [
            "userdel nobody",
            "userdel 'nobody'",
            'userdel "nobody"',
            "groupdel nogroup",
            "groupdel 'nogroup'",
            'groupdel "nogroup"',
            "usermod nobody",
            "usermod 'nobody'",
            'usermod "nobody"',
            "groupmod nogroup",
            "groupmod 'nogroup'",
            'groupmod "nogroup"',
            "passwd nobody",
            "passwd 'nobody'",
            'passwd "nobody"',
            "chage nobody",
            "chage 'nobody'",
            'chage "nobody"',
        ]

        for pattern in dangerous_patterns:
            if pattern in command_lower:
                self._write_output(self.fire_warning, "error")
                self.command_entry.delete(0, tk.END)
                return

        self.history.append(command)
        self.history_index = len(self.history)

        self._write_output(f"\n{self.prompt_label.cget('text')}{command}", "command")

        if command.lower() == 'clear':
            self.clear_output()
            self.command_entry.delete(0, tk.END)
            return
        elif command.lower() == 'exit':
            self._write_output("Saliendo del terminal...", "warning")
            self.command_entry.delete(0, tk.END)
            return
        elif command.lower().startswith('cd '):
            try:
                new_dir = command[3:].strip()
                if new_dir == '~':
                    new_dir = os.path.expanduser('~')
                os.chdir(new_dir)
                self.current_directory = os.getcwd()
                self._write_output(f"Directorio cambiado a: {self.current_directory}", "success")
            except Exception as e:
                self._write_output(f"Error: {str(e)}", "error")
            self.command_entry.delete(0, tk.END)
            return

        self.command_entry.delete(0, tk.END)
        self.command_entry.configure(state='disabled')
        self.exec_btn.configure(state='disabled')

        def run():
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=self.current_directory,
                    timeout=30
                )

                if result.stdout:
                    for line in result.stdout.splitlines():
                        self._write_output(line)
                if result.stderr:
                    for line in result.stderr.splitlines():
                        self._write_output(line, "error")
                if result.returncode != 0 and not result.stderr:
                    self._write_output(f"Comando finalizado con código: {result.returncode}", "warning")

            except subprocess.TimeoutExpired:
                self._write_output("ERROR: El comando excedió el tiempo límite (30 segundos)", "error")
            except Exception as e:
                self._write_output(f"ERROR: {str(e)}", "error")
            finally:
                self.parent.after(0, self._reenable_input)

        threading.Thread(target=run, daemon=True).start()

    def _reenable_input(self):
        self.command_entry.configure(state='normal')
        self.exec_btn.configure(state='normal')
        self.command_entry.focus()

    def history_up(self, event):
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.history[self.history_index])

    def history_down(self, event):
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.history[self.history_index])
        elif self.history_index == len(self.history) - 1:
            self.history_index = len(self.history)
            self.command_entry.delete(0, tk.END)

    def clear_output(self):
        self.output_area.configure(state='normal')
        self.output_area.delete(1.0, tk.END)
        self.output_area.configure(state='disabled')

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.frame.pack_forget()


# ─────────────────────────────────────────────────────────────────────────────
# APLICACIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

class FENAdmin(tk.Tk):
    def __init__(self):
        super().__init__()

        self.theme_name = tk.StringVar(value="dark")
        self.T = THEMES["dark"]
        self.show_system = tk.BooleanVar(value=False)
        self._filter_text = tk.StringVar()
        self._filter_text.trace_add("write", lambda *_: self._apply_filter())

        self.title("FENAdmin v1.2 - by @fenreitsu")
        self.geometry("1200x700")
        self.minsize(900, 600)
        self.configure(bg=self.T["bg"])
        self._set_icon()
        self._set_window_icon()
        # Mensaje de advertencia para acciones prohibidas
        self.FIRE_WARNING = "🔥 No juegues con fuego, esta acción es peligrosa y está prohibida."
        self._build_ui()
        self._apply_theme()
        self.refresh_users()


    def _load_logo_image(self):
        try:
            logo_path = LOGO_DARK if self.theme_name.get() == "dark" else LOGO_LIGHT
            if os.path.exists(logo_path):
                original_image = tk.PhotoImage(file=logo_path)
                desired_width, desired_height = LOGO_SIZE
                if original_image.width() != desired_width or original_image.height() != desired_height:
                    w_factor = max(1, original_image.width() // desired_width)
                    h_factor = max(1, original_image.height() // desired_height)
                    self.logo_image = original_image.subsample(w_factor, h_factor)
                else:
                    self.logo_image = original_image
                self.logo_label.config(image=self.logo_image)
            else:
                self.logo_label.config(image='', text='⬡', font=("Courier New", 24))
        except Exception as e:
            print(f"Error cargando logo: {e}")
            self.logo_label.config(image='', text='⬡', font=("Courier New", 24))

    def _set_icon(self):
        try:
            icon_path = LOGO_DARK if self.theme_name.get() == "dark" else LOGO_LIGHT
            if os.path.exists(icon_path):
                icon_image = tk.PhotoImage(file=icon_path)
                if icon_image.width() > 64 or icon_image.height() > 64:
                    icon_image = icon_image.subsample(
                        icon_image.width() // 32,
                        icon_image.height() // 32
                    )
                self.iconphoto(True, icon_image)
                self.icon_image = icon_image
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")

    def _set_window_icon(self):
        try:
            icon_path = LOGO_DARK if self.theme_name.get() == "dark" else LOGO_LIGHT
            if os.path.exists(icon_path):
                icon_img = tk.PhotoImage(file=icon_path)
                if icon_img.width() > 64:
                    icon_img = icon_img.subsample(icon_img.width() // 32, icon_img.height() // 32)
                self.iconphoto(True, icon_img)
                self.icon_image = icon_img
        except Exception as e:
            print(f"No se pudo establecer el icono: {e}")

    def _build_ui(self):
        T = self.T

        # Barra superior
        self.topbar = tk.Frame(self, height=50)
        self.topbar.pack(fill="x", side="top")
        self.topbar.pack_propagate(False)

        logo_frame = tk.Frame(self.topbar)
        logo_frame.pack(side="left", padx=10, pady=5)

        self.logo_image = None
        self.logo_label = tk.Label(logo_frame, image=None)
        self.logo_label.pack(side="left", padx=(0, 10))

        self.lbl_logo = tk.Label(
            logo_frame,
            text="FENAdmin v1.2",
            font=("Courier New", 16, "bold"),
        )
        self.lbl_logo.pack(side="left")

        self._load_logo_image()

        self.lbl_creator = tk.Label(
            self.topbar,
            text="by @fenreitsu",
            font=("Courier New", 9),
            padx=4
        )
        self.lbl_creator.pack(side="left", pady=6)

        right_frame = tk.Frame(self.topbar)
        right_frame.pack(side="right", padx=12)

        self.btn_theme = tk.Button(
            right_frame, text="☀  Claro", font=("Courier New", 9, "bold"),
            relief="flat", cursor="hand2", padx=10, pady=4,
            command=self._toggle_theme
        )
        self.btn_theme.pack(side="right", padx=4)

        root_text = "● ROOT" if is_root() else "● USER"
        root_color = T["success"] if is_root() else T["warning"]
        self.lbl_root = tk.Label(
            right_frame,
            text=root_text,
            font=("Courier New", 9, "bold"),
            fg=root_color, padx=8
        )
        self.lbl_root.pack(side="right", padx=8)

        self.sep_top = tk.Frame(self, height=1)
        self.sep_top.pack(fill="x")

        # PANEL PRINCIPAL - Sidebar + Contenido
        self.main_container = tk.Frame(self)
        self.main_container.pack(fill="both", expand=True)

        # Sidebar izquierda
        self.sidebar = tk.Frame(self.main_container, width=160)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        self.sep_side = tk.Frame(self.main_container, width=1)
        self.sep_side.pack(side="left", fill="y")

        # Área central (contenido principal + terminal)
        self.center_area = tk.Frame(self.main_container)
        self.center_area.pack(side="left", fill="both", expand=True)

        # Contenido principal (tablas)
        self.content = tk.Frame(self.center_area)
        self.content.pack(fill="both", expand=True)

        self._frames = {}
        for name in ("users", "groups"):
            f = tk.Frame(self.content)
            self._frames[name] = f
            f.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_users_view(self._frames["users"])
        self._build_groups_view(self._frames["groups"])
        self._show_frame("users")

        # TERMINAL INTERACTIVA (parte inferior)
        self.FIRE_WARNING = "🔥 No juegues con fuego, esta acción es peligrosa y está prohibida."
        self.terminal = InteractiveTerminal(self.center_area, self.T, self.FIRE_WARNING)
        self.terminal.pack(fill="both", side="bottom", pady=(5, 0))

        # Barra de estado inferior
        self.statusbar = tk.Frame(self, height=26)
        self.statusbar.pack(fill="x", side="bottom")
        self.statusbar.pack_propagate(False)

        self.status_label = tk.Label(
            self.statusbar, text="  FENAdmin listo. Usa la terminal inferior para comandos.",
            font=("Courier New", 8), anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=6)

        self.lbl_time = tk.Label(
            self.statusbar, font=("Courier New", 8), padx=8
        )
        self.lbl_time.pack(side="right")
        self._update_clock()

    def _build_sidebar(self):
        T = self.T

        tk.Label(
            self.sidebar, text="NAVEGACIÓN",
            font=("Courier New", 8, "bold"), anchor="w", padx=14, pady=12
        ).pack(fill="x")

        self.nav_buttons = {}
        nav_items = [
            ("users",  "👤  Usuarios",  self._show_users),
            ("groups", "👥  Grupos",    self._show_groups),
        ]
        for key, label, cmd in nav_items:
            btn = tk.Button(
                self.sidebar, text=label,
                font=("Courier New", 10), anchor="w",
                relief="flat", cursor="hand2", padx=14, pady=8,
                command=cmd
            )
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        tk.Frame(self.sidebar, height=1).pack(fill="x", pady=8, padx=14)

        tk.Label(
            self.sidebar, text="FILTROS",
            font=("Courier New", 8, "bold"), anchor="w", padx=14, pady=4
        ).pack(fill="x")

        self.chk_system = tk.Checkbutton(
            self.sidebar, text="  Mostrar sistema",
            font=("Courier New", 9),
            variable=self.show_system, anchor="w",
            relief="flat", cursor="hand2",
            command=self._apply_filter
        )
        self.chk_system.pack(fill="x", padx=8)

        tk.Frame(self.sidebar, height=1).pack(fill="x", pady=8, padx=14)

        self.btn_refresh = tk.Button(
            self.sidebar, text="↻  Actualizar",
            font=("Courier New", 9), anchor="w",
            relief="flat", cursor="hand2", padx=14, pady=6,
            command=self._full_refresh
        )
        self.btn_refresh.pack(fill="x")

        tk.Frame(self.sidebar, height=20).pack(fill="x", expand=True)

        tk.Label(
            self.sidebar, text="💡 TIP",
            font=("Courier New", 8, "bold"), anchor="w", padx=14, pady=4
        ).pack(fill="x")

        tip_text = tk.Label(
            self.sidebar,
            text="Usa la terminal\ninferior para\ncomandos directos",
            font=("Courier New", 8),
            anchor="w", justify="left", padx=14
        )
        tip_text.pack(fill="x")

    def _build_users_view(self, parent):
        T = self.T

        top_toolbar = tk.Frame(parent, height=50)
        top_toolbar.pack(fill="x", pady=(0, 0))
        top_toolbar.pack_propagate(False)

        tk.Label(
            top_toolbar, text="Gestión de Usuarios",
            font=("Courier New", 14, "bold"), anchor="w", padx=16, pady=8
        ).pack(side="left")

        actions = [
            ("😁 Nuevo Usuario",  self._dlg_new_user,    "accent"),
            ("✏ Editar Usuario",  self._dlg_edit_user,   "warning"),
            ("🗑 Eliminar",       self._delete_user,     "danger"),
            ("🔒 Bloquear",       self._lock_user,       "warning"),
            ("🔓 Desbloquear",    self._unlock_user,     "success"),
        ]

        action_frame = tk.Frame(top_toolbar)
        action_frame.pack(side="right", padx=10)

        for label, cmd, style in actions:
            btn = self._styled_btn(action_frame, label, cmd, style)
            btn.pack(side="left", padx=3, pady=8)

        filter_bar = tk.Frame(parent, height=40)
        filter_bar.pack(fill="x", pady=(5, 0))
        filter_bar.pack_propagate(False)

        tk.Label(filter_bar, text="🔍 Buscar:", font=("Courier New", 9, "bold"),
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(15, 5))

        self.search_entry = tk.Entry(filter_bar, font=("Courier New", 10), relief="flat",
                                    bg=T["entry_bg"], fg=T["entry_fg"],
                                    insertbackground=T["accent"], width=25)
        self.search_entry.pack(side="left", padx=(0, 15), ipady=3)
        self.search_entry.bind("<KeyRelease>", lambda e: self._apply_user_filters())

        clear_btn = tk.Button(filter_bar, text="✕ Limpiar filtros", font=("Courier New", 8),
                            relief="flat", cursor="hand2", command=self._clear_user_filters)
        clear_btn.pack(side="left", padx=5)
        self._theme_widget(clear_btn)

        tk.Frame(parent, height=1).pack(fill="x", pady=(5, 0))

        self.filters_visible = tk.BooleanVar(value=False)

        filter_header = tk.Frame(parent)
        filter_header.pack(fill="x", pady=(5, 0))

        self.toggle_btn = tk.Button(filter_header, text="▼ FILTROS AVANZADOS", font=("Courier New", 8, "bold"),
                                    relief="flat", cursor="hand2", command=self._toggle_filters)
        self.toggle_btn.pack(side="left", padx=15, pady=2)
        self._theme_widget(self.toggle_btn)

        self.advanced_filters = tk.Frame(parent)
        self._create_advanced_filters()

        table_frame = tk.Frame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("Usuario", "UID", "GID", "Info (GECOS)", "Home", "Shell", "Estado", "Tipo")
        self.tree_users = ttk.Treeview(
            table_frame, columns=cols, show="headings",
            selectmode="browse"
        )

        col_widths = [120, 60, 60, 160, 200, 140, 90, 100]
        for col, w in zip(cols, col_widths):
            self.tree_users.heading(col, text=col, command=partial(self._sort_tree, self.tree_users, col, False))
            self.tree_users.column(col, width=w, minwidth=40, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_users.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_users.xview)
        self.tree_users.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree_users.pack(fill="both", expand=True)

        def _on_double_user(event):
            row = self.tree_users.identify_row(event.y)
            if row:
                self.tree_users.selection_set(row)
                self.after(10, self._dlg_edit_user)
        self.tree_users.bind("<Double-1>", _on_double_user)
        self.tree_users.bind("<Button-3>", self._context_menu_user)

        self.ctx_user = tk.Menu(self, tearoff=0)

        info_bar = tk.Frame(parent, height=28)
        info_bar.pack(fill="x", side="bottom")
        info_bar.pack_propagate(False)
        self.lbl_user_count = tk.Label(
            info_bar, text="", font=("Courier New", 8), anchor="w", padx=10
        )
        self.lbl_user_count.pack(side="left")

    def _build_groups_view(self, parent):
        T = self.T

        toolbar = tk.Frame(parent, height=50)
        toolbar.pack(fill="x", pady=(0, 0))
        toolbar.pack_propagate(False)

        tk.Label(
            toolbar, text="Gestión de Grupos",
            font=("Courier New", 14, "bold"), anchor="w", padx=16, pady=8
        ).pack(side="left")

        actions = [
            ("＋ Nuevo Grupo",  self._dlg_new_group,   "accent"),
            ("🗑 Eliminar",     self._delete_group,    "danger"),
            ("✏ Editar",       self._dlg_edit_group,  "warning"),
        ]
        for label, cmd, style in reversed(actions):
            btn = self._styled_btn(toolbar, label, cmd, style)
            btn.pack(side="right", padx=4, pady=8)

        search_frame = tk.Frame(parent, height=35)
        search_frame.pack(fill="x", pady=(5, 0))
        search_frame.pack_propagate(False)

        tk.Label(search_frame, text="🔍 Buscar grupo:", font=("Courier New", 9, "bold"),
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(15, 5))

        self.group_search_entry = tk.Entry(search_frame, font=("Courier New", 10), relief="flat",
                                          bg=T["entry_bg"], fg=T["entry_fg"],
                                          insertbackground=T["accent"], width=25)
        self.group_search_entry.pack(side="left", padx=(0, 15), ipady=3)
        self.group_search_entry.bind("<KeyRelease>", lambda e: self.refresh_groups())

        tk.Frame(parent, height=1).pack(fill="x")

        table_frame = tk.Frame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("Grupo", "GID", "Miembros", "Tipo", "Contraseña")
        self.tree_groups = ttk.Treeview(
            table_frame, columns=cols, show="headings",
            selectmode="browse"
        )
        col_widths = [160, 70, 450, 100, 80]
        for col, w in zip(cols, col_widths):
            self.tree_groups.heading(col, text=col, command=partial(self._sort_tree, self.tree_groups, col, False))
            self.tree_groups.column(col, width=w, minwidth=40, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_groups.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_groups.xview)
        self.tree_groups.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree_groups.pack(fill="both", expand=True)

        def _on_double_group(event):
            row = self.tree_groups.identify_row(event.y)
            if row:
                self.tree_groups.selection_set(row)
                self.after(10, self._dlg_edit_group)
        self.tree_groups.bind("<Double-1>", _on_double_group)
        self.tree_groups.bind("<Button-3>", self._context_menu_group)

        self.ctx_group = tk.Menu(self, tearoff=0)

        info_bar = tk.Frame(parent, height=28)
        info_bar.pack(fill="x", side="bottom")
        info_bar.pack_propagate(False)
        self.lbl_group_count = tk.Label(
            info_bar, text="", font=("Courier New", 8), anchor="w", padx=10
        )
        self.lbl_group_count.pack(side="left")

    def _create_advanced_filters(self):
        T = self.T

        self.filter_vars = {
            "username": tk.StringVar(),
            "uid_min": tk.StringVar(),
            "uid_max": tk.StringVar(),
            "shell": tk.StringVar(),
            "state": tk.StringVar(),
            "gecos": tk.StringVar(),
            "home": tk.StringVar(),
            "account_type": tk.StringVar(),
        }

        filters_frame = tk.Frame(self.advanced_filters, pady=8)
        filters_frame.pack(fill="x", padx=15)

        row1 = tk.Frame(filters_frame)
        row1.pack(fill="x", pady=3)

        tk.Label(row1, text="Usuario:", font=("Courier New", 8), width=12, anchor="e",
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(0, 5))
        username_entry = tk.Entry(row1, textvariable=self.filter_vars["username"], width=20,
                                font=("Courier New", 8), relief="flat")
        username_entry.pack(side="left", padx=(0, 20))
        username_entry.bind("<KeyRelease>", lambda e: self._apply_user_filters())

        tk.Label(row1, text="UID desde:", font=("Courier New", 8), width=10, anchor="e",
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(0, 5))
        uid_min_entry = tk.Entry(row1, textvariable=self.filter_vars["uid_min"], width=8,
                                font=("Courier New", 8), relief="flat")
        uid_min_entry.pack(side="left", padx=(0, 5))
        uid_min_entry.bind("<KeyRelease>", lambda e: self._apply_user_filters())

        tk.Label(row1, text="hasta:", font=("Courier New", 8), width=5, anchor="e",
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(0, 5))
        uid_max_entry = tk.Entry(row1, textvariable=self.filter_vars["uid_max"], width=8,
                                font=("Courier New", 8), relief="flat")
        uid_max_entry.pack(side="left", padx=(0, 20))
        uid_max_entry.bind("<KeyRelease>", lambda e: self._apply_user_filters())

        row2 = tk.Frame(filters_frame)
        row2.pack(fill="x", pady=3)

        tk.Label(row2, text="Shell:", font=("Courier New", 8), width=12, anchor="e",
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(0, 5))
        shell_combo = ttk.Combobox(row2, textvariable=self.filter_vars["shell"], width=25,
                                    font=("Courier New", 8), state="readonly")
        shells = ['Todos'] + get_available_shells()
        shell_combo['values'] = shells
        shell_combo.set('Todos')
        shell_combo.pack(side="left", padx=(0, 20))
        shell_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_user_filters())

        tk.Label(row2, text="Estado:", font=("Courier New", 8), width=10, anchor="e",
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(0, 5))
        state_combo = ttk.Combobox(row2, textvariable=self.filter_vars["state"], width=15,
                                    font=("Courier New", 8), state="readonly")
        state_combo['values'] = ['Todos', 'Activo', 'Bloqueado']
        state_combo.set('Todos')
        state_combo.pack(side="left", padx=(0, 20))
        state_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_user_filters())

        tk.Label(row2, text="Tipo:", font=("Courier New", 8), width=8, anchor="e",
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(0, 5))
        type_combo = ttk.Combobox(row2, textvariable=self.filter_vars["account_type"], width=15,
                                    font=("Courier New", 8), state="readonly")
        type_combo['values'] = ['Todos', 'Admin', 'Desktop User', 'Personalizado']
        type_combo.set('Todos')
        type_combo.pack(side="left", padx=(0, 20))
        type_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_user_filters())

        row3 = tk.Frame(filters_frame)
        row3.pack(fill="x", pady=3)

        tk.Label(row3, text="GECOS:", font=("Courier New", 8), width=12, anchor="e",
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(0, 5))
        gecos_entry = tk.Entry(row3, textvariable=self.filter_vars["gecos"], width=52,
                                font=("Courier New", 8), relief="flat")
        gecos_entry.pack(side="left", padx=(0, 20))
        gecos_entry.bind("<KeyRelease>", lambda e: self._apply_user_filters())

        row4 = tk.Frame(filters_frame)
        row4.pack(fill="x", pady=3)

        tk.Label(row4, text="Home:", font=("Courier New", 8), width=12, anchor="e",
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(0, 5))
        home_entry = tk.Entry(row4, textvariable=self.filter_vars["home"], width=52,
                            font=("Courier New", 8), relief="flat")
        home_entry.pack(side="left", padx=(0, 20))
        home_entry.bind("<KeyRelease>", lambda e: self._apply_user_filters())

        for widget in [row1, row2, row3, row4, filters_frame]:
            self._theme_widget(widget)

    def _toggle_filters(self):
        if self.filters_visible.get():
            self.advanced_filters.pack_forget()
            self.filters_visible.set(False)
            self.toggle_btn.config(text="▶ FILTROS AVANZADOS")
        else:
            self.advanced_filters.pack(fill="x", before=self.tree_users.master)
            self.filters_visible.set(True)
            self.toggle_btn.config(text="▼ FILTROS AVANZADOS")

    def _apply_user_filters(self):
        users = get_users()
        show_sys = self.show_system.get()

        search_text = self.search_entry.get().lower()
        username_filter = self.filter_vars["username"].get().lower()
        uid_min = self.filter_vars["uid_min"].get()
        uid_max = self.filter_vars["uid_max"].get()
        shell_filter = self.filter_vars["shell"].get()
        state_filter = self.filter_vars["state"].get()
        gecos_filter = self.filter_vars["gecos"].get().lower()
        home_filter = self.filter_vars["home"].get().lower()
        type_filter = self.filter_vars["account_type"].get()


        for row in self.tree_users.get_children():
            self.tree_users.delete(row)

        count = 0
        for u in users:

            # 👇 Ocultar "nobody" del fitlro principal
            # if u["name"] == "nobody":
            #     continue

            if not show_sys and u["system"]:
                continue

            if search_text:
                if (search_text not in u["name"].lower() and
                    search_text not in u["gecos"].lower() and
                    search_text not in u["home"].lower() and
                    search_text not in u["shell"].lower()):
                    continue

            if username_filter and username_filter not in u["name"].lower():
                continue

            if uid_min:
                try:
                    if u["uid"] < int(uid_min):
                        continue
                except ValueError:
                    pass

            if uid_max:
                try:
                    if u["uid"] > int(uid_max):
                        continue
                except ValueError:
                    pass

            if shell_filter != "Todos" and u["shell"] != shell_filter:
                continue

            if state_filter != "Todos":
                user_locked = u["locked"]
                if state_filter == "Activo" and user_locked:
                    continue
                elif state_filter == "Bloqueado" and not user_locked:
                    continue

            if gecos_filter and gecos_filter not in u["gecos"].lower():
                continue

            if home_filter and home_filter not in u["home"].lower():
                continue

            account_type = self._determine_account_type(u["name"])
            if type_filter != "Todos" and account_type != type_filter:
                continue

            state = "🔒 Bloqueado" if u["locked"] else "✅ Activo"
            tag = "system" if u["system"] else ("locked" if u["locked"] else "normal")
            self.tree_users.insert(
                "", "end", iid=u["name"],
                values=(u["name"], u["uid"], u["gid"], u["gecos"],
                        u["home"], u["shell"], state, account_type),
                tags=(tag,)
            )
            count += 1

        T = self.T
        self.tree_users.tag_configure("system", background=T["tag_sys"], foreground=T["tag_sys_fg"])
        self.tree_users.tag_configure("locked", foreground=T["warning"])
        self.tree_users.tag_configure("normal", foreground=T["text"])
        self.lbl_user_count.config(text=f"  {count} usuario(s) mostrado(s)")

    # Grupos exactos que definen un Desktop User
    _DESKTOP_GROUPS = frozenset({'adm', 'dialout', 'fax', 'cdrom', 'floppy',
                                  'tape', 'audio', 'dip', 'video', 'plugdev', 'scanner'})

    def _determine_account_type(self, username):
        groups = set(get_user_groups(username))
        # Quitar el propio username (grupo personal) para comparar
        groups.discard(username)
        if 'sudo' in groups or 'wheel' in groups or 'admin' in groups:
            return "Admin"
        # Desktop User: tiene EXACTAMENTE los grupos del conjunto (puede tener el suyo propio)
        if groups == self._DESKTOP_GROUPS:
            return "Desktop User"
        return "Personalizado"

    def _clear_user_filters(self):
        self.search_entry.delete(0, tk.END)
        for var in self.filter_vars.values():
            var.set("")
        self.filter_vars["shell"].set("Todos")
        self.filter_vars["state"].set("Todos")
        self.filter_vars["account_type"].set("Todos")
        self._apply_user_filters()
        self._set_status("Filtros limpiados.")

    def _log_to_terminal(self, message, tag="info"):
        """Envía un mensaje a la terminal"""
        if hasattr(self, 'terminal'):
            self.terminal._write_output(message, tag)

    def _toggle_theme(self):
        if self.theme_name.get() == "dark":
            self.theme_name.set("light")
            self.btn_theme.config(text="🌙  Oscuro")
        else:
            self.theme_name.set("dark")
            self.btn_theme.config(text="☀  Claro")

        self.T = THEMES[self.theme_name.get()]
        self._apply_theme()

        self._set_window_icon()
        self._load_logo_image()

        if hasattr(self, 'terminal'):
            self.terminal.apply_theme(self.T)

        self.refresh_users()
        self.refresh_groups()

    def _apply_theme(self):
        T = self.T
        self.configure(bg=T["bg"])

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Treeview",
            background=T["bg2"],
            foreground=T["text"],
            fieldbackground=T["bg2"],
            rowheight=26,
            font=("Courier New", 9)
        )
        style.configure("Treeview.Heading",
            background=T["bg3"],
            foreground=T["text"],
            font=("Courier New", 9, "bold"),
            relief="flat"
        )
        style.map("Treeview",
            background=[("selected", T["select_bg"])],
            foreground=[("selected", T["select_fg"])]
        )
        style.configure("Vertical.TScrollbar",
            background=T["bg3"], troughcolor=T["bg2"],
            arrowcolor=T["text2"], relief="flat"
        )
        style.configure("Horizontal.TScrollbar",
            background=T["bg3"], troughcolor=T["bg2"],
            arrowcolor=T["text2"], relief="flat"
        )

        if hasattr(self, 'lbl_logo'):
            self.lbl_logo.configure(bg=T["bg"], fg=T["accent"])

        self._show_frame(getattr(self, "_current_frame", "users"))
        self._theme_all(self)
        self._show_frame(getattr(self, "_current_frame", "users"))

    def _theme_all(self, widget):
        T = self.T
        cls = widget.__class__.__name__
        try:
            if cls == "Frame":
                bg = T["bg"]
                widget.configure(bg=bg)
            elif cls == "Label":
                widget.configure(bg=T["bg"], fg=T["text"])
            elif cls == "Button":
                widget.configure(
                    bg=T["button_bg"], fg=T["button_fg"],
                    activebackground=T["button_hover"],
                    activeforeground=T["text"],
                    highlightbackground=T["border"],
                    highlightcolor=T["accent"]
                )
            elif cls == "Entry":
                widget.configure(
                    bg=T["entry_bg"], fg=T["entry_fg"],
                    insertbackground=T["accent"],
                    highlightbackground=T["border"],
                    highlightcolor=T["accent"],
                    highlightthickness=1
                )
            elif cls == "Checkbutton":
                widget.configure(
                    bg=T["bg"], fg=T["text"],
                    selectcolor=T["accent"],
                    activebackground=T["bg"],
                    activeforeground=T["text"]
                )
        except Exception:
            pass
        for child in widget.winfo_children():
            self._theme_all(child)

    def _theme_widget(self, widget):
        T = self.T
        try:
            widget.configure(bg=T["bg3"])
        except Exception:
            pass

    def _styled_btn(self, parent, text, cmd, style="accent"):
        T = self.T
        colors = {
            "accent":  (T["accent2"],  "#fff"),
            "danger":  (T["danger"],   "#fff"),
            "warning": (T["warning"],  "#fff"),
            "success": (T["success"],  "#fff"),
            "default": (T["button_bg"], T["button_fg"]),
        }
        bg, fg = colors.get(style, colors["default"])
        btn = tk.Button(
            parent, text=text, font=("Courier New", 9, "bold"),
            bg=bg, fg=fg,
            activebackground=T["button_hover"], activeforeground=T["text"],
            relief="flat", cursor="hand2", padx=10, pady=4,
            command=cmd
        )
        return btn

    def _set_status(self, msg):
        self.status_label.config(text=f"  {msg}")

    def _update_clock(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.lbl_time.config(text=now + "  ")
        self.after(1000, self._update_clock)

    def _sort_tree(self, tree, col, reverse):
        data = [(tree.set(k, col), k) for k in tree.get_children("")]
        try:
            data.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            data.sort(reverse=reverse)
        for i, (_, k) in enumerate(data):
            tree.move(k, "", i)
        tree.heading(col, command=partial(self._sort_tree, tree, col, not reverse))

    def _show_frame(self, name):
        self._current_frame = name
        for k, f in self._frames.items():
            f.lower() if k != name else f.lift()
        for k, b in self.nav_buttons.items():
            T = self.T
            if k == name:
                b.configure(bg=T["accent"], fg="#ffffff")
            else:
                b.configure(bg=T["bg"], fg=T["text2"])

    def _show_users(self):
        self._show_frame("users")
        self.refresh_users()

    def _show_groups(self):
        self._show_frame("groups")
        self.refresh_groups()

    def refresh_users(self):
        self._apply_user_filters()

    def refresh_groups(self):
        for row in self.tree_groups.get_children():
            self.tree_groups.delete(row)

        groups = get_all_groups()
        show_sys = self.show_system.get()
        search_text = getattr(self, 'group_search_entry', None)
        search_term = search_text.get().lower() if search_text else ""

        count = 0

        for g in groups:
            # 👇 Ocultar "nogroup" del filtro principal
            # if g["name"] == "nogroup":
            #     continue

            if not show_sys and g["system"]:
                continue

            if search_term and search_term not in g["name"].lower():
                continue

            tipo = "Sistema" if g["system"] else "Normal"
            members = ", ".join(g["members"]) if g["members"] else "(sin miembros)"
            has_passwd = "🔒 Sí" if g["passwd"] and g["passwd"] != 'x' else "❌ No"

            self.tree_groups.insert(
                "", "end", iid=g["name"],
                values=(g["name"], g["gid"], members, tipo, has_passwd),
                tags=("system",) if g["system"] else ("normal",)
            )
            count += 1

        T = self.T
        self.tree_groups.tag_configure("system", background=T["tag_sys"], foreground=T["tag_sys_fg"])
        self.tree_groups.tag_configure("normal", foreground=T["text"])
        self.lbl_group_count.config(text=f"  {count} grupo(s) mostrado(s) de {len(groups)} total")

    def _full_refresh(self):
        if self._current_frame == "users":
            self.refresh_users()
        else:
            self.refresh_groups()
        self._set_status("Datos actualizados.")

    def _apply_filter(self):
        if hasattr(self, "_current_frame") and self._current_frame == "users":
            self._apply_user_filters()
        elif hasattr(self, "_current_frame") and self._current_frame == "groups":
            self.refresh_groups()

    def _dlg_new_user(self):
        dlg = AdvancedUserDialog(self, "Nuevo Usuario", {}, self.T)
        dlg.saved_permissions = {}
        self.wait_window(dlg)
        if dlg.result:
            d = dlg.result

            # Validación de contraseña (ya existe)
            if not d.get("password"):
                messagebox.showerror("Error", "La contraseña es obligatoria.")
                return

            valid, msg = validate_password(d["password"])
            if not valid:
                messagebox.showerror("Contraseña inválida", msg)
                return

            cmd = f"useradd"
            if d.get("comment"):  cmd += f" -c '{d['comment']}'"
            if d.get("home"):     cmd += f" -d '{d['home']}'"
            if d.get("shell"):    cmd += f" -s '{d['shell']}'"
            if d.get("group"):    cmd += f" -g '{d['group']}'"
            if d.get("groups"):   cmd += f" -G '{d['groups']}'"
            if d.get("uid"):      cmd += f" -u '{d['uid']}'"
            if d.get("create_home", True): cmd += " -m"

            # NUEVO: Si NO es admin, expira en 90 días
            if d.get("account_type") != "Admin":
                expire_date = (datetime.datetime.now() + datetime.timedelta(days=90)).strftime("%Y-%m-%d")
                cmd += f" -e '{expire_date}'"
                # También configurar cambio de contraseña cada 90 días
                cmd_aging = f"chage -M 90 '{d['username']}'"
            else:
                # Admin sin expiración
                cmd += " -e ''"
                cmd_aging = ""

            if d.get("expires"):  # Si el usuario especificó una fecha, sobreescribe
                cmd = cmd.replace(f"-e '{expire_date}'", f"-e '{d['expires']}'") if expire_date else cmd + f" -e '{d['expires']}'"
            if d.get("inactive"): cmd += f" -f '{d['inactive']}'"
            cmd += f" '{d['username']}'"

            if not is_root():
                self._log_to_terminal(f"ERROR: Se requiere root para: {cmd}", "error")
                messagebox.showwarning("Sin privilegios", "Se requiere ejecutar como root (sudo).")
                return

            self._log_to_terminal(f"Ejecutando: $ {cmd}", "command")
            out, err, rc = run_cmd(cmd)

            if rc == 0:
                # Establecer contraseña
                pw_cmd = f"echo '{d['username']}:{d['password']}' | chpasswd"
                self._log_to_terminal(f"Estableciendo contraseña...", "info")
                run_cmd(pw_cmd)

                # Aplicar política de envejecimiento si no es admin
                if d.get("account_type") != "Admin" and cmd_aging:
                    self._log_to_terminal(f"Aplicando política: contraseña expira cada 90 días", "info")
                    run_cmd(cmd_aging)

                # Configurar sudo si es admin
                if d.get("account_type") == "Admin":
                    run_cmd(f"usermod -aG sudo '{d['username']}' 2>/dev/null || usermod -aG wheel '{d['username']}'")
                    self._log_to_terminal(f"✅ Usuario Admin '{d['username']}' creado (sin expiración)", "success")
                else:
                    self._log_to_terminal(f"✅ Usuario '{d['username']}' creado (expira en 90 días)", "success")

                # Configurar permisos avanzados (especiales) si se seleccionaron
                if hasattr(dlg, 'permisos_seleccionados') and dlg.permisos_seleccionados:
                    for grupo in dlg.permisos_seleccionados:
                        cmd = f"usermod -aG '{grupo}' '{d['username']}'"
                        self._log_to_terminal(f"Ejecutando: $ {cmd}", "command")
                        out, err, rc = run_cmd(cmd)
                        if rc == 0:
                            self._log_to_terminal(f"➕ Añadido permiso: {grupo} a '{d['username']}'", "success")
                        else:
                            self._log_to_terminal(f"❌ Error al añadir {grupo}: {err}", "error")

    def _dlg_edit_user(self):
        sel = self.tree_users.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un usuario para editar.")
            return
        username = sel[0]

        #BLOQUEO DE MODIFICACION DE "nobody"
        if username == "nobody":
            messagebox.showerror("Acción prohibida", self.FIRE_WARNING)
            return

        try:
            p = pwd.getpwnam(username)
            privileges = get_user_privileges(username)
            account_type_current = self._determine_account_type(username)
            try:
                primary_group_name = grp.getgrgid(p.pw_gid).gr_name
            except KeyError:
                primary_group_name = str(p.pw_gid)
            all_groups = get_user_groups(username)
            additional_groups = [g for g in all_groups
                                 if g != username and g != primary_group_name]
            current = {
                "username":     p.pw_name,
                "comment":      p.pw_gecos,
                "home":         p.pw_dir,
                "shell":        p.pw_shell,
                "uid":          p.pw_uid,
                "gid":          p.pw_gid,
                "group":        primary_group_name,
                "groups":       ",".join(additional_groups),
                "privileges":   privileges,
                "account_type": account_type_current,
            }
        except KeyError:
            messagebox.showerror("Error", f"Usuario '{username}' no encontrado.")
            return

        # Dentro de _dlg_edit_user, antes de crear el diálogo:
        current_permissions = {}
        for grupo in ['plugdev', 'lpadmin', 'dialout', 'netdev', 'adm', 'fax',
                    'sambashare', 'audio', 'cdrom', 'floppy', 'scanner',
                    'tape', 'video']:
            if grupo in privileges.get('groups', []):
                current_permissions[grupo] = True

        # Pasar los permisos actuales al diálogo
        dlg = AdvancedUserDialog(self, f"Editar Usuario: {username}", current, self.T, edit=True)
        dlg.saved_permissions = current_permissions  # Cargar permisos guardados

        self.wait_window(dlg)
        if not dlg.result:
            return  # Salir si el usuario canceló

        d = dlg.result

        # Validar contraseña si se proporcionó
        if d.get("password"):
            valid, msg = validate_password(d["password"])
            if not valid:
                messagebox.showerror("Contraseña inválida", msg)
                return

        # ============================================================
        # 1. CONSTRUIR Y EJECUTAR COMANDO USERMOD (Cambios Básicos)
        # ============================================================
        cmd_parts = ["usermod"]
        has_changes = False

        if d.get("comment") != current["comment"]:
            cmd_parts.append(f"-c '{d['comment']}'")
            has_changes = True

        if d.get("home") != current["home"]:
            cmd_parts.append(f"-d '{d['home']}' -m")
            has_changes = True

        if d.get("shell") != current["shell"]:
            cmd_parts.append(f"-s '{d['shell']}'")
            has_changes = True

        if d.get("new_name") and d["new_name"] != username:
            cmd_parts.append(f"-l '{d['new_name']}'")
            has_changes = True

        if d.get("groups"):
            cmd_parts.append(f"-aG '{d['groups']}'")
            has_changes = True

        if d.get("uid") and str(d["uid"]) != str(current["uid"]):
            cmd_parts.append(f"-u '{d['uid']}'")
            has_changes = True

        if d.get("expires"):
            cmd_parts.append(f"-e '{d['expires']}'")
            has_changes = True

        if d.get("inactive"):
            cmd_parts.append(f"-f '{d['inactive']}'")
            has_changes = True

        cmd_parts.append(f"'{username}'")
        cmd = " ".join(cmd_parts)

        if has_changes:
            if not is_root():
                self._log_to_terminal(f"ERROR: Se requiere root para: {cmd}", "error")
                messagebox.showwarning("Sin privilegios", "Se requiere ejecutar como root (sudo).")
                return

            self._log_to_terminal(f"Ejecutando: $ {cmd}", "command")
            out, err, rc = run_cmd(cmd)

            if rc != 0:
                self._log_to_terminal(f"❌ Error: {err}", "error")
                messagebox.showerror("Error", f"No se pudo modificar:\n{err}")
                return
            else:
                self._log_to_terminal(f"Sin cambios en campos básicos del usuario '{username}'", "info")

        # ============================================================
        # 2. ACTUALIZAR CONTRASEÑA (Si se cambio)
        # ============================================================
        if d.get("password"):
            self._log_to_terminal(f"Actualizando contraseña...", "info")
            run_cmd(f"echo '{username}:{d['password']}' | chpasswd")
            self._log_to_terminal(f"✅ Contraseña actualizada", "success")

        # ============================================================
        # 2.5 ACTUALIZAR PERMISOS AVANZADOS (grupos del sistema)
        # ============================================================
        if hasattr(dlg, 'permisos_seleccionados'):
            grupos_actuales = set(get_user_groups(username))
            grupos_nuevos = set(dlg.permisos_seleccionados)

            # Log para depuración
            self._log_to_terminal(f"Grupos actuales de {username}: {', '.join(grupos_actuales) if grupos_actuales else '(ninguno)'}", "info")
            self._log_to_terminal(f"Nuevos grupos seleccionados: {', '.join(grupos_nuevos) if grupos_nuevos else '(ninguno)'}", "info")

            # Añadir grupos nuevos
            for grupo in grupos_nuevos - grupos_actuales:
                cmd = f"usermod -aG '{grupo}' '{username}'"
                self._log_to_terminal(f"Ejecutando: $ {cmd}", "command")
                out, err, rc = run_cmd(cmd)
                if rc == 0:
                    self._log_to_terminal(f"➕ Añadido permiso: {grupo} a '{username}'", "success")
                else:
                    self._log_to_terminal(f"❌ Error al añadir {grupo}: {err}", "error")

            # Quitar grupos ya no seleccionados
            for grupo in grupos_actuales - grupos_nuevos:
                if grupo in ['plugdev', 'lpadmin', 'dialout', 'netdev', 'adm', 'fax',
                            'sambashare', 'audio', 'cdrom', 'floppy', 'scanner',
                            'tape', 'video']:
                    cmd = f"gpasswd -d '{username}' '{grupo}' 2>/dev/null"
                    self._log_to_terminal(f"Ejecutando: $ {cmd}", "command")
                    out, err, rc = run_cmd(cmd)
                    if rc == 0:
                        self._log_to_terminal(f"➖ Eliminado permiso: {grupo} de '{username}'", "warning")
                    else:
                        self._log_to_terminal(f"⚠ No se pudo eliminar {grupo}: {err}", "error")

            # ============================================================
            # 3. ACTUALIZAR PRIVILEGIOS DE ADMIN/SUDO
            # ============================================================
            if d.get("account_type") == "Admin":
                run_cmd(f"usermod -aG sudo '{username}' 2>/dev/null || usermod -aG wheel '{username}'")
                self._log_to_terminal(f"✅ Usuario '{username}' tiene privilegios de Admin", "success")
            else:
                run_cmd(f"deluser '{username}' sudo 2>/dev/null || gpasswd -d '{username}' wheel 2>/dev/null")
                self._log_to_terminal(f"⚠ Usuario '{username}' ya NO es Admin", "warning")

            # ============================================================
            # 4. Verificar si el TIPO DE CUENTA cambió
            # ============================================================
            tipo_anterior = current.get("account_type", "Personalizado")
            tipo_nuevo = d.get("account_type", "Personalizado")

            if tipo_anterior != tipo_nuevo:
                self._log_to_terminal(f"Tipo anterior: {tipo_anterior} → Tipo nuevo: {tipo_nuevo}", "info")

                if tipo_nuevo == "Admin":
                    self._log_to_terminal(f"Configurando usuario '{username}' como Admin SIN expiración", "info")
                    run_cmd(f"chage -E -1 '{username}'")
                    run_cmd(f"chage -M -1 '{username}'")
                    run_cmd(f"chage -I -1 '{username}'")
                    self._log_to_terminal(f"✅ Usuario Admin '{username}' - sin fecha de expiración", "success")
                else:
                    expire_date = (datetime.datetime.now() + datetime.timedelta(days=90)).strftime("%Y-%m-%d")
                    self._log_to_terminal(f"Aplicando expiración en 90 días ({expire_date})", "warning")
                    run_cmd(f"chage -E '{expire_date}' '{username}'")
                    run_cmd(f"chage -M 90 '{username}'")
                    run_cmd(f"chage -I 30 '{username}'")
                    self._log_to_terminal(f"⚠ Usuario '{username}' expirará el {expire_date}", "warning")
            else:
                self._log_to_terminal(f"Tipo de cuenta sin cambios", "info")

        # ============================================================
        # 5. FINALIZAR (ESTE MENSAJE SIEMPRE DEBE EJECUTARSE)
        # ============================================================
        self._log_to_terminal(f"✅ Usuario '{username}' modificado exitosamente", "success")
        self.refresh_users()
        self._set_status(f"Usuario '{username}' modificado.")

    def _delete_user(self):
        sel = self.tree_users.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un usuario.")
            return
        username = sel[0]

        #BLOQUEO DE ELIMINACION DE "nobody"
        if username == "nobody":
            messagebox.showerror("Acción prohibida", self.FIRE_WARNING)
            return

    # ========== NUEVO DIÁLOGO PERSONALIZADO ==========
        dialog = tk.Toplevel(self)
        dialog.title("Eliminar Usuario")
        dialog.resizable(False, False)
        dialog.configure(bg=self.T["bg"])
        dialog.transient(self)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        tk.Label(
            dialog,
            text="Eliminar Usuario\n"
        f"¿Eliminar el usuario '{username}'?\n\n"
        "Pulsa SI A TODO para eliminar también el directorio home.\n"
        "Pulsa SOLO USUARIO para eliminar solo el usuario.\n"
        "Pulsa CANCELAR para abortar.\n",
            font=("Courier New", 11, "bold"),
            bg=self.T["bg"], fg=self.T["text"]
        ).pack(pady=(15, 0))

        resultado = {"opcion": None}

        def responder(opcion):
            resultado["opcion"] = opcion
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg=self.T["bg"])
        btn_frame.pack(pady=(0, 20))

        tk.Button(
            btn_frame, text="🗑 SÍ A TODO", font=("Courier New", 9, "bold"),
            bg=self.T["danger"], fg="white", padx=15, pady=5,
            command=lambda: responder("full")
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="✓ Solo usuario", font=("Courier New", 9),
            bg=self.T["warning"], fg="white", padx=15, pady=5,
            command=lambda: responder("user_only")
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame, text="✗ Cancelar", font=("Courier New", 9),
            bg=self.T["disabled_fg"], fg=self.T["text"], padx=15, pady=5,
            command=lambda: responder("cancel")
        ).pack(side="left", padx=5)

        self.wait_window(dialog)

        if resultado["opcion"] == "full":
            remove_home = True
        elif resultado["opcion"] == "user_only":
            remove_home = False
        else:
            return
        # ========== FIN NUEVO DIÁLOGO ==========

        cmd = f"userdel{' -r' if remove_home else ''} '{username}'"
        if not is_root():
            self._log_to_terminal(f"ERROR: Se requiere root para: {cmd}", "error")
            messagebox.showwarning("Sin privilegios", "Se requiere ejecutar como root (sudo).")
            return

        self._log_to_terminal(f"Ejecutando: $ {cmd}", "command")
        out, err, rc = run_cmd(cmd)

        if rc == 0:
            self._log_to_terminal(f"✅ Usuario '{username}' eliminado", "success")
            self.refresh_users()
            self._set_status(f"Usuario '{username}' eliminado.")
        else:
            self._log_to_terminal(f"❌ Error: {err}", "error")
            messagebox.showerror("Error", f"No se pudo eliminar:\n{err}")

    def _lock_user(self):
        sel = self.tree_users.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un usuario.")
            return
        username = sel[0]
        cmd = f"passwd -l '{username}'"

        if not is_root():
            self._log_to_terminal(f"ERROR: Se requiere root para: {cmd}", "error")
            messagebox.showwarning("Sin privilegios", "Se requiere root.")
            return

        self._log_to_terminal(f"Ejecutando: $ {cmd}", "command")
        out, err, rc = run_cmd(cmd)

        if rc == 0:
            self._log_to_terminal(f"🔒 Usuario '{username}' bloqueado", "warning")
            self.refresh_users()
            self._set_status(f"Usuario '{username}' bloqueado.")
        else:
            self._log_to_terminal(f"❌ Error: {err}", "error")
            messagebox.showerror("Error", err)

    def _unlock_user(self):
        sel = self.tree_users.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un usuario.")
            return
        username = sel[0]
        # Primero asegurar que tiene contraseña, luego desbloquear
        cmd = f"passwd -u '{username}' 2>&1"

        if not is_root():
            self._log_to_terminal(f"ERROR: Se requiere root para: {cmd}", "error")
            messagebox.showwarning("Sin privilegios", "Se requiere root.")
            return

        self._log_to_terminal(f"Ejecutando: $ {cmd}", "command")
        out, err, rc = run_cmd(cmd)

        if rc == 0:
            self._log_to_terminal(f"🔓 Usuario '{username}' desbloqueado exitosamente", "success")
            self.refresh_users()
            self._set_status(f"Usuario '{username}' desbloqueado.")
        elif "passwordless" in err or "no password" in err:
            # Si el error es por falta de contraseña, pedir una nueva
            self._log_to_terminal(f"⚠ El usuario '{username}' no tiene contraseña válida. Se requiere establecer una.", "warning")
            respuesta = messagebox.askyesno(
                "Contraseña requerida",
                f"El usuario '{username}' no tiene una contraseña válida.\n\n"
                "¿Deseas establecer una nueva contraseña ahora para poder desbloquearlo?"
            )
            if respuesta:
                dlg = PasswordDialog(self, username, self.T)
                self.wait_window(dlg)
                if dlg.result:
                    valid, msg = validate_password(dlg.result)
                    if valid:
                        set_pw_cmd = f"echo '{username}:{dlg.result}' | chpasswd"
                        self._log_to_terminal(f"Estableciendo contraseña: $ {set_pw_cmd}", "info")
                        run_cmd(set_pw_cmd)
                        # Reintentar desbloqueo
                        run_cmd(f"passwd -u '{username}'")
                        self._log_to_terminal(f"🔓 Usuario '{username}' desbloqueado después de establecer contraseña", "success")
                        self.refresh_users()
                    else:
                        messagebox.showerror("Error", msg)
        else:
            self._log_to_terminal(f"❌ Error: {err}", "error")
            messagebox.showerror("Error", err)

    def _context_menu_user(self, event):
        T = self.T
        item = self.tree_users.identify_row(event.y)
        if item:
            self.tree_users.selection_set(item)
        self.ctx_user.delete(0, "end")
        self.ctx_user.configure(
            bg=T["bg2"], fg=T["text"],
            activebackground=T["accent"], activeforeground="#fff",
            font=("Courier New", 9)
        )
        self.ctx_user.add_command(label="✏  Editar usuario",    command=self._dlg_edit_user)
        self.ctx_user.add_command(label="🔒  Bloquear",          command=self._lock_user)
        self.ctx_user.add_command(label="🔓  Desbloquear",       command=self._unlock_user)
        self.ctx_user.add_separator()
        self.ctx_user.add_command(label="🔑  Cambiar contraseña", command=self._change_password)
        self.ctx_user.add_command(label="👥  Ver grupos",         command=self._show_user_groups)
        self.ctx_user.add_separator()
        self.ctx_user.add_command(label="🗑  Eliminar usuario",   command=self._delete_user,
                                   foreground=T["danger"], activeforeground=T["danger"])
        try:
            self.ctx_user.tk_popup(event.x_root, event.y_root)
        finally:
            self.ctx_user.grab_release()

    def _change_password(self):
        sel = self.tree_users.selection()
        if not sel:
            return
        username = sel[0]
        dlg = PasswordDialog(self, username, self.T)
        self.wait_window(dlg)
        if dlg.result:
            valid, msg = validate_password(dlg.result)
            if not valid:
                messagebox.showerror("Contraseña inválida", msg)
                return

            cmd = f"echo '{username}:{dlg.result}' | chpasswd"
            display_cmd = f"passwd {username}"

            if not is_root():
                self._log_to_terminal(f"ERROR: Se requiere root para cambiar contraseña", "error")
                messagebox.showwarning("Sin privilegios", "Se requiere root.")
                return

            self._log_to_terminal(f"Ejecutando: $ {display_cmd}", "command")
            out, err, rc = run_cmd(cmd)

            if rc == 0:
                self._log_to_terminal(f"✅ Contraseña de '{username}' cambiada exitosamente", "success")
                self._set_status(f"Contraseña de '{username}' cambiada.")
            else:
                self._log_to_terminal(f"❌ Error: {err}", "error")
                messagebox.showerror("Error", err)

    def _show_user_groups(self):
        sel = self.tree_users.selection()
        if not sel:
            return
        username = sel[0]
        groups = get_user_groups(username)
        messagebox.showinfo(
            f"Grupos de '{username}'",
            f"El usuario '{username}' pertenece a:\n\n" + "\n".join(f"  • {g}" for g in groups)
        )

    def _dlg_new_group(self):
        dlg = GroupDialog(self, "Nuevo Grupo", {}, self.T)
        self.wait_window(dlg)
        if dlg.result:
            d = dlg.result
            cmd = f"groupadd"
            if d.get("gid"):    cmd += f" -g '{d['gid']}'"
            if d.get("system"): cmd += " -r"
            if d.get("password"): cmd += f" -p '{d['password']}'"
            cmd += f" '{d['name']}'"

            if not is_root():
                self._log_to_terminal(f"ERROR: Se requiere root para: {cmd}", "error")
                messagebox.showwarning("Sin privilegios", "Se requiere root.")
                return

            self._log_to_terminal(f"Ejecutando: $ {cmd}", "command")
            out, err, rc = run_cmd(cmd)

            if rc == 0:
                if d.get("members"):
                    for member in d["members"].split(","):
                        m = member.strip()
                        if m:
                            m_cmd = f"usermod -aG '{d['name']}' '{m}'"
                            self._log_to_terminal(f"Agregando miembro: $ {m_cmd}", "info")
                            run_cmd(m_cmd)
                self._log_to_terminal(f"✅ Grupo '{d['name']}' creado exitosamente", "success")
                self.refresh_groups()
                self._set_status(f"Grupo '{d['name']}' creado.")
            else:
                self._log_to_terminal(f"❌ Error: {err}", "error")
                messagebox.showerror("Error", err)

    def _dlg_edit_group(self):
        sel = self.tree_groups.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un grupo para editar.")
            return
        gname = sel[0]

        #BLOQUEO DE MODIFICACION DE "nogroup"
        if gname == "nogroup":
            messagebox.showerror("Acción prohibida", self.FIRE_WARNING)
            return

        try:
            g = grp.getgrnam(gname)
            current = {
                "name":    g.gr_name,
                "gid":     g.gr_gid,
                "members": ", ".join(g.gr_mem),
                "passwd":  g.gr_passwd,
            }
        except KeyError:
            messagebox.showerror("Error", f"Grupo '{gname}' no encontrado.")
            return
        dlg = GroupDialog(self, f"Editar Grupo: {gname}", current, self.T, edit=True)
        self.wait_window(dlg)
        if dlg.result:
            d = dlg.result
            cmds = []
            if d.get("new_name") and d["new_name"] != gname:
                cmd = f"groupmod -n '{d['new_name']}' '{gname}'"
                cmds.append(cmd)
            if d.get("gid") and str(d["gid"]) != str(current["gid"]):
                cmd = f"groupmod -g '{d['gid']}' '{gname}'"
                cmds.append(cmd)
            if d.get("password") and d["password"] != current.get("passwd", ""):
                cmd = f"gpasswd '{gname}'"
                cmds.append(f"# {cmd} (contraseña: {d['password']})")

            if d.get("members") is not None:
                new_members = set(m.strip() for m in d["members"].split(",") if m.strip())
                old_members = set(m.strip() for m in current["members"].split(",") if m.strip())
                for m in new_members - old_members:
                    c = f"usermod -aG '{gname}' '{m}'"
                    cmds.append(c)
                for m in old_members - new_members:
                    c = f"gpasswd -d '{m}' '{gname}'"
                    cmds.append(c)

            if not is_root():
                self._log_to_terminal(f"ERROR: Se requiere root para modificar grupo", "error")
                messagebox.showwarning("Sin privilegios", "Se requiere root.")
                return

            errors = []
            for cmd in cmds:
                if cmd.startswith("#"):
                    continue
                self._log_to_terminal(f"Ejecutando: $ {cmd}", "command")
                out, err, rc = run_cmd(cmd)
                if rc != 0:
                    errors.append(err)

            if not errors:
                self._log_to_terminal(f"✅ Grupo '{gname}' modificado exitosamente", "success")
                self.refresh_groups()
                self._set_status(f"Grupo '{gname}' modificado.")
            else:
                self._log_to_terminal(f"❌ Errores: {', '.join(errors)}", "error")
                messagebox.showerror("Error", "\n".join(errors))

    def _delete_group(self):
        sel = self.tree_groups.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un grupo.")
            return
        gname = sel[0]

        #BLOQUEO DE ELIMINACION DE "nogroup"
        if gname == "nogroup":
            messagebox.showerror("Acción prohibida", self.FIRE_WARNING)
            return

        try:
            g = grp.getgrnam(gname)
            if g.gr_gid < 1000:
                if not messagebox.askyesno("Advertencia",
                    f"'{gname}' es un grupo de sistema. ¿Estás seguro de eliminarlo?\n"
                    "Esto podría afectar el funcionamiento del sistema."):
                    return
        except:
            pass

        if not messagebox.askyesno("Eliminar Grupo",
            f"¿Eliminar el grupo '{gname}'?\nEsta acción no se puede deshacer."):
            return
        cmd = f"groupdel '{gname}'"

        if not is_root():
            self._log_to_terminal(f"ERROR: Se requiere root para: {cmd}", "error")
            messagebox.showwarning("Sin privilegios", "Se requiere root.")
            return

        self._log_to_terminal(f"Ejecutando: $ {cmd}", "command")
        out, err, rc = run_cmd(cmd)

        if rc == 0:
            self._log_to_terminal(f"✅ Grupo '{gname}' eliminado", "success")
            self.refresh_groups()
            self._set_status(f"Grupo '{gname}' eliminado.")
        else:
            self._log_to_terminal(f"❌ Error: {err}", "error")
            messagebox.showerror("Error", err)

    def _context_menu_group(self, event):
        T = self.T
        item = self.tree_groups.identify_row(event.y)
        if item:
            self.tree_groups.selection_set(item)
        self.ctx_group.delete(0, "end")
        self.ctx_group.configure(
            bg=T["bg2"], fg=T["text"],
            activebackground=T["accent"], activeforeground="#fff",
            font=("Courier New", 9)
        )
        self.ctx_group.add_command(label="✏  Editar grupo",    command=self._dlg_edit_group)
        self.ctx_group.add_command(label="👥  Ver miembros",    command=self._show_group_members)
        self.ctx_group.add_separator()
        self.ctx_group.add_command(label="🗑  Eliminar grupo",   command=self._delete_group,
                                   foreground=T["danger"], activeforeground=T["danger"])
        try:
            self.ctx_group.tk_popup(event.x_root, event.y_root)
        finally:
            self.ctx_group.grab_release()

    def _show_group_members(self):
        sel = self.tree_groups.selection()
        if not sel:
            return
        gname = sel[0]
        try:
            g = grp.getgrnam(gname)
            members = "\n".join(f"  • {m}" for m in g.gr_mem) if g.gr_mem else "  (sin miembros)"
            messagebox.showinfo(
                f"Miembros de '{gname}'",
                f"Grupo: {gname}\nGID: {g.gr_gid}\n\nMiembros:\n{members}"
            )
        except KeyError:
            messagebox.showerror("Error", f"Grupo '{gname}' no encontrado.")


# ─────────────────────────────────────────────────────────────────────────────
# DIÁLOGO AVANZADO: USUARIO
# ─────────────────────────────────────────────────────────────────────────────

class AdvancedUserDialog(tk.Toplevel):
    def __init__(self, parent, title, data, theme, edit=False):
        super().__init__(parent)
        self.T = theme
        self.result = None
        self.edit = edit
        self.saved_permissions = {}
        self.title(title)
        self.withdraw()  # Ocultar mientras se construye
        self.resizable(True, True)
        self.configure(bg=theme["bg"])
        self._build(data)
        # Forzar cálculo de tamaño real antes de centrar y mostrar
        self.update_idletasks()
        self.update_idletasks()
        self._center()
        self.grab_set()
        self.after(0, self.deiconify)  # Mostrar en el siguiente ciclo del event loop

    def _center(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width()  - self.winfo_width())  // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self, data):
        T = self.T

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        basic_frame = tk.Frame(notebook, bg=T["bg"])
        notebook.add(basic_frame, text="Información Básica")

        # ============================================================
        # PESTAÑA DE CONFIGURACIÓN AVANZADA (CON CONTROL DE ACCESO)
        # ============================================================
        self.advanced_frame = tk.Frame(notebook, bg=T["bg"])
        notebook.add(self.advanced_frame, text="Configuración de cuenta")

        # Variable para controlar si la pestaña está habilitada
        self.advanced_tab_enabled = False

        # Bind para detectar cuando se selecciona la pestaña
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Tooltip para mostrar mensaje al pasar el cursor
        self._create_tooltip(notebook, "Configuración Avanzada")

        hdr = tk.Frame(basic_frame, bg=T["bg2"], pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=self.title(), font=("Courier New", 13, "bold"),
                 bg=T["bg2"], fg=T["accent"], padx=16).pack(anchor="w")

        tk.Frame(basic_frame, height=1, bg=T["border"]).pack(fill="x")

        form = tk.Frame(basic_frame, bg=T["bg"], pady=10)
        form.pack(fill="both", expand=True, padx=4)

        pad = dict(padx=14, pady=5)

        fields = [
            ("Nombre de usuario *", "username"),
            ("Nombre completo (GECOS)", "comment"),
            ("Directorio home", "home"),
            ("Shell", "shell"),
        ]
        if self.edit:
            fields.insert(1, ("Nuevo nombre de usuario", "new_name"))

        self.entries = {}
        for label, key in fields:
            row = tk.Frame(form, bg=T["bg"])
            row.pack(fill="x", **pad)
            tk.Label(row, text=label, font=("Courier New", 9),
                     bg=T["bg"], fg=T["text2"], width=25, anchor="w").pack(side="left")
            e = tk.Entry(row, font=("Courier New", 10),
                         bg=T["entry_bg"], fg=T["entry_fg"],
                         insertbackground=T["accent"],
                         highlightbackground=T["border"],
                         highlightcolor=T["accent"],
                         highlightthickness=1, relief="flat", width=35)
            if data.get(key):
                e.insert(0, str(data[key]))
            e.pack(side="left", ipady=3)
            self.entries[key] = e

        row = tk.Frame(form, bg=T["bg"])
        row.pack(fill="x", **pad)
        tk.Label(row, text="Tipo de cuenta", font=("Courier New", 9),
                 bg=T["bg"], fg=T["text2"], width=25, anchor="w").pack(side="left")

        self.account_type = tk.StringVar(value="Personalizado")
        account_types = [("Personalizado", "Usuario estándar sin privilegios especiales"),
                         ("Desktop User", "Usuario de escritorio con configuraciones básicas"),
                         ("Admin", "Usuario con privilegios de administrador (sudo)")]

        type_frame = tk.Frame(row, bg=T["bg"])
        type_frame.pack(side="left")

        self.expiry_warning = tk.Label(
            type_frame,
            text="⚠ Los usuarios no-Admin expirarán automáticamente después de 90 días",
            font=("Courier New", 7),
            bg=T["bg"], fg=T["warning"]
        )
        self.expiry_warning.pack(anchor="w", padx=(20, 0), pady=(5, 0))

        # Botones de tipo de cuenta con estilo toggle (azul = seleccionado, gris = no seleccionado)
        self._actype_buttons = {}

        def make_actype_callback(atype):
            def select():
                self.account_type.set(atype)
                for t, btn in self._actype_buttons.items():
                    if t == atype:
                        btn.config(bg=T["accent2"], fg="#ffffff", relief="flat")
                    else:
                        btn.config(bg=T["bg3"], fg=T["text2"], relief="flat")
            return select

        for i, (atype, desc) in enumerate(account_types):
            btn_row_at = tk.Frame(type_frame, bg=T["bg"])
            btn_row_at.pack(anchor="w", pady=(4, 0), padx=5)
            btn = tk.Button(
                btn_row_at, text=atype,
                font=("Courier New", 9, "bold"),
                bg=T["bg3"], fg=T["text2"],
                activebackground=T["accent2"], activeforeground="#ffffff",
                relief="flat", cursor="hand2", padx=12, pady=3,
                command=make_actype_callback(atype)
            )
            btn.pack(side="left")
            self._actype_buttons[atype] = btn
            tk.Label(btn_row_at, text=f"  {desc}", font=("Courier New", 7),
                    bg=T["bg"], fg=T["text2"]).pack(side="left", padx=(6, 0))

        if data.get("account_type"):
            self.account_type.set(data["account_type"])

        # Resaltar el botón correspondiente al tipo de cuenta actual
        def _init_actype_buttons():
            current_type = self.account_type.get()
            for t, btn in self._actype_buttons.items():
                if t == current_type:
                    btn.config(bg=T["accent2"], fg="#ffffff")
                else:
                    btn.config(bg=T["bg3"], fg=T["text2"])
        self.after(10, _init_actype_buttons)

        # ============================================================
        # FUNCIÓN PARA MOSTRAR/OCULTAR PERMISOS SEGÚN TIPO DE CUENTA
        # ============================================================
        def on_account_type_change(*args):
            if hasattr(self, 'permisos_switches_frame'):
                if self.account_type.get() == "Personalizado":
                    self.warning_label.pack_forget()
                    self.permisos_switches_frame.pack(fill="both", expand=True, pady=(5, 0))
                else:
                    self.permisos_switches_frame.pack_forget()
                    self.warning_label.pack(anchor="w", padx=14, pady=(2, 10))

        self.account_type.trace_add("write", on_account_type_change)
        # La llamada inicial se hace al final de _build, cuando ya existen todos los widgets

        row = tk.Frame(form, bg=T["bg"])
        row.pack(fill="x", **pad)
        tk.Label(row, text="Contraseña", font=("Courier New", 9),
                 bg=T["bg"], fg=T["text2"], width=25, anchor="w").pack(side="left")

        pw_frame = tk.Frame(row, bg=T["bg"])
        pw_frame.pack(side="left")

        self.password_entry = tk.Entry(pw_frame, font=("Courier New", 10), show="*",
                                       bg=T["entry_bg"], fg=T["entry_fg"],
                                       insertbackground=T["accent"],
                                       highlightbackground=T["border"],
                                       highlightcolor=T["accent"],
                                       highlightthickness=1, relief="flat", width=35)
        self.password_entry.pack(side="left", ipady=3)

        self.gen_btn = tk.Button(pw_frame, text="🔑 Generar", font=("Courier New", 8),
                                bg=T["accent2"], fg="#fff", relief="flat", cursor="hand2",
                                command=self._generate_and_save_password)
        self.gen_btn.pack(side="left", padx=5)

        self.show_pw = tk.BooleanVar(value=False)
        self.toggle_btn = tk.Button(pw_frame, text="👁", font=("Courier New", 8),
                                   bg=T["button_bg"], fg=T["text"], relief="flat", cursor="hand2",
                                   command=self._toggle_password_visibility)
        self.toggle_btn.pack(side="left", padx=2)

        req_frame = tk.Frame(form, bg=T["bg"])
        req_frame.pack(fill="x", padx=14, pady=5)
        tk.Label(req_frame, text="Requisitos de contraseña:", font=("Courier New", 8, "bold"),
                bg=T["bg"], fg=T["text"]).pack(anchor="w")

        requirements = [
            "• Mínimo 8 caracteres",
            "• Al menos una letra mayúscula",
            "• Al menos una letra minúscula",
            "• Al menos un número",
            "• Al menos un carácter especial (!@#$%^&*)",
            "• Evitar palabras comunes o patrones débiles"
        ]
        for req in requirements:
            tk.Label(req_frame, text=req, font=("Courier New", 7),
                    bg=T["bg"], fg=T["text2"]).pack(anchor="w", padx=15)

        self.create_home = tk.BooleanVar(value=True)
        if not self.edit:
            chk_row = tk.Frame(form, bg=T["bg"])
            chk_row.pack(fill="x", padx=14, pady=4)
            tk.Checkbutton(
                chk_row, text="Crear directorio home (-m)",
                variable=self.create_home,
                bg=T["bg"], fg=T["text"],
                selectcolor=T["accent"],
                activebackground=T["bg"],
                activeforeground=T["text"],
                font=("Courier New", 9)
            ).pack(anchor="w")

        # ============================================================
        # PESTAÑA CONFIGURACIÓN AVANZADA (CORREGIDA)
        # ============================================================

        # Frame principal para la pestaña
        main_adv_frame = tk.Frame(self.advanced_frame, bg=T["bg"])
        main_adv_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # ============================================================
        # PARTE SUPERIOR: CAMPOS BÁSICOS
        # ============================================================
        campos_frame = tk.Frame(main_adv_frame, bg=T["bg"])
        campos_frame.pack(fill="x", pady=(0, 10))

        pad = dict(padx=14, pady=3)

        # UID
        row = tk.Frame(campos_frame, bg=T["bg"])
        row.pack(fill="x", **pad)
        tk.Label(row, text="UID (dejar vacío para auto):", font=("Courier New", 9),
                bg=T["bg"], fg=T["text2"], width=30, anchor="w").pack(anchor="w")
        self.uid_entry = tk.Entry(row, font=("Courier New", 10),
                                bg=T["entry_bg"], fg=T["entry_fg"],
                                insertbackground=T["accent"],
                                highlightbackground=T["border"],
                                highlightcolor=T["accent"],
                                highlightthickness=1, relief="flat", width=35)
        if data.get("uid"):
            self.uid_entry.insert(0, str(data["uid"]))
        self.uid_entry.pack(anchor="w", ipady=3, pady=(2, 0))

        # Obtener todos los grupos del sistema para los comboboxes
        all_system_groups = sorted([g.gr_name for g in grp.getgrall()])

        def _make_autocomplete_combo(parent, width=28):
            """Combobox con filtrado/autocompletado de grupos del sistema"""
            var = tk.StringVar()
            combo = ttk.Combobox(parent, textvariable=var,
                                 values=all_system_groups, width=width)
            combo.configure(font=("Courier New", 10))
            def _on_key(event):
                typed = var.get()
                if typed:
                    filtered = [g for g in all_system_groups
                                if g.lower().startswith(typed.lower())]
                    combo['values'] = filtered if filtered else all_system_groups
                else:
                    combo['values'] = all_system_groups
            combo.bind("<KeyRelease>", _on_key)
            return combo, var

        # Grupo principal — combobox con autocompletado
        row = tk.Frame(campos_frame, bg=T["bg"])
        row.pack(fill="x", **pad)
        tk.Label(row, text="Grupo principal:", font=("Courier New", 9),
                bg=T["bg"], fg=T["text2"], width=30, anchor="w").pack(anchor="w")

        gp_input_row = tk.Frame(row, bg=T["bg"])
        gp_input_row.pack(anchor="w", pady=(2, 0))

        self._gp_combo, self._gp_var = _make_autocomplete_combo(gp_input_row, width=28)
        self._gp_combo.pack(side="left", ipady=3)

        # Solo permite UN grupo principal — listbox con un elemento
        self._gp_listbox = tk.Listbox(row, font=("Courier New", 9),
                                      bg=T["entry_bg"], fg=T["entry_fg"],
                                      selectbackground=T["accent2"],
                                      height=2, width=30, relief="flat",
                                      highlightbackground=T["border"],
                                      highlightthickness=1)
        self._gp_listbox.pack(anchor="w", pady=(2, 0))

        if data.get("group"):
            self._gp_listbox.insert(tk.END, data["group"])

        def _set_gp():
            val = self._gp_var.get().strip()
            if val:
                self._gp_listbox.delete(0, tk.END)
                self._gp_listbox.insert(tk.END, val)
                self._gp_var.set("")
                self._gp_combo['values'] = all_system_groups

        def _del_gp():
            sel = self._gp_listbox.curselection()
            if sel:
                self._gp_listbox.delete(sel[0])

        self._gp_combo.bind("<Return>", lambda e: _set_gp())

        tk.Button(gp_input_row, text="✓ Establecer", font=("Courier New", 8),
                  bg=T["accent2"], fg="#fff", relief="flat", cursor="hand2",
                  padx=6, command=_set_gp).pack(side="left", padx=(4, 2))
        tk.Button(gp_input_row, text="✕ Limpiar", font=("Courier New", 8),
                  bg=T["button_bg"], fg=T["text2"], relief="flat", cursor="hand2",
                  padx=6, command=_del_gp).pack(side="left", padx=2)

        # Grupos adicionales — combobox con autocompletado + lista dinámica
        row = tk.Frame(campos_frame, bg=T["bg"])
        row.pack(fill="x", **pad)
        tk.Label(row, text="Grupos adicionales:", font=("Courier New", 9),
                bg=T["bg"], fg=T["text2"], width=30, anchor="w").pack(anchor="w")

        ga_input_row = tk.Frame(row, bg=T["bg"])
        ga_input_row.pack(anchor="w", pady=(2, 0))

        self._ga_combo, self._ga_var = _make_autocomplete_combo(ga_input_row, width=28)
        self._ga_combo.pack(side="left", ipady=3)

        self._ga_listbox = tk.Listbox(row, font=("Courier New", 9),
                                      bg=T["entry_bg"], fg=T["entry_fg"],
                                      selectbackground=T["accent2"],
                                      height=4, width=30, relief="flat",
                                      highlightbackground=T["border"],
                                      highlightthickness=1)
        self._ga_listbox.pack(anchor="w", pady=(2, 0))

        # Precargar grupos adicionales
        if data.get("groups"):
            existing = [g.strip() for g in data["groups"].split(",") if g.strip()]
            for g in existing:
                self._ga_listbox.insert(tk.END, g)

        def _add_ga():
            val = self._ga_var.get().strip()
            if val and val not in self._ga_listbox.get(0, tk.END):
                self._ga_listbox.insert(tk.END, val)
                self._ga_var.set("")
                self._ga_combo['values'] = all_system_groups

        def _del_ga():
            sel = self._ga_listbox.curselection()
            if sel:
                self._ga_listbox.delete(sel[0])

        self._ga_combo.bind("<Return>", lambda e: _add_ga())

        tk.Button(ga_input_row, text="＋ Agregar", font=("Courier New", 8),
                  bg=T["accent2"], fg="#fff", relief="flat", cursor="hand2",
                  padx=6, command=_add_ga).pack(side="left", padx=(4, 2))
        tk.Button(ga_input_row, text="✕ Eliminar", font=("Courier New", 8),
                  bg=T["button_bg"], fg=T["text2"], relief="flat", cursor="hand2",
                  padx=6, command=_del_ga).pack(side="left", padx=2)

        # Fecha expiración
        row = tk.Frame(campos_frame, bg=T["bg"])
        row.pack(fill="x", **pad)
        tk.Label(row, text="Fecha expiración (YYYY-MM-DD o never):", font=("Courier New", 9),
                bg=T["bg"], fg=T["text2"], width=30, anchor="w").pack(anchor="w")
        self.expires_entry = tk.Entry(row, font=("Courier New", 10),
                                    bg=T["entry_bg"], fg=T["entry_fg"],
                                    insertbackground=T["accent"],
                                    highlightbackground=T["border"],
                                    highlightcolor=T["accent"],
                                    highlightthickness=1, relief="flat", width=35)
        if data.get("expires"):
            self.expires_entry.insert(0, data["expires"])
        elif data.get("privileges", {}).get("expires") and data["privileges"]["expires"] != "never":
            self.expires_entry.insert(0, data["privileges"]["expires"])
        self.expires_entry.pack(anchor="w", ipady=3, pady=(2, 0))

        # Días de inactividad
        row = tk.Frame(campos_frame, bg=T["bg"])
        row.pack(fill="x", **pad)
        tk.Label(row, text="Días de inactividad (-1 para nunca):", font=("Courier New", 9),
                bg=T["bg"], fg=T["text2"], width=30, anchor="w").pack(anchor="w")
        self.inactive_entry = tk.Entry(row, font=("Courier New", 10),
                                    bg=T["entry_bg"], fg=T["entry_fg"],
                                    insertbackground=T["accent"],
                                    highlightbackground=T["border"],
                                    highlightcolor=T["accent"],
                                    highlightthickness=1, relief="flat", width=35)
        if data.get("inactive"):
            self.inactive_entry.insert(0, data["inactive"])
        elif data.get("privileges", {}).get("inactive_days") and data["privileges"]["inactive_days"] != "never":
            self.inactive_entry.insert(0, data["privileges"]["inactive_days"])
        self.inactive_entry.pack(anchor="w", ipady=3, pady=(2, 0))

        # Separador visual
        tk.Frame(main_adv_frame, height=1, bg=T["border"]).pack(fill="x", pady=5)

        # ============================================================
        # PARTE INFERIOR: PERMISOS AVANZADOS
        # ============================================================

        # Título (SIEMPRE visible)
        self.permisos_title_frame = tk.Frame(main_adv_frame, bg=T["bg"])
        self.permisos_title_frame.pack(anchor="w", pady=(5, 5))

        self.permisos_label = tk.Label(self.permisos_title_frame, text="🔐 PERMISOS ESPECIALES",
                                       font=("Courier New", 10, "bold"),
                                       bg=T["bg"], fg=T["accent"])
        self.permisos_label.pack(side="left")

        # Mensaje de advertencia (se muestra debajo del título cuando no es Personalizado)
        self.warning_label = tk.Label(main_adv_frame,
                                      text="⚠ Para modificar PERMISOS ESPECIALES, primero seleccione el tipo de cuenta 'Personalizado'",
                                      font=("Courier New", 9),
                                      bg=T["bg"], fg=T["warning"])

        # Contenedor de switches (SOLO visible para Personalizado)
        self.permisos_switches_frame = tk.Frame(main_adv_frame, bg=T["bg"])

        # Contenedor principal para permisos (sin scroll)
        permisos_container = tk.Frame(self.permisos_switches_frame, bg=T["bg"])
        permisos_container.pack(fill="both", expand=True)

        # Lista de permisos con SWITCHES deslizantes estilo moderno
        self.perm_vars = {}

        permisos = [
            ("plugdev",      "Acceder a dispositivos de almacenamiento externo"),
            ("lpadmin",      "Configurar impresoras"),
            ("dialout",      "Conectar a Internet (módem)"),
            ("netdev",       "Conectar a redes WiFi/Ethernet"),
            ("adm",          "Monitorear logs del sistema"),
            ("fax",          "Enviar/recibir faxes"),
            ("sambashare",   "Compartir archivos en red local"),
            ("audio",        "Usar dispositivos de audio"),
            ("cdrom",        "Usar unidades CD-ROM"),
            ("floppy",       "Usar disqueteras"),
            ("scanner",      "Usar escáneres"),
            ("tape",         "Usar unidades de cinta"),
            ("video",        "Usar dispositivos de video"),
        ]

        # Organizar en 2 columnas
        col1 = tk.Frame(permisos_container, bg=T["bg"])
        col1.pack(side="left", fill="both", expand=True, padx=10)
        col2 = tk.Frame(permisos_container, bg=T["bg"])
        col2.pack(side="left", fill="both", expand=True, padx=10)

        def create_switch(parent, var, width=52, height=28):
            """Crea un interruptor deslizante con animación suave (estilo iOS/Android)"""
            canvas = tk.Canvas(parent, width=width, height=height, bg=T["bg"], highlightthickness=0)

            # Dimensiones
            radius = height // 1
            knob_size = height - 6
            off_x = 3
            on_x = width - knob_size - 3

            # Función para rectángulo redondeado
            def create_rounded_rectangle(x1, y1, x2, y2, radius, **kwargs):
                points = []
                points.extend([x1 + radius, y1, x2 - radius, y1,
                            x2 - radius, y1, x2, y1,
                            x2, y1 + radius])
                points.extend([x2, y1 + radius, x2, y2 - radius,
                            x2, y2 - radius, x2, y2,
                            x2 - radius, y2])
                points.extend([x2 - radius, y2, x1 + radius, y2,
                            x1 + radius, y2, x1, y2,
                            x1, y2 - radius])
                points.extend([x1, y2 - radius, x1, y1 + radius,
                            x1, y1 + radius, x1, y1,
                            x1 + radius, y1])
                return canvas.create_polygon(points, smooth=True, **kwargs)

            # Track (fondo)
            track = create_rounded_rectangle(2, 2, width-2, height-2, radius,
                                            fill=T["bg3"], outline="", width=0)

            # Knob (círculo deslizante)
            knob = canvas.create_oval(off_x, 3, off_x + knob_size, height - 3,
                                    fill=T["disabled_fg"], outline=T["border"], width=1)

            def animate_to(target_x, steps=8):
                """Animación suave del knob"""
                current_coords = canvas.coords(knob)
                current_x = current_coords[0]
                distance = target_x - current_x
                step = distance / steps

                def animate_step(step_count=0):
                    if step_count < steps:
                        new_x = current_x + step * (step_count + 1)
                        canvas.coords(knob, new_x, 3, new_x + knob_size, height - 3)
                        canvas.after(8, lambda: animate_step(step_count + 1))
                    else:
                        canvas.coords(knob, target_x, 3, target_x + knob_size, height - 3)

                animate_step()

            def update_switch(with_animation=True):
                if var.get():
                    if with_animation:
                        animate_to(on_x)
                    else:
                        canvas.coords(knob, on_x, 3, on_x + knob_size, height - 3)
                    canvas.itemconfig(track, fill=T["accent"])
                    canvas.itemconfig(knob, fill=T["select_fg"], outline=T["accent2"])
                else:
                    if with_animation:
                        animate_to(off_x)
                    else:
                        canvas.coords(knob, off_x, 3, off_x + knob_size, height - 3)
                    canvas.itemconfig(track, fill=T["bg3"])
                    canvas.itemconfig(knob, fill=T["disabled_fg"], outline=T["border"])

            def toggle_switch(event=None):
                var.set(not var.get())
                update_switch(True)

            canvas.bind("<Button-1>", toggle_switch)

            # Hover effects
            def on_enter(event):
                canvas.config(cursor="hand2")

            canvas.bind("<Enter>", on_enter)

            # Estado inicial
            update_switch(False)

            # Devolver el canvas y un método para actualizar
            return canvas, update_switch

        # En la parte donde creas los switches, cambia:
        for i, (grupo, desc) in enumerate(permisos):
            target = col1 if i % 2 == 0 else col2
            frame = tk.Frame(target, bg=T["bg"])
            frame.pack(anchor="w", pady=6)

            var = tk.BooleanVar(value=False)
            self.perm_vars[grupo] = var

            # Crear switch moderno
            switch, update_func = create_switch(frame, var)  # <-- Cambio aquí
            switch.pack(side="left")

            # Guardar referencia para actualización posterior
            if not hasattr(self, 'switches'):
                self.switches = {}
            self.switches[grupo] = type('Switch', (), {'update_switch': update_func, 'canvas': switch})()

            # Label del permiso
            lbl = tk.Label(frame, text=desc, font=("Courier New", 9),
                        bg=T["bg"], fg=T["text"], cursor="hand2")
            lbl.pack(side="left", padx=10)

            # Hacer que el label también toggle el switch
            def make_lbl_callback(v=var):
                def toggle(event=None):
                    v.set(not v.get())
                return toggle

            lbl.bind("<Button-1>", make_lbl_callback())

            # Cargar estado actual si estamos editando
            if self.edit and data.get("privileges", {}).get("groups"):
                if grupo in data["privileges"]["groups"]:
                    var.set(True)

        # ============================================================
        # BOTONES (DEBEN ESTAR FUERA DE LA PESTAÑA, EN EL DIÁLOGO PRINCIPAL)
        # ============================================================
        tk.Frame(self, height=1, bg=T["border"]).pack(fill="x", pady=4)

        btn_row = tk.Frame(self, bg=T["bg"], pady=10)
        btn_row.pack(fill="x", padx=14)

        tk.Button(
            btn_row, text="Cancelar", font=("Courier New", 9),
            bg=T["button_bg"], fg=T["text2"],
            relief="flat", cursor="hand2", padx=14, pady=5,
            command=self.destroy
        ).pack(side="right", padx=4)

        action = "Guardar cambios" if self.edit else "Crear usuario"
        tk.Button(
            btn_row, text=action, font=("Courier New", 9, "bold"),
            bg=T["accent2"], fg="#fff",
            relief="flat", cursor="hand2", padx=14, pady=5,
            command=self._submit
        ).pack(side="right", padx=4)

        # Configurar el combobox de shells
        shells = get_available_shells()
        if "shell" in self.entries:
            # Guardar el valor actual del Entry antes de reemplazarlo
            current_shell = self.entries["shell"].get()
            shell_var = tk.StringVar(value=current_shell)
            # Desempaquetar el Entry original
            self.entries["shell"].pack_forget()
            # Crear Combobox con el valor actual preseleccionado
            shell_combo = ttk.Combobox(form, textvariable=shell_var, values=shells, width=33)
            if current_shell and current_shell not in shells:
                shell_combo['values'] = [current_shell] + list(shells)
            shell_combo.set(current_shell)
            shell_combo.pack(side="left", ipady=3)
            self.entries["shell"] = shell_combo

        # Inicializar visibilidad de permisos y cargar estado guardado
        on_account_type_change()
        self._load_saved_permissions()

    def _create_tooltip(self, notebook, tab_text):
        """Crea un tooltip para la pestaña Configuración Avanzada"""
        def on_enter(event):
            if not self.advanced_tab_enabled and self.account_type.get() != "Personalizado":
                # Crear tooltip flotante
                self.tooltip = tk.Toplevel(self)
                self.tooltip.wm_overrideredirect(True)
                self.tooltip.configure(bg=self.T["bg2"])

                x = event.x_root + 10
                y = event.y_root + 10

                label = tk.Label(self.tooltip,
                            text="⚠ Para usar esta pestaña, primero asegúrese de que su tipo de cuenta es 'Personalizado'",
                            font=("Courier New", 9),
                            bg=self.T["bg2"],
                            fg=self.T["accent"],
                            padx=10, pady=5,
                            relief="solid",
                            borderwidth=1)
                label.pack()

                self.tooltip.geometry(f"+{x}+{y}")
                self.tooltip.after(2000, self.tooltip.destroy)

        def on_leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()

        # Buscar la pestaña por su texto y bindear eventos
        def bind_to_tab():
            for child in notebook.winfo_children():
                if isinstance(child, tk.Frame):
                    # Buscar el label de la pestaña
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Label) and subchild.cget("text") == tab_text:
                            subchild.bind("<Enter>", on_enter)
                            subchild.bind("<Leave>", on_leave)
                            return
            self.after(100, bind_to_tab)

        bind_to_tab()

    def _on_tab_changed(self, event):
        """Callback cuando se cambia de pestaña"""
        notebook = event.widget
        selected = notebook.index(notebook.select())
        tab_text = notebook.tab(selected, "text")

        # if tab_text == "Configuración de cuenta":
        #     if self.account_type.get() != "Personalizado":
        #         # Mostrar mensaje de error y volver a la pestaña anterior
        #         messagebox.showwarning(
        #             "Acceso Denegado",
        #             "Para usar la pestaña 'Configuración de cuenta', primero debe seleccionar el tipo de cuenta 'Personalizado'.\n\n"
        #             "Cambie el tipo de cuenta en la pestaña 'Información Básica'.",
        #             parent=self
        #         )
        #         # Volver a la pestaña de Información Básica
        #         notebook.select(0)
        #     else:
        #         # Cargar los permisos guardados cuando se accede a la pestaña
        #         self._load_saved_permissions()

    def _load_saved_permissions(self):
        """Carga los permisos guardados desde self.saved_permissions"""
        if hasattr(self, 'saved_permissions') and self.saved_permissions:
            for grupo, activo in self.saved_permissions.items():
                if grupo in self.perm_vars:
                    self.perm_vars[grupo].set(activo)
                    # Actualizar visualmente el switch
                    if hasattr(self, 'switches') and grupo in self.switches:
                        self.switches[grupo].update_switch()

    def _toggle_password_visibility(self):
        if self.show_pw.get():
            self.password_entry.config(show="*")
            self.show_pw.set(False)
            self.toggle_btn.config(text="👁")
        else:
            self.password_entry.config(show="")
            self.show_pw.set(True)
            self.toggle_btn.config(text="🙈")

    def _generate_and_save_password(self):
        password = generate_password()
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

        self.password_entry.config(show="")
        self.show_pw.set(True)
        self.toggle_btn.config(text="🙈")

        self.grab_release()

        def ask_save():
            try:
                self.lift()
                self.focus_force()

                if messagebox.askyesno("Guardar contraseña",
                    "¿Deseas guardar esta contraseña en un archivo de texto?\n\n"
                    "Se abrirá un diálogo para elegir la ubicación.", parent=self):
                    username = self.entries["username"].get() if "username" in self.entries else ""
                    save_password_to_file(password, username)
            finally:
                self.grab_set()
                self.lift()
                self.focus_force()

        self.after(100, ask_save)

    def _submit(self):
        d = {k: e.get().strip() if hasattr(e, 'get') else e.get() for k, e in self.entries.items()}

        d["password"] = self.password_entry.get().strip()

        if not d.get("username") and not self.edit:
            messagebox.showerror("Error", "El nombre de usuario es obligatorio.", parent=self)
            return

        # Validar shell
        shell_val = d.get("shell", "").strip()
        if not shell_val:
            messagebox.showerror("Error", "Debes seleccionar una shell.", parent=self)
            return

        # VALIDACIÓN DE CONTRASEÑA
        if self.edit:
            # MODO EDICIÓN: la contraseña es OPCIONAL
            # Solo validar si el usuario escribió algo en el campo
            if d.get("password") and d["password"] != "":
                valid, msg = validate_password(d["password"])
                if not valid:
                    messagebox.showerror("Contraseña inválida", msg, parent=self)
                    return
        else:
            # MODO CREACIÓN: la contraseña es OBLIGATORIA
            if not d.get("password") or d["password"] == "":
                messagebox.showerror("Error", "La contraseña es obligatoria para crear un usuario.", parent=self)
                return
            valid, msg = validate_password(d["password"])
            if not valid:
                messagebox.showerror("Contraseña inválida", msg, parent=self)
                return

        d["create_home"] = getattr(self, "create_home", tk.BooleanVar(value=True)).get()
        d["account_type"] = self.account_type.get()
        d["uid"] = self.uid_entry.get().strip() if self.uid_entry.get().strip() else None
        # Leer grupo principal del listbox
        gp_items = list(self._gp_listbox.get(0, tk.END))
        d["group"] = gp_items[0] if gp_items else ""
        # Leer grupos adicionales del listbox
        ga_items = list(self._ga_listbox.get(0, tk.END))
        d["groups"] = ",".join(ga_items) if ga_items else ""
        d["expires"] = self.expires_entry.get().strip() if self.expires_entry.get().strip() else None
        d["inactive"] = self.inactive_entry.get().strip() if self.inactive_entry.get().strip() else None

        self.result = d
        # Guardar permisos seleccionados ANTES de destruir el diálogo
        self.permisos_seleccionados = [g for g, v in self.perm_vars.items() if v.get()]
        self.grab_release()
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# DIÁLOGO: GRUPO
# ─────────────────────────────────────────────────────────────────────────────

class GroupDialog(tk.Toplevel):
    def __init__(self, parent, title, data, theme, edit=False):
        super().__init__(parent)
        self.T = theme
        self.result = None
        self.edit = edit
        self.title(title)
        self.withdraw()  # Ocultar mientras se construye
        self.resizable(True, True)
        self.configure(bg=theme["bg"])
        self._build(data)
        self.update_idletasks()
        self.update_idletasks()
        self._center()
        self.grab_set()
        self.after(0, self.deiconify)

    def _center(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width()  - self.winfo_width())  // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self, data):
        T = self.T
        pad = dict(padx=14, pady=5)

        hdr = tk.Frame(self, bg=T["bg2"], pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=self.title(), font=("Courier New", 13, "bold"),
                 bg=T["bg2"], fg=T["accent"], padx=16).pack(anchor="w")
        tk.Frame(self, height=1, bg=T["border"]).pack(fill="x")

        form = tk.Frame(self, bg=T["bg"], pady=10)
        form.pack(fill="both", expand=True, padx=4)

        # Campos básicos (sin "members" que se maneja aparte)
        basic_fields = [("Nombre del grupo *", "name"), ("GID (dejar vacío para auto)", "gid"),
                        ("Contraseña del grupo (opcional)", "password")]
        if self.edit:
            basic_fields.insert(1, ("Nuevo nombre", "new_name"))

        self.entries = {}
        for label, key in basic_fields:
            row = tk.Frame(form, bg=T["bg"])
            row.pack(fill="x", **pad)
            tk.Label(row, text=label, font=("Courier New", 9),
                     bg=T["bg"], fg=T["text2"], width=28, anchor="w").pack(side="left")
            e = tk.Entry(row, font=("Courier New", 10),
                         bg=T["entry_bg"], fg=T["entry_fg"],
                         insertbackground=T["accent"],
                         highlightbackground=T["border"],
                         highlightcolor=T["accent"],
                         highlightthickness=1, relief="flat", width=35)
            val = data.get(key, "")
            if val:
                e.insert(0, str(val))
            e.pack(side="left", ipady=3)
            self.entries[key] = e

        # ── Miembros: combobox con autocompletado + lista dinámica ──
        all_users = sorted([p.pw_name for p in pwd.getpwall() if p.pw_uid >= 1000])

        mb_frame = tk.Frame(form, bg=T["bg"])
        mb_frame.pack(fill="x", **pad)
        tk.Label(mb_frame, text="Miembros:", font=("Courier New", 9),
                 bg=T["bg"], fg=T["text2"], width=28, anchor="w").pack(anchor="w")

        mb_input_row = tk.Frame(mb_frame, bg=T["bg"])
        mb_input_row.pack(anchor="w", pady=(2, 0))

        self._mb_var = tk.StringVar()
        self._mb_combo = ttk.Combobox(mb_input_row, textvariable=self._mb_var,
                                      values=all_users, width=28)
        self._mb_combo.configure(font=("Courier New", 10))

        def _on_mb_key(event):
            typed = self._mb_var.get()
            if typed:
                filtered = [u for u in all_users if u.lower().startswith(typed.lower())]
                self._mb_combo['values'] = filtered if filtered else all_users
            else:
                self._mb_combo['values'] = all_users
        self._mb_combo.bind("<KeyRelease>", _on_mb_key)
        self._mb_combo.pack(side="left", ipady=3)

        self._mb_listbox = tk.Listbox(mb_frame, font=("Courier New", 9),
                                      bg=T["entry_bg"], fg=T["entry_fg"],
                                      selectbackground=T["accent2"],
                                      height=4, width=30, relief="flat",
                                      highlightbackground=T["border"],
                                      highlightthickness=1)
        self._mb_listbox.pack(anchor="w", pady=(2, 0))

        # Precargar miembros actuales
        if data.get("members"):
            for m in [m.strip() for m in data["members"].split(",") if m.strip()]:
                self._mb_listbox.insert(tk.END, m)

        def _add_mb():
            val = self._mb_var.get().strip()
            if val and val not in self._mb_listbox.get(0, tk.END):
                self._mb_listbox.insert(tk.END, val)
                self._mb_var.set("")
                self._mb_combo['values'] = all_users

        def _del_mb():
            sel = self._mb_listbox.curselection()
            if sel:
                self._mb_listbox.delete(sel[0])

        self._mb_combo.bind("<Return>", lambda e: _add_mb())

        tk.Button(mb_input_row, text="＋ Agregar", font=("Courier New", 8),
                  bg=T["accent2"], fg="#fff", relief="flat", cursor="hand2",
                  padx=6, command=_add_mb).pack(side="left", padx=(4, 2))
        tk.Button(mb_input_row, text="✕ Eliminar", font=("Courier New", 8),
                  bg=T["button_bg"], fg=T["text2"], relief="flat", cursor="hand2",
                  padx=6, command=_del_mb).pack(side="left", padx=2)
        # ── fin miembros ──

        self.is_system = tk.BooleanVar(value=False)
        if not self.edit:
            chk_row = tk.Frame(form, bg=T["bg"])
            chk_row.pack(fill="x", padx=14, pady=4)
            tk.Checkbutton(
                chk_row, text="Grupo de sistema (-r, GID < 1000)",
                variable=self.is_system,
                bg=T["bg"], fg=T["text"], selectcolor=T["accent"],
                activebackground=T["bg"], activeforeground=T["text"],
                font=("Courier New", 9)
            ).pack(anchor="w")

        tk.Frame(self, height=1, bg=T["border"]).pack(fill="x", pady=4)

        btn_row = tk.Frame(self, bg=T["bg"], pady=10)
        btn_row.pack(fill="x", padx=14)

        tk.Button(
            btn_row, text="Cancelar", font=("Courier New", 9),
            bg=T["button_bg"], fg=T["text2"],
            relief="flat", cursor="hand2", padx=14, pady=5,
            command=self.destroy
        ).pack(side="right", padx=4)

        action = "Guardar cambios" if self.edit else "Crear grupo"
        tk.Button(
            btn_row, text=action, font=("Courier New", 9, "bold"),
            bg=T["accent2"], fg="#fff",
            relief="flat", cursor="hand2", padx=14, pady=5,
            command=self._submit
        ).pack(side="right", padx=4)

    def _submit(self):
        d = {k: e.get().strip() for k, e in self.entries.items()}
        if not d.get("name") and not self.edit:
            messagebox.showerror("Error", "El nombre del grupo es obligatorio.", parent=self)
            return
        # Leer miembros del listbox
        d["members"] = ",".join(self._mb_listbox.get(0, tk.END))
        d["system"] = self.is_system.get() if hasattr(self, 'is_system') else False
        self.result = d
        self.destroy()

# ─────────────────────────────────────────────────────────────────────────────
# DIÁLOGO: CONTRASEÑA
# ─────────────────────────────────────────────────────────────────────────────

class PasswordDialog(tk.Toplevel):
    def __init__(self, parent, username, theme):
        super().__init__(parent)
        self.T = theme
        self.result = None
        self.title(f"Cambiar contraseña: {username}")
        self.resizable(False, False)
        self.configure(bg=theme["bg"])
        self.grab_set()
        self._build(username)
        self._center()

    def _center(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width()  - self.winfo_width())  // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self, username):
        T = self.T
        hdr = tk.Frame(self, bg=T["bg2"], pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"🔑  Contraseña para: {username}",
                 font=("Courier New", 11, "bold"), bg=T["bg2"], fg=T["accent"], padx=16).pack(anchor="w")
        tk.Frame(self, height=1, bg=T["border"]).pack(fill="x")

        form = tk.Frame(self, bg=T["bg"], pady=14)
        form.pack(padx=20, pady=8, fill="x")

        self.show_pw = tk.BooleanVar(value=False)

        for label, key in [("Nueva contraseña", "pw1"), ("Confirmar contraseña", "pw2")]:
            row = tk.Frame(form, bg=T["bg"])
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=("Courier New", 9),
                     bg=T["bg"], fg=T["text2"], width=20, anchor="w").pack(side="left")

            frame = tk.Frame(row, bg=T["bg"])
            frame.pack(side="left")

            e = tk.Entry(frame, show="*", font=("Courier New", 10),
                         bg=T["entry_bg"], fg=T["entry_fg"],
                         insertbackground=T["accent"],
                         highlightbackground=T["border"],
                         highlightcolor=T["accent"],
                         highlightthickness=1, relief="flat", width=28)
            e.pack(side="left", ipady=3)
            setattr(self, f"entry_{key}", e)

            if key == "pw1":
                self.toggle_btn = tk.Button(frame, text="👁", font=("Courier New", 8),
                                           bg=T["button_bg"], fg=T["text"], relief="flat", cursor="hand2",
                                           command=self._toggle_visibility)
                self.toggle_btn.pack(side="left", padx=2)

                self.gen_btn = tk.Button(frame, text="🔑 Generar", font=("Courier New", 8),
                                        bg=T["accent2"], fg="#fff", relief="flat", cursor="hand2",
                                        command=self._generate_password)
                self.gen_btn.pack(side="left", padx=2)

        req_frame = tk.Frame(form, bg=T["bg"])
        req_frame.pack(fill="x", pady=8)
        tk.Label(req_frame, text="Requisitos:", font=("Courier New", 8, "bold"),
                bg=T["bg"], fg=T["text"]).pack(anchor="w")

        requirements = [
            "• Mínimo 8 caracteres",
            "• Mayúscula, minúscula, número y carácter especial",
            "• Evitar palabras comunes"
        ]
        for req in requirements:
            tk.Label(req_frame, text=req, font=("Courier New", 7),
                    bg=T["bg"], fg=T["text2"]).pack(anchor="w", padx=15)

        tk.Frame(self, height=1, bg=T["border"]).pack(fill="x", pady=4)

        btn_row = tk.Frame(self, bg=T["bg"], pady=10)
        btn_row.pack(fill="x", padx=14)

        tk.Button(btn_row, text="Cancelar", font=("Courier New", 9),
                  bg=T["button_bg"], fg=T["text2"], relief="flat", cursor="hand2",
                  padx=14, pady=5, command=self.destroy).pack(side="right", padx=4)
        tk.Button(btn_row, text="Cambiar contraseña", font=("Courier New", 9, "bold"),
                  bg=T["accent2"], fg="#fff", relief="flat", cursor="hand2",
                  padx=14, pady=5, command=self._submit).pack(side="right", padx=4)

    def _toggle_visibility(self):
        if self.show_pw.get():
            self.entry_pw1.config(show="*")
            self.show_pw.set(False)
            self.toggle_btn.config(text="👁")
        else:
            self.entry_pw1.config(show="")
            self.show_pw.set(True)
            self.toggle_btn.config(text="🙈")

    def _generate_password(self):
        password = generate_password()
        self.entry_pw1.delete(0, tk.END)
        self.entry_pw1.insert(0, password)
        self.entry_pw2.delete(0, tk.END)
        self.entry_pw2.insert(0, password)

        self.entry_pw1.config(show="")
        self.show_pw.set(True)
        self.toggle_btn.config(text="🙈")

        self.after(500, lambda: messagebox.showinfo("Contraseña generada",
                    "La contraseña se ha generado y está visible.\n"
                    "Puedes copiarla antes de cerrar.", parent=self))

    def _submit(self):
        pw1 = self.entry_pw1.get()
        pw2 = self.entry_pw2.get()

        valid, msg = validate_password(pw1)
        if not valid:
            messagebox.showerror("Contraseña inválida", msg, parent=self)
            return

        if pw1 != pw2:
            messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=self)
            return

        self.result = pw1
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not is_root():
        print("\n⚠  ADVERTENCIA: FENAdmin necesita permisos de root para ejecutar modificaciones.")
        print("   Lanzando en modo LECTURA. Usa: sudo python3 fenadmin.py\n")
    app = FENAdmin()
    app.mainloop()
