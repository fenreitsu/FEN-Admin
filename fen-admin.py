#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FENAdmin - Gestor de Usuarios y Grupos v0.3.1
Creador: @fenreitsu
Compatibilidad: Linux (Kali Linux, Ubuntu, Debian, etc.)
Mejoras: Grupos completos, tipos de cuenta, validación de contraseña, generador, configuración avanzada
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
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
from functools import partial

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE LOGOS
# ─────────────────────────────────────────────────────────────────────────────

# Ruta donde están las imágenes (ajústala según tu estructura)

# Obtener la ruta del directorio donde está el script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Construir rutas completas a las imágenes
LOGO_LIGHT = os.path.join(SCRIPT_DIR, "resources", "logo", "fenreitsu.png")
LOGO_DARK = os.path.join(SCRIPT_DIR, "resources", "logo", "fenreitsu-white.png")

# Tamaño del logo en la interfaz (ancho, alto)
LOGO_SIZE = (48, 48)  # Ajusta según necesites

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
        "notif_bg":     "#0d1117",
        "notif_border": "#1f6feb",
        "label_fg":     "#e6edf3",
        "disabled_fg":  "#484f58",
        "tag_sys":      "#161b22",
        "tag_sys_fg":   "#8b949e",
        "scrollbar":    "#30363d",
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
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES DE SISTEMA
# ─────────────────────────────────────────────────────────────────────────────

def run_cmd(cmd, shell=True):
    """Ejecuta un comando y devuelve (stdout, stderr, returncode)."""
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
    """Valida una contraseña según criterios de seguridad"""
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

    # Palabras comunes y patrones débiles
    weak_patterns = [
        'password', '123456', 'qwerty', 'abc123', 'admin', 'root',
        'toor', 'iloveyou', 'monkey', 'dragon', 'master', 'sunshine'
    ]

    if password.lower() in weak_patterns:
        return False, "La contraseña es demasiado común o débil."

    # Evitar secuencias repetitivas
    if re.search(r'(.)\1{3,}', password):
        return False, "Evite secuencias repetitivas de caracteres."

    return True, "OK"

def generate_password(length=16, use_special=True):
    """Genera una contraseña segura aleatoria"""
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?" if use_special else ""

    all_chars = uppercase + lowercase + digits + special

    # Asegurar al menos uno de cada tipo
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
    ]

    if use_special:
        password.append(secrets.choice(special))

    # Completar el resto
    password.extend(secrets.choice(all_chars) for _ in range(length - len(password)))

    # Mezclar
    random.shuffle(password)

    return ''.join(password)

def save_password_to_file(password, username=""):
    """Guarda la contraseña generada en un archivo"""
    # Asegurar que la ventana padre tenga el foco
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
    """Devuelve lista de TODOS los grupos del sistema"""
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
    """Obtiene todos los privilegios/configuraciones de un usuario"""
    privileges = {}

    # Obtener información de /etc/passwd
    try:
        p = pwd.getpwnam(username)
        privileges['uid'] = p.pw_uid
        privileges['gid'] = p.pw_gid
        privileges['gecos'] = p.pw_gecos
        privileges['home'] = p.pw_dir
        privileges['shell'] = p.pw_shell
    except KeyError:
        pass

    # Verificar si es sudoer
    out, _, _ = run_cmd(f"groups {username}")
    privileges['groups'] = out.split(':')[1].strip().split() if ':' in out else out.strip().split()
    privileges['is_sudoer'] = 'sudo' in privileges['groups'] or 'wheel' in privileges['groups']

    # Verificar expiración de cuenta
    out, _, _ = run_cmd(f"chage -l {username} 2>/dev/null | grep 'Account expires'")
    privileges['expires'] = out.split(':')[1].strip() if out and ':' in out else 'never'

    # Verificar si la contraseña expira
    out, _, _ = run_cmd(f"chage -l {username} 2>/dev/null | grep 'Password expires'")
    privileges['passwd_expires'] = out.split(':')[1].strip() if out and ':' in out else 'never'

    # Verificar días de inactividad
    out, _, _ = run_cmd(f"chage -l {username} 2>/dev/null | grep 'Inactive'")
    privileges['inactive_days'] = out.split(':')[1].strip() if out and ':' in out else 'never'

    return privileges

def get_users():
    """Devuelve lista de TODOS los usuarios del sistema"""
    users = []
    for p in pwd.getpwall():
        # Determinar si es usuario de sistema (UID < 1000)
        is_system = p.pw_uid < 1000

        # Verificar si la cuenta está bloqueada
        # Método: verificar si la contraseña tiene '!' o '*' al inicio en /etc/shadow
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
            # Si no se puede leer shadow, intentar con passwd -S
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
    """Devuelve lista de grupos a los que pertenece un usuario"""
    try:
        out, _, _ = run_cmd(f"groups {username}")
        # El formato es "username : group1 group2 group3"
        if ':' in out:
            groups = out.split(':')[1].strip().split()
        else:
            groups = out.strip().split()
        return groups
    except Exception:
        return []

def get_available_shells():
    """Obtiene lista de shells disponibles"""
    shells = ['/bin/bash', '/bin/sh', '/bin/dash', '/bin/zsh', '/bin/fish',
              '/sbin/nologin', '/usr/sbin/nologin', '/bin/rbash']

    # Verificar shells realmente disponibles
    available = []
    for shell in shells:
        if os.path.exists(shell):
            available.append(shell)

    return available if available else ['/bin/bash']

# ─────────────────────────────────────────────────────────────────────────────
# APLICACIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

class FENAdmin(tk.Tk):
    def __init__(self):
        super().__init__()

        self.theme_name = tk.StringVar(value="dark")
        self.T = THEMES["dark"]
        self.notifications = []
        self.show_system = tk.BooleanVar(value=False)
        self._filter_text = tk.StringVar()
        self._filter_text.trace_add("write", lambda *_: self._apply_filter())

        self.title("FENAdmin v0.3.1 - by @fenreitsu")
        self.geometry("1280x780")
        self.minsize(900, 600)
        self.configure(bg=self.T["bg"])

        self._set_icon()
        self._set_window_icon()
        self._build_ui()
        self._apply_theme()
        self.refresh_users()

        self.bind("<Configure>", self._on_resize)

    def _load_logo_image(self):
        """Carga la imagen del logo según el tema actual"""
        try:
            # Elegir la imagen según el tema
            logo_path = LOGO_DARK if self.theme_name.get() == "dark" else LOGO_LIGHT

            if os.path.exists(logo_path):
                # Cargar imagen
                original_image = tk.PhotoImage(file=logo_path)

                # Redimensionar si es necesario
                desired_width, desired_height = LOGO_SIZE
                if original_image.width() != desired_width or original_image.height() != desired_height:
                    # Calcular factor de subsample (aproximado)
                    w_factor = max(1, original_image.width() // desired_width)
                    h_factor = max(1, original_image.height() // desired_height)
                    self.logo_image = original_image.subsample(w_factor, h_factor)
                else:
                    self.logo_image = original_image

                # Aplicar al label
                self.logo_label.config(image=self.logo_image)
            else:
                # Si no existe la imagen, usar texto como fallback
                self.logo_label.config(image='', text='⬡', font=("Courier New", 24))
        except Exception as e:
            print(f"Error cargando logo: {e}")
            self.logo_label.config(image='', text='⬡', font=("Courier New", 24))

    def _set_icon(self):
        """Establece el icono de la ventana principal"""
        try:
            # Cargar el icono según el tema actual
            icon_path = LOGO_DARK if self.theme_name.get() == "dark" else LOGO_LIGHT
            if os.path.exists(icon_path):
                icon_image = tk.PhotoImage(file=icon_path)
                # Redimensionar si es necesario
                if icon_image.width() > 64 or icon_image.height() > 64:
                    icon_image = icon_image.subsample(
                        icon_image.width() // 32,
                        icon_image.height() // 32
                    )
                self.iconphoto(True, icon_image)
                # Guardar referencia para evitar garbage collection
                self.icon_image = icon_image
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")
            # Icono por defecto si falla
            try:
                default_icon = tk.PhotoImage(width=32, height=32)
                self.iconphoto(True, default_icon)
            except:
                pass

    def _set_window_icon(self):
        """Establece el icono de la ventana (barra de tareas)"""
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
        self.topbar = tk.Frame(self, height=54)
        self.topbar.pack(fill="x", side="top")
        self.topbar.pack_propagate(False)

        # Frame para contener logo y texto
        logo_frame = tk.Frame(self.topbar)
        logo_frame.pack(side="left", padx=10, pady=5)

        # Logo imagen
        self.logo_image = None
        self.logo_label = tk.Label(logo_frame, image=None)
        self.logo_label.pack(side="left", padx=(0, 10))

        # Texto del logo
        self.lbl_logo = tk.Label(
            logo_frame,
            text="FENAdmin v0.3.1",
            font=("Courier New", 18, "bold"),
        )
        self.lbl_logo.pack(side="left")

        # Cargar el logo según el tema actual
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

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(self.main_frame, width=180)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self._build_sidebar()

        self.sep_side = tk.Frame(self.main_frame, width=1)
        self.sep_side.pack(side="left", fill="y")

        self.content = tk.Frame(self.main_frame)
        self.content.pack(side="left", fill="both", expand=True)

        self.notif_panel = tk.Frame(self.main_frame, width=310)
        self.notif_panel.pack(side="right", fill="y")
        self.notif_panel.pack_propagate(False)

        self.sep_notif = tk.Frame(self.main_frame, width=1)
        self.sep_notif.pack(side="right", fill="y")

        self._build_notif_panel()

        self._frames = {}
        for name in ("users", "groups"):
            f = tk.Frame(self.content)
            self._frames[name] = f
            f.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_users_view(self._frames["users"])
        self._build_groups_view(self._frames["groups"])

        self._show_frame("users")

        self.statusbar = tk.Frame(self, height=26)
        self.statusbar.pack(fill="x", side="bottom")
        self.statusbar.pack_propagate(False)

        self.status_label = tk.Label(
            self.statusbar, text="  FENAdmin listo.",
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

    def _build_notif_panel(self):
        T = self.T

        header = tk.Frame(self.notif_panel, height=44)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="⚡  Actividad / Comandos",
            font=("Courier New", 10, "bold"), anchor="w", padx=12, pady=10
        ).pack(side="left")

        btn_clear = tk.Button(
            header, text="✕ Limpiar",
            font=("Courier New", 8), relief="flat", cursor="hand2",
            padx=6, pady=2,
            command=self._clear_notifications
        )
        btn_clear.pack(side="right", padx=8, pady=8)
        self.btn_notif_clear = btn_clear

        tk.Frame(self.notif_panel, height=1).pack(fill="x")

        self.notif_canvas = tk.Canvas(
            self.notif_panel, highlightthickness=0
        )
        notif_scroll = tk.Scrollbar(
            self.notif_panel, orient="vertical",
            command=self.notif_canvas.yview
        )
        self.notif_canvas.configure(yscrollcommand=notif_scroll.set)
        notif_scroll.pack(side="right", fill="y")
        self.notif_canvas.pack(fill="both", expand=True)

        self.notif_inner = tk.Frame(self.notif_canvas)
        self.notif_window = self.notif_canvas.create_window(
            (0, 0), window=self.notif_inner, anchor="nw"
        )
        self.notif_inner.bind(
            "<Configure>",
            lambda e: self.notif_canvas.configure(
                scrollregion=self.notif_canvas.bbox("all")
            )
        )
        self.notif_canvas.bind(
            "<Configure>",
            lambda e: self.notif_canvas.itemconfig(
                self.notif_window, width=e.width
            )
        )
        self.notif_canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.notif_canvas.yview_scroll(-1*(e.delta//120), "units")
        )

        self._add_notification(
            "info", "Sistema iniciado",
            "FENAdmin v0.3.1 listo. Ejecute acciones para ver los comandos equivalentes aquí.",
            ""
        )

    def _build_users_view(self, parent):
        T = self.T

        top_toolbar = tk.Frame(parent, height=52)
        top_toolbar.pack(fill="x", pady=(0, 0))
        top_toolbar.pack_propagate(False)

        tk.Label(
            top_toolbar, text="Gestión de Usuarios",
            font=("Courier New", 14, "bold"), anchor="w", padx=16, pady=10
        ).pack(side="left")

        actions = [
            ("😁 Nuevo Usuario",  self._dlg_new_user,    "accent"),
            ("🗑 Eliminar",       self._delete_user,     "danger"),
            ("🔒 Bloquear",       self._lock_user,       "warning"),
            ("🔓 Desbloquear",    self._unlock_user,     "success"),
        ]

        action_frame = tk.Frame(top_toolbar)
        action_frame.pack(side="right", padx=10)

        for label, cmd, style in actions:
            btn = self._styled_btn(action_frame, label, cmd, style)
            btn.pack(side="left", padx=3, pady=10)

        filter_bar = tk.Frame(parent, height=45)
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
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

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

        self.tree_users.bind("<Double-1>", lambda e: self._dlg_edit_user())
        self.tree_users.bind("<Button-3>", self._context_menu_user)

        self.ctx_user = tk.Menu(self, tearoff=0)

        info_bar = tk.Frame(parent, height=28)
        info_bar.pack(fill="x", side="bottom")
        info_bar.pack_propagate(False)
        self.lbl_user_count = tk.Label(
            info_bar, text="", font=("Courier New", 8), anchor="w", padx=10
        )
        self.lbl_user_count.pack(side="left")

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

            # Determinar tipo de cuenta
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

    def _determine_account_type(self, username):
        """Determina el tipo de cuenta basado en grupos y privilegios"""
        groups = get_user_groups(username)

        if 'sudo' in groups or 'wheel' in groups or 'admin' in groups:
            return "Admin"
        elif username.startswith(('user', 'alumno', 'estudiante')):
            return "Desktop User"
        else:
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

    def _build_groups_view(self, parent):
        T = self.T

        toolbar = tk.Frame(parent, height=52)
        toolbar.pack(fill="x", pady=(0, 0))
        toolbar.pack_propagate(False)

        tk.Label(
            toolbar, text="Gestión de Grupos",
            font=("Courier New", 14, "bold"), anchor="w", padx=16, pady=10
        ).pack(side="left")

        actions = [
            ("＋ Nuevo Grupo",  self._dlg_new_group,   "accent"),
            ("🗑 Eliminar",     self._delete_group,    "danger"),
            ("✏ Editar",       self._dlg_edit_group,  "warning"),
        ]
        for label, cmd, style in reversed(actions):
            btn = self._styled_btn(toolbar, label, cmd, style)
            btn.pack(side="right", padx=4, pady=10)

        # Barra de búsqueda para grupos
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
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

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

        self.tree_groups.bind("<Double-1>", lambda e: self._dlg_edit_group())
        self.tree_groups.bind("<Button-3>", self._context_menu_group)

        self.ctx_group = tk.Menu(self, tearoff=0)

        info_bar = tk.Frame(parent, height=28)
        info_bar.pack(fill="x", side="bottom")
        info_bar.pack_propagate(False)
        self.lbl_group_count = tk.Label(
            info_bar, text="", font=("Courier New", 8), anchor="w", padx=10
        )
        self.lbl_group_count.pack(side="left")

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

        groups = get_all_groups()  # Usar la nueva función que obtiene TODOS los grupos
        show_sys = self.show_system.get()
        search_text = getattr(self, 'group_search_entry', None)
        search_term = search_text.get().lower() if search_text else ""

        count = 0
        for g in groups:
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
        self.wait_window(dlg)
        if dlg.result:
            d = dlg.result

            # Validar contraseña si se proporcionó
            if d.get("password"):
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
            if d.get("expires"):  cmd += f" -e '{d['expires']}'"
            if d.get("inactive"): cmd += f" -f '{d['inactive']}'"
            cmd += f" '{d['username']}'"

            if not is_root():
                self._add_notification("warning", "Sin privilegios",
                    "Necesitas ejecutar FENAdmin como root (sudo) para crear usuarios.",
                    f"# sudo {cmd}")
                messagebox.showwarning("Sin privilegios", "Se requiere ejecutar como root (sudo).")
                return

            out, err, rc = run_cmd(cmd)
            if rc == 0:
                if d.get("password"):
                    pw_cmd = f"echo '{d['username']}:{d['password']}' | chpasswd"
                    run_cmd(pw_cmd)

                # Configurar privilegios de sudo si es Admin
                if d.get("account_type") == "Admin":
                    run_cmd(f"usermod -aG sudo '{d['username']}' 2>/dev/null || usermod -aG wheel '{d['username']}'")

                self._add_notification("success", f"Usuario '{d['username']}' creado",
                    f"Se creó el usuario tipo {d.get('account_type', 'Personalizado')}.", cmd)
                self.refresh_users()
                self._set_status(f"Usuario '{d['username']}' creado correctamente.")
            else:
                self._add_notification("danger", f"Error al crear '{d['username']}'", err, cmd)
                messagebox.showerror("Error", f"No se pudo crear el usuario:\n{err}")

    def _dlg_edit_user(self):
        sel = self.tree_users.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un usuario para editar.")
            return
        username = sel[0]
        try:
            p = pwd.getpwnam(username)
            privileges = get_user_privileges(username)
            current = {
                "username": p.pw_name,
                "comment":  p.pw_gecos,
                "home":     p.pw_dir,
                "shell":    p.pw_shell,
                "uid":      p.pw_uid,
                "gid":      p.pw_gid,
                "privileges": privileges,
            }
        except KeyError:
            messagebox.showerror("Error", f"Usuario '{username}' no encontrado.")
            return

        dlg = AdvancedUserDialog(self, f"Editar Usuario: {username}", current, self.T, edit=True)
        self.wait_window(dlg)
        if dlg.result:
            d = dlg.result

            if d.get("password"):
                valid, msg = validate_password(d["password"])
                if not valid:
                    messagebox.showerror("Contraseña inválida", msg)
                    return

            cmd = f"usermod"
            if d.get("comment") != current["comment"]: cmd += f" -c '{d['comment']}'"
            if d.get("home") != current["home"]:       cmd += f" -d '{d['home']}' -m"
            if d.get("shell") != current["shell"]:     cmd += f" -s '{d['shell']}'"
            if d.get("new_name") and d["new_name"] != username: cmd += f" -l '{d['new_name']}'"
            if d.get("groups"):                         cmd += f" -aG '{d['groups']}'"
            if d.get("uid") and str(d["uid"]) != str(current["uid"]): cmd += f" -u '{d['uid']}'"
            if d.get("expires"):                        cmd += f" -e '{d['expires']}'"
            if d.get("inactive"):                       cmd += f" -f '{d['inactive']}'"
            cmd += f" '{username}'"

            if not is_root():
                self._add_notification("warning", "Sin privilegios",
                    "Necesitas ejecutar FENAdmin como root para modificar usuarios.", f"# sudo {cmd}")
                messagebox.showwarning("Sin privilegios", "Se requiere ejecutar como root (sudo).")
                return

            out, err, rc = run_cmd(cmd)
            if rc == 0:
                if d.get("password"):
                    run_cmd(f"echo '{username}:{d['password']}' | chpasswd")

                # Configurar/remover sudo según tipo de cuenta
                if d.get("account_type") == "Admin":
                    run_cmd(f"usermod -aG sudo '{username}' 2>/dev/null || usermod -aG wheel '{username}'")
                else:
                    run_cmd(f"deluser '{username}' sudo 2>/dev/null || gpasswd -d '{username}' wheel 2>/dev/null")

                self._add_notification("success", f"Usuario '{username}' modificado",
                    "Los datos del usuario fueron actualizados.", cmd)
                self.refresh_users()
                self._set_status(f"Usuario '{username}' modificado.")
            else:
                self._add_notification("danger", f"Error modificando '{username}'", err, cmd)
                messagebox.showerror("Error", f"No se pudo modificar:\n{err}")

    def _delete_user(self):
        sel = self.tree_users.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un usuario.")
            return
        username = sel[0]
        resp = messagebox.askyesnocancel(
            "Eliminar Usuario",
            f"¿Eliminar el usuario '{username}'?\n\n"
            "Pulsa SÍ para eliminar también el directorio home.\n"
            "Pulsa NO para eliminar solo el usuario.\n"
            "Pulsa CANCELAR para abortar."
        )
        if resp is None:
            return
        remove_home = resp

        cmd = f"userdel{' -r' if remove_home else ''} '{username}'"
        if not is_root():
            self._add_notification("warning", "Sin privilegios", "Se requiere root.", f"# sudo {cmd}")
            messagebox.showwarning("Sin privilegios", "Se requiere ejecutar como root (sudo).")
            return

        out, err, rc = run_cmd(cmd)
        if rc == 0:
            self._add_notification("danger", f"Usuario '{username}' eliminado",
                f"{'También se eliminó el directorio home.' if remove_home else 'El directorio home se conservó.'}", cmd)
            self.refresh_users()
            self._set_status(f"Usuario '{username}' eliminado.")
        else:
            self._add_notification("danger", f"Error eliminando '{username}'", err, cmd)
            messagebox.showerror("Error", f"No se pudo eliminar:\n{err}")

    def _lock_user(self):
        sel = self.tree_users.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un usuario.")
            return
        username = sel[0]
        cmd = f"usermod -L '{username}'"
        if not is_root():
            self._add_notification("warning", "Sin privilegios", "Se requiere root.", f"# sudo {cmd}")
            messagebox.showwarning("Sin privilegios", "Se requiere root.")
            return
        out, err, rc = run_cmd(cmd)
        if rc == 0:
            self._add_notification("warning", f"Usuario '{username}' bloqueado",
                "El usuario no podrá iniciar sesión hasta ser desbloqueado.", cmd)
            self.refresh_users()
            self._set_status(f"Usuario '{username}' bloqueado.")
        else:
            messagebox.showerror("Error", err)

    def _unlock_user(self):
        sel = self.tree_users.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un usuario.")
            return
        username = sel[0]
        cmd = f"usermod -U '{username}'"
        if not is_root():
            self._add_notification("warning", "Sin privilegios", "Se requiere root.", f"# sudo {cmd}")
            messagebox.showwarning("Sin privilegios", "Se requiere root.")
            return
        out, err, rc = run_cmd(cmd)
        if rc == 0:
            self._add_notification("success", f"Usuario '{username}' desbloqueado",
                "El usuario puede iniciar sesión nuevamente.", cmd)
            self.refresh_users()
            self._set_status(f"Usuario '{username}' desbloqueado.")
        else:
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
            display_cmd = f"passwd {username}  # (contraseña no mostrada)"
            if not is_root():
                self._add_notification("warning", "Sin privilegios", "Se requiere root.", f"# sudo passwd {username}")
                messagebox.showwarning("Sin privilegios", "Se requiere root.")
                return
            out, err, rc = run_cmd(cmd)
            if rc == 0:
                self._add_notification("success", f"Contraseña de '{username}' cambiada",
                    "La contraseña fue actualizada correctamente.", display_cmd)
                self._set_status(f"Contraseña de '{username}' cambiada.")
            else:
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
                self._add_notification("warning", "Sin privilegios", "Se requiere root.", f"# sudo {cmd}")
                messagebox.showwarning("Sin privilegios", "Se requiere root.")
                return
            out, err, rc = run_cmd(cmd)
            if rc == 0:
                if d.get("members"):
                    for member in d["members"].split(","):
                        m = member.strip()
                        if m:
                            m_cmd = f"usermod -aG '{d['name']}' '{m}'"
                            run_cmd(m_cmd)
                self._add_notification("success", f"Grupo '{d['name']}' creado", "", cmd)
                self.refresh_groups()
                self._set_status(f"Grupo '{d['name']}' creado.")
            else:
                self._add_notification("danger", f"Error creando grupo", err, cmd)
                messagebox.showerror("Error", err)

    def _dlg_edit_group(self):
        sel = self.tree_groups.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un grupo para editar.")
            return
        gname = sel[0]
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
                self._add_notification("warning", "Sin privilegios", "Se requiere root.",
                    "\n".join(f"# sudo {c}" for c in cmds))
                messagebox.showwarning("Sin privilegios", "Se requiere root.")
                return

            errors = []
            for cmd in cmds:
                if cmd.startswith("#"):
                    continue
                out, err, rc = run_cmd(cmd)
                if rc != 0:
                    errors.append(err)

            if not errors:
                self._add_notification("success", f"Grupo '{gname}' modificado", "",
                    "\n".join(cmds))
                self.refresh_groups()
                self._set_status(f"Grupo '{gname}' modificado.")
            else:
                self._add_notification("danger", f"Errores modificando grupo", "\n".join(errors),
                    "\n".join(cmds))
                messagebox.showerror("Error", "\n".join(errors))

    def _delete_group(self):
        sel = self.tree_groups.selection()
        if not sel:
            messagebox.showinfo("Selección", "Selecciona un grupo.")
            return
        gname = sel[0]

        # Verificar si es un grupo de sistema
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
            self._add_notification("warning", "Sin privilegios", "Se requiere root.", f"# sudo {cmd}")
            messagebox.showwarning("Sin privilegios", "Se requiere root.")
            return
        out, err, rc = run_cmd(cmd)
        if rc == 0:
            self._add_notification("danger", f"Grupo '{gname}' eliminado", "", cmd)
            self.refresh_groups()
            self._set_status(f"Grupo '{gname}' eliminado.")
        else:
            messagebox.showerror("Error", err)

    def _add_notification(self, level, title, message, command=""):
        T = self.T
        colors = {
            "success": T["success"],
            "warning": T["warning"],
            "danger":  T["danger"],
            "info":    T["info"],
        }
        color = colors.get(level, T["info"])
        icons = {"success": "✔", "warning": "⚠", "danger": "✖", "info": "ℹ"}
        icon = icons.get(level, "•")

        now = datetime.datetime.now().strftime("%H:%M:%S")

        card = tk.Frame(
            self.notif_inner,
            relief="flat", bd=0, pady=0
        )
        card.pack(fill="x", padx=8, pady=4)

        accent_bar = tk.Frame(card, width=3)
        accent_bar.configure(bg=color)
        accent_bar.pack(side="left", fill="y")

        inner = tk.Frame(card, padx=8, pady=6)
        inner.pack(side="left", fill="both", expand=True)

        header_row = tk.Frame(inner)
        header_row.pack(fill="x")

        tk.Label(
            header_row, text=f"{icon}  {title}",
            font=("Courier New", 9, "bold"),
            fg=color, anchor="w"
        ).pack(side="left")

        tk.Label(
            header_row, text=now,
            font=("Courier New", 8),
            anchor="e"
        ).pack(side="right")

        if message:
            tk.Label(
                inner, text=message,
                font=("Courier New", 8),
                anchor="w", wraplength=250, justify="left"
            ).pack(fill="x")

        if command:
            cmd_frame = tk.Frame(inner, pady=3)
            cmd_frame.pack(fill="x")
            tk.Label(
                cmd_frame, text="$ " + command,
                font=("Courier New", 8, "bold"),
                anchor="w", wraplength=250, justify="left"
            ).pack(fill="x", padx=4, pady=2)

        self._theme_widget(card)
        self._theme_widget(inner)
        self._theme_widget(header_row)
        if command:
            self._theme_widget(cmd_frame)

        for w in inner.winfo_children():
            if isinstance(w, tk.Label):
                if w.cget("fg") not in (color, T["text2"]):
                    w.configure(bg=T["bg3"])
            w.configure(bg=T["bg3"])
        inner.configure(bg=T["bg3"])
        card.configure(bg=T["bg3"])
        accent_bar.configure(bg=color)
        header_row.configure(bg=T["bg3"])

        for w in inner.winfo_children():
            try:
                if isinstance(w, tk.Label):
                    cur_fg = w.cget("fg")
                    if cur_fg not in (color,):
                        w.configure(fg=T["text2"])
                    w.configure(bg=T["bg3"])
                elif isinstance(w, tk.Frame):
                    w.configure(bg=T["bg3"])
                    for ww in w.winfo_children():
                        try:
                            ww.configure(bg=T["bg3"])
                            if isinstance(ww, tk.Label):
                                ww.configure(fg=T["accent"])
                        except Exception:
                            pass
            except Exception:
                pass

        tk.Frame(self.notif_inner, height=1).pack(fill="x", padx=8)
        self._theme_widget(self.notif_inner.winfo_children()[-1])

        self.notif_canvas.update_idletasks()
        self.notif_canvas.yview_moveto(1.0)

        self.notifications.append(card)

    def _clear_notifications(self):
        for w in self.notif_inner.winfo_children():
            w.destroy()
        self.notifications.clear()
        self._add_notification("info", "Panel limpiado", "Historial de acciones borrado.", "")

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
        # Actualizar el logo cuando cambia el tema
        self._load_logo_image()

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

        # ACTUALIZAR COLOR DEL TEXTO DEL LOGO
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
            elif cls == "Canvas":
                widget.configure(bg=T["notif_bg"])
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

    def _on_resize(self, event):
        pass

    def _sort_tree(self, tree, col, reverse):
        data = [(tree.set(k, col), k) for k in tree.get_children("")]
        try:
            data.sort(key=lambda t: int(t[0]), reverse=reverse)
        except ValueError:
            data.sort(reverse=reverse)
        for i, (_, k) in enumerate(data):
            tree.move(k, "", i)
        tree.heading(col, command=partial(self._sort_tree, tree, col, not reverse))


# ─────────────────────────────────────────────────────────────────────────────
# DIÁLOGO AVANZADO: USUARIO (con tipos de cuenta y generador de contraseña)
# ─────────────────────────────────────────────────────────────────────────────

class AdvancedUserDialog(tk.Toplevel):
    def __init__(self, parent, title, data, theme, edit=False):
        super().__init__(parent)
        self.T = theme
        self.result = None
        self.edit = edit
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=theme["bg"])
        self.grab_set()
        self._build(data)
        self._center()

    def _center(self):
        self.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width()  - self.winfo_width())  // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build(self, data):
        T = self.T

        # Crear notebook para pestañas
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Pestaña: Información básica
        basic_frame = tk.Frame(notebook, bg=T["bg"])
        notebook.add(basic_frame, text="Información Básica")

        # Pestaña: Configuración Avanzada
        advanced_frame = tk.Frame(notebook, bg=T["bg"])
        notebook.add(advanced_frame, text="Configuración Avanzada")

        # --- Pestaña Básica ---
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

        # Tipo de cuenta
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

        for i, (atype, desc) in enumerate(account_types):
            rb = tk.Radiobutton(type_frame, text=atype, variable=self.account_type, value=atype,
                               bg=T["bg"], fg=T["text"], selectcolor=T["accent"],
                               activebackground=T["bg"], activeforeground=T["text"])
            rb.pack(anchor="w", padx=5)
            # Tooltip-like description
            tk.Label(type_frame, text=f"  ({desc})", font=("Courier New", 7),
                    bg=T["bg"], fg=T["text2"]).pack(anchor="w", padx=(20, 0))

        if data.get("account_type"):
            self.account_type.set(data["account_type"])

        # Contraseña
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

        # Botón generar contraseña
        self.gen_btn = tk.Button(pw_frame, text="🔑 Generar", font=("Courier New", 8),
                                bg=T["accent2"], fg="#fff", relief="flat", cursor="hand2",
                                command=self._generate_and_save_password)
        self.gen_btn.pack(side="left", padx=5)

        # Botón mostrar/ocultar
        self.show_pw = tk.BooleanVar(value=False)
        self.toggle_btn = tk.Button(pw_frame, text="👁", font=("Courier New", 8),
                                   bg=T["button_bg"], fg=T["text"], relief="flat", cursor="hand2",
                                   command=self._toggle_password_visibility)
        self.toggle_btn.pack(side="left", padx=2)

        # Requisitos de contraseña
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

        # Checkbutton crear home
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

        # --- Pestaña Avanzada ---
        adv_form = tk.Frame(advanced_frame, bg=T["bg"], pady=10)
        adv_form.pack(fill="both", expand=True, padx=4)

        # UID
        row = tk.Frame(adv_form, bg=T["bg"])
        row.pack(fill="x", **pad)
        tk.Label(row, text="UID (dejar vacío para auto)", font=("Courier New", 9),
                 bg=T["bg"], fg=T["text2"], width=25, anchor="w").pack(side="left")
        self.uid_entry = tk.Entry(row, font=("Courier New", 10),
                                  bg=T["entry_bg"], fg=T["entry_fg"],
                                  insertbackground=T["accent"],
                                  highlightbackground=T["border"],
                                  highlightcolor=T["accent"],
                                  highlightthickness=1, relief="flat", width=35)
        if data.get("uid"):
            self.uid_entry.insert(0, str(data["uid"]))
        self.uid_entry.pack(side="left", ipady=3)

        # Grupo principal
        row = tk.Frame(adv_form, bg=T["bg"])
        row.pack(fill="x", **pad)
        tk.Label(row, text="Grupo principal", font=("Courier New", 9),
                 bg=T["bg"], fg=T["text2"], width=25, anchor="w").pack(side="left")
        self.group_entry = tk.Entry(row, font=("Courier New", 10),
                                    bg=T["entry_bg"], fg=T["entry_fg"],
                                    insertbackground=T["accent"],
                                    highlightbackground=T["border"],
                                    highlightcolor=T["accent"],
                                    highlightthickness=1, relief="flat", width=35)
        if data.get("group"):
            self.group_entry.insert(0, data["group"])
        self.group_entry.pack(side="left", ipady=3)

        # Grupos adicionales
        row = tk.Frame(adv_form, bg=T["bg"])
        row.pack(fill="x", **pad)
        tk.Label(row, text="Grupos adicionales (separados por coma)", font=("Courier New", 9),
                 bg=T["bg"], fg=T["text2"], width=25, anchor="w").pack(side="left")
        self.groups_entry = tk.Entry(row, font=("Courier New", 10),
                                     bg=T["entry_bg"], fg=T["entry_fg"],
                                     insertbackground=T["accent"],
                                     highlightbackground=T["border"],
                                     highlightcolor=T["accent"],
                                     highlightthickness=1, relief="flat", width=35)
        if data.get("groups"):
            self.groups_entry.insert(0, data["groups"])
        self.groups_entry.pack(side="left", ipady=3)

        # Fecha de expiración
        row = tk.Frame(adv_form, bg=T["bg"])
        row.pack(fill="x", **pad)
        tk.Label(row, text="Fecha expiración (YYYY-MM-DD o never)", font=("Courier New", 9),
                 bg=T["bg"], fg=T["text2"], width=25, anchor="w").pack(side="left")
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
        self.expires_entry.pack(side="left", ipady=3)

        # Días de inactividad
        row = tk.Frame(adv_form, bg=T["bg"])
        row.pack(fill="x", **pad)
        tk.Label(row, text="Días de inactividad (-1 para nunca)", font=("Courier New", 9),
                 bg=T["bg"], fg=T["text2"], width=25, anchor="w").pack(side="left")
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
        self.inactive_entry.pack(side="left", ipady=3)

        tk.Frame(self, height=1, bg=T["border"]).pack(fill="x", pady=4)

        # Botones
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

        # Shell options
        shells = get_available_shells()
        if "shell" in self.entries:
            shell_combo = ttk.Combobox(form, textvariable=self.entries["shell"], values=shells, width=33)
            shell_combo.pack(side="left", ipady=3)
            self.entries["shell"].pack_forget()
            self.entries["shell"] = shell_combo

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

        # Mostrar la contraseña temporalmente
        self.password_entry.config(show="")
        self.show_pw.set(True)
        self.toggle_btn.config(text="🙈")

        # Liberar el grab temporalmente para evitar bloqueos
        self.grab_release()

        # Usar 'after' para dar tiempo a que se actualice la interfaz
        def ask_save():
            try:
                # Asegurar que la ventana esté visible
                self.lift()
                self.focus_force()

                if messagebox.askyesno("Guardar contraseña",
                    "¿Deseas guardar esta contraseña en un archivo de texto?\n\n"
                    "Se abrirá un diálogo para elegir la ubicación.", parent=self):
                    username = self.entries["username"].get() if "username" in self.entries else ""
                    save_password_to_file(password, username)
            finally:
                # Restaurar el grab después de cerrar los diálogos
                self.grab_set()
                # Devolver el foco al diálogo
                self.lift()
                self.focus_force()

        self.after(100, ask_save)

    def _submit(self):
        d = {k: e.get().strip() if hasattr(e, 'get') else e.get() for k, e in self.entries.items()}

        if not d.get("username") and not self.edit:
            messagebox.showerror("Error", "El nombre de usuario es obligatorio.", parent=self)
            return

        # Validar contraseña si se proporcionó
        if d.get("password"):
            valid, msg = validate_password(d["password"])
            if not valid:
                messagebox.showerror("Contraseña inválida", msg, parent=self)
                return

        d["create_home"] = getattr(self, "create_home", tk.BooleanVar(value=True)).get()
        d["account_type"] = self.account_type.get()
        d["uid"] = self.uid_entry.get().strip() if self.uid_entry.get().strip() else None
        d["group"] = self.group_entry.get().strip()
        d["groups"] = self.groups_entry.get().strip()
        d["expires"] = self.expires_entry.get().strip() if self.expires_entry.get().strip() else None
        d["inactive"] = self.inactive_entry.get().strip() if self.inactive_entry.get().strip() else None

        self.result = d

        # Liberar grab antes de destruir
        self.grab_release()
        self.destroy()

# ─────────────────────────────────────────────────────────────────────────────
# DIÁLOGO: GRUPO (mejorado)
# ─────────────────────────────────────────────────────────────────────────────

class GroupDialog(tk.Toplevel):
    def __init__(self, parent, title, data, theme, edit=False):
        super().__init__(parent)
        self.T = theme
        self.result = None
        self.edit = edit
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=theme["bg"])
        self.grab_set()
        self._build(data)
        self._center()

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

        fields = [("Nombre del grupo *", "name"), ("GID (dejar vacío para auto)", "gid"),
                  ("Miembros (separados por coma)", "members"), ("Contraseña del grupo (opcional)", "password")]
        if self.edit:
            fields.insert(1, ("Nuevo nombre", "new_name"))

        self.entries = {}
        for label, key in fields:
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
        d["system"] = getattr(self, "is_system", tk.BooleanVar()).get()
        self.result = d
        self.destroy()


# ─────────────────────────────────────────────────────────────────────────────
# DIÁLOGO: CONTRASEÑA (mejorado)
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

        # Requisitos
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

        # Mostrar la contraseña
        self.entry_pw1.config(show="")
        self.show_pw.set(True)
        self.toggle_btn.config(text="🙈")

        # Mostrar mensaje sin bloquear
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
