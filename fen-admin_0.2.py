#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FENAdmin - Gestor de Usuarios y Grupos
Creador: @fenreitsu
Compatibilidad: Linux (Kali Linux, Ubuntu, Debian, etc.)
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import pwd
import grp
import os
import sys
import re
import datetime
from functools import partial

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

def get_users():
    """Devuelve lista de dicts con info de todos los usuarios."""
    users = []
    for p in pwd.getpwall():
        # Comprobar si está bloqueado (! o * en /etc/shadow)
        locked = False
        try:
            out, _, _ = run_cmd(f"passwd -S {p.pw_name} 2>/dev/null")
            if out:
                parts = out.split()
                if len(parts) >= 2 and parts[1] in ('L', 'LK'):
                    locked = True
        except Exception:
            pass

        users.append({
            "name":    p.pw_name,
            "uid":     p.pw_uid,
            "gid":     p.pw_gid,
            "gecos":   p.pw_gecos,
            "home":    p.pw_dir,
            "shell":   p.pw_shell,
            "locked":  locked,
            "system":  p.pw_uid < 1000,
        })
    return sorted(users, key=lambda u: u["uid"])

def get_groups():
    """Devuelve lista de dicts con info de todos los grupos."""
    groups = []
    for g in grp.getgrall():
        groups.append({
            "name":    g.gr_name,
            "gid":     g.gr_gid,
            "members": g.gr_mem,
            "system":  g.gr_gid < 1000,
        })
    return sorted(groups, key=lambda g: g["gid"])

def get_user_groups(username):
    """Devuelve lista de grupos a los que pertenece un usuario."""
    out, _, _ = run_cmd(f"groups {username}")
    if ":" in out:
        return out.split(":")[1].strip().split()
    return out.strip().split()

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

        self.title("FENAdmin")
        self.geometry("1280x780")
        self.minsize(900, 600)
        self.configure(bg=self.T["bg"])

        # Icono de ventana (usando un canvas simple)
        self._set_icon()

        self._build_ui()
        self._apply_theme()
        self.refresh_users()

        self.bind("<Configure>", self._on_resize)

    # ─── ICONO ────────────────────────────────────────────────────────────────

    def _set_icon(self):
        try:
            icon = tk.PhotoImage(width=32, height=32)
            self.iconphoto(True, icon)
        except Exception:
            pass

    # ─── CONSTRUCCIÓN UI ──────────────────────────────────────────────────────

    def _build_ui(self):
        T = self.T

        # ── Barra superior ──────────────────────────────────────────────────
        self.topbar = tk.Frame(self, height=54)
        self.topbar.pack(fill="x", side="top")
        self.topbar.pack_propagate(False)

        # Logo / Título
        self.lbl_logo = tk.Label(
            self.topbar,
            text="⬡  FENAdmin",
            font=("Courier New", 18, "bold"),
            padx=18, pady=8
        )
        self.lbl_logo.pack(side="left")

        self.lbl_creator = tk.Label(
            self.topbar,
            text="by @fenreitsu",
            font=("Courier New", 9),
            padx=4
        )
        self.lbl_creator.pack(side="left", pady=6)

        # Controles derecha
        right_frame = tk.Frame(self.topbar)
        right_frame.pack(side="right", padx=12)

        # Toggle tema
        self.btn_theme = tk.Button(
            right_frame, text="☀  Claro", font=("Courier New", 9, "bold"),
            relief="flat", cursor="hand2", padx=10, pady=4,
            command=self._toggle_theme
        )
        self.btn_theme.pack(side="right", padx=4)

        # Indicador root
        root_text = "● ROOT" if is_root() else "● USER"
        root_color = T["success"] if is_root() else T["warning"]
        self.lbl_root = tk.Label(
            right_frame,
            text=root_text,
            font=("Courier New", 9, "bold"),
            fg=root_color, padx=8
        )
        self.lbl_root.pack(side="right", padx=8)

        # ── Separador ───────────────────────────────────────────────────────
        self.sep_top = tk.Frame(self, height=1)
        self.sep_top.pack(fill="x")

        # ── Layout principal (sidebar + content) ────────────────────────────
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Sidebar izquierda
        self.sidebar = tk.Frame(self.main_frame, width=180)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self._build_sidebar()

        # Separador vertical
        self.sep_side = tk.Frame(self.main_frame, width=1)
        self.sep_side.pack(side="left", fill="y")

        # Área de contenido
        self.content = tk.Frame(self.main_frame)
        self.content.pack(side="left", fill="both", expand=True)

        # ── Panel de notificaciones (derecha) ────────────────────────────────
        self.notif_panel = tk.Frame(self.main_frame, width=310)
        self.notif_panel.pack(side="right", fill="y")
        self.notif_panel.pack_propagate(False)

        self.sep_notif = tk.Frame(self.main_frame, width=1)
        self.sep_notif.pack(side="right", fill="y")

        self._build_notif_panel()

        # ── Vistas de contenido ──────────────────────────────────────────────
        self._frames = {}
        for name in ("users", "groups"):
            f = tk.Frame(self.content)
            self._frames[name] = f
            f.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_users_view(self._frames["users"])
        self._build_groups_view(self._frames["groups"])

        self._show_frame("users")

        # ── Barra de estado ──────────────────────────────────────────────────
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

        # Botón refresh
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

        # Scrollable área
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
        # Mousewheel
        self.notif_canvas.bind_all(
            "<MouseWheel>",
            lambda e: self.notif_canvas.yview_scroll(-1*(e.delta//120), "units")
        )

        self._add_notification(
            "info", "Sistema iniciado",
            "FENAdmin listo. Ejecute acciones para ver los comandos equivalentes aquí.",
            ""
        )

    def _build_users_view(self, parent):
        T = self.T

        # ── Toolbar superior con título y acciones ──────────────────────────────
        top_toolbar = tk.Frame(parent, height=52)
        top_toolbar.pack(fill="x", pady=(0, 0))
        top_toolbar.pack_propagate(False)
        
        tk.Label(
            top_toolbar, text="Gestión de Usuarios",
            font=("Courier New", 14, "bold"), anchor="w", padx=16, pady=10
        ).pack(side="left")
        
        # Botones de acción (ahora a la derecha)
        actions = [
            ("＋ Nuevo Usuario",  self._dlg_new_user,    "accent"),
            ("🗑 Eliminar",       self._delete_user,     "danger"),
            ("🔒 Bloquear",       self._lock_user,       "warning"),
            ("🔓 Desbloquear",    self._unlock_user,     "success"),
        ]
        
        action_frame = tk.Frame(top_toolbar)
        action_frame.pack(side="right", padx=10)
        
        for label, cmd, style in actions:
            btn = self._styled_btn(action_frame, label, cmd, style)
            btn.pack(side="left", padx=3, pady=10)
        
        # ── Barra de filtros (horizontal debajo del toolbar) ────────────────────
        filter_bar = tk.Frame(parent, height=45)
        filter_bar.pack(fill="x", pady=(5, 0))
        filter_bar.pack_propagate(False)
        
        # Filtro rápido (buscador general)
        tk.Label(filter_bar, text="🔍 Buscar:", font=("Courier New", 9, "bold"),
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(15, 5))
        
        self.search_entry = tk.Entry(filter_bar, font=("Courier New", 10), relief="flat",
                                    bg=T["entry_bg"], fg=T["entry_fg"],
                                    insertbackground=T["accent"], width=25)
        self.search_entry.pack(side="left", padx=(0, 15), ipady=3)
        self.search_entry.bind("<KeyRelease>", lambda e: self._apply_user_filters())
        
        # Botón limpiar filtros
        clear_btn = tk.Button(filter_bar, text="✕ Limpiar filtros", font=("Courier New", 8),
                            relief="flat", cursor="hand2", command=self._clear_user_filters)
        clear_btn.pack(side="left", padx=5)
        self._theme_widget(clear_btn)
        
        # Separador
        tk.Frame(parent, height=1).pack(fill="x", pady=(5, 0))
        
        # ── Panel de filtros avanzados (colapsable) ────────────────────────────
        self.filters_visible = tk.BooleanVar(value=False)
        
        filter_header = tk.Frame(parent)
        filter_header.pack(fill="x", pady=(5, 0))
        
        self.toggle_btn = tk.Button(filter_header, text="▼ FILTROS AVANZADOS", font=("Courier New", 8, "bold"),
                                    relief="flat", cursor="hand2", command=self._toggle_filters)
        self.toggle_btn.pack(side="left", padx=15, pady=2)
        self._theme_widget(self.toggle_btn)
        
        # Frame contenedor de filtros (inicialmente oculto)
        self.advanced_filters = tk.Frame(parent)
        # No lo empaquetamos aún
        
        # Crear los filtros avanzados
        self._create_advanced_filters()
        
        # ── Tabla ────────────────────────────────────────────────────────────────
        table_frame = tk.Frame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)
        
        cols = ("Usuario", "UID", "GID", "Info (GECOS)", "Home", "Shell", "Estado")
        self.tree_users = ttk.Treeview(
            table_frame, columns=cols, show="headings",
            selectmode="browse"
        )
        
        col_widths = [120, 60, 60, 160, 200, 140, 90]
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
        
        # Menú contextual
        self.ctx_user = tk.Menu(self, tearoff=0)
        
        # ── Barra de info inferior ────────────────────────────────────────────────
        info_bar = tk.Frame(parent, height=28)
        info_bar.pack(fill="x", side="bottom")
        info_bar.pack_propagate(False)
        self.lbl_user_count = tk.Label(
            info_bar, text="", font=("Courier New", 8), anchor="w", padx=10
        )
        self.lbl_user_count.pack(side="left")

    def _create_advanced_filters(self):
        """Crea los widgets de filtros avanzados"""
        T = self.T
        
        # Diccionario para almacenar las variables de filtro
        self.filter_vars = {
            "username": tk.StringVar(),
            "uid_min": tk.StringVar(),
            "uid_max": tk.StringVar(),
            "shell": tk.StringVar(),
            "state": tk.StringVar(),  # Activo, Bloqueado, Todos
            "gecos": tk.StringVar(),
            "home": tk.StringVar(),
        }
        
        # Frame principal de filtros con grid
        filters_frame = tk.Frame(self.advanced_filters, pady=8)
        filters_frame.pack(fill="x", padx=15)
        
        # Fila 1: Nombre de usuario y UID
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
        
        # Fila 2: Shell y Estado
        row2 = tk.Frame(filters_frame)
        row2.pack(fill="x", pady=3)
        
        tk.Label(row2, text="Shell:", font=("Courier New", 8), width=12, anchor="e",
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(0, 5))
        shell_combo = ttk.Combobox(row2, textvariable=self.filter_vars["shell"], width=25,
                                    font=("Courier New", 8), state="readonly")
        shell_combo['values'] = ['Todos', '/bin/bash', '/bin/sh', '/bin/dash', '/bin/zsh', '/sbin/nologin', '/usr/sbin/nologin']
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
        
        # Fila 3: GECOS y Home
        row3 = tk.Frame(filters_frame)
        row3.pack(fill="x", pady=3)
        
        tk.Label(row3, text="GECOS:", font=("Courier New", 8), width=12, anchor="e",
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(0, 5))
        gecos_entry = tk.Entry(row3, textvariable=self.filter_vars["gecos"], width=52,
                                font=("Courier New", 8), relief="flat")
        gecos_entry.pack(side="left", padx=(0, 20))
        gecos_entry.bind("<KeyRelease>", lambda e: self._apply_user_filters())
        
        # Fila 4: Home
        row4 = tk.Frame(filters_frame)
        row4.pack(fill="x", pady=3)
        
        tk.Label(row4, text="Home:", font=("Courier New", 8), width=12, anchor="e",
                bg=T["bg"], fg=T["text"]).pack(side="left", padx=(0, 5))
        home_entry = tk.Entry(row4, textvariable=self.filter_vars["home"], width=52,
                            font=("Courier New", 8), relief="flat")
        home_entry.pack(side="left", padx=(0, 20))
        home_entry.bind("<KeyRelease>", lambda e: self._apply_user_filters())
        
        # Aplicar tema a los filtros
        for widget in [row1, row2, row3, row4, filters_frame]:
            self._theme_widget(widget)

    def _toggle_filters(self):
        """Muestra u oculta los filtros avanzados"""
        if self.filters_visible.get():
            self.advanced_filters.pack_forget()
            self.filters_visible.set(False)
            self.toggle_btn.config(text="▶ FILTROS AVANZADOS")
        else:
            self.advanced_filters.pack(fill="x", before=self.tree_users.master)
            self.filters_visible.set(True)
            self.toggle_btn.config(text="▼ FILTROS AVANZADOS")

    def _apply_user_filters(self):
        """Aplica todos los filtros a la tabla de usuarios"""
        # Obtener todos los usuarios
        users = get_users()
        show_sys = self.show_system.get()
        
        # Obtener valores de búsqueda y filtros
        search_text = self.search_entry.get().lower()
        username_filter = self.filter_vars["username"].get().lower()
        uid_min = self.filter_vars["uid_min"].get()
        uid_max = self.filter_vars["uid_max"].get()
        shell_filter = self.filter_vars["shell"].get()
        state_filter = self.filter_vars["state"].get()
        gecos_filter = self.filter_vars["gecos"].get().lower()
        home_filter = self.filter_vars["home"].get().lower()
        
        # Limpiar tabla
        for row in self.tree_users.get_children():
            self.tree_users.delete(row)
        
        count = 0
        for u in users:
            # Filtro de sistema
            if not show_sys and u["system"]:
                continue
            
            # Búsqueda general (nombre, GECOS, home, shell)
            if search_text:
                if (search_text not in u["name"].lower() and 
                    search_text not in u["gecos"].lower() and
                    search_text not in u["home"].lower() and
                    search_text not in u["shell"].lower()):
                    continue
            
            # Filtro por nombre de usuario
            if username_filter and username_filter not in u["name"].lower():
                continue
            
            # Filtro por UID mínimo
            if uid_min:
                try:
                    if u["uid"] < int(uid_min):
                        continue
                except ValueError:
                    pass
            
            # Filtro por UID máximo
            if uid_max:
                try:
                    if u["uid"] > int(uid_max):
                        continue
                except ValueError:
                    pass
            
            # Filtro por shell
            if shell_filter != "Todos" and u["shell"] != shell_filter:
                continue
            
            # Filtro por estado
            if state_filter != "Todos":
                user_locked = u["locked"]
                if state_filter == "Activo" and user_locked:
                    continue
                elif state_filter == "Bloqueado" and not user_locked:
                    continue
            
            # Filtro por GECOS
            if gecos_filter and gecos_filter not in u["gecos"].lower():
                continue
            
            # Filtro por home
            if home_filter and home_filter not in u["home"].lower():
                continue
            
            # Pasa todos los filtros - mostrar usuario
            state = "🔒 Bloqueado" if u["locked"] else "✅ Activo"
            tag = "system" if u["system"] else ("locked" if u["locked"] else "normal")
            self.tree_users.insert(
                "", "end", iid=u["name"],
                values=(u["name"], u["uid"], u["gid"], u["gecos"],
                        u["home"], u["shell"], state),
                tags=(tag,)
            )
            count += 1
        
        # Configurar colores
        T = self.T
        self.tree_users.tag_configure("system", background=T["tag_sys"], foreground=T["tag_sys_fg"])
        self.tree_users.tag_configure("locked", foreground=T["warning"])
        self.tree_users.tag_configure("normal", foreground=T["text"])
        self.lbl_user_count.config(text=f"  {count} usuario(s) mostrado(s)")

    def _clear_user_filters(self):
        """Limpia todos los filtros y la búsqueda"""
        self.search_entry.delete(0, tk.END)
        for var in self.filter_vars.values():
            var.set("")
        self.filter_vars["shell"].set("Todos")
        self.filter_vars["state"].set("Todos")
        self._apply_user_filters()
        self._set_status("Filtros limpiados.")

    def _build_groups_view(self, parent):
        T = self.T

        toolbar = tk.Frame(parent, height=52)
        toolbar.pack(fill="x", pady=(0, 0))
        toolbar.pack_propagate(False)
        toolbar.configure(width=800)  # ← línea añadida

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

        tk.Frame(parent, height=1).pack(fill="x")

        table_frame = tk.Frame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        cols = ("Grupo", "GID", "Miembros", "Tipo")
        self.tree_groups = ttk.Treeview(
            table_frame, columns=cols, show="headings",
            selectmode="browse"
        )
        col_widths = [160, 70, 500, 100]
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

        info_bar = tk.Frame(parent, height=28)
        info_bar.pack(fill="x", side="bottom")
        info_bar.pack_propagate(False)
        self.lbl_group_count = tk.Label(
            info_bar, text="", font=("Courier New", 8), anchor="w", padx=10
        )
        self.lbl_group_count.pack(side="left")

    # ─── NAVEGACIÓN ───────────────────────────────────────────────────────────

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

    # ─── REFRESCO DE DATOS ────────────────────────────────────────────────────

    def refresh_users(self):
        """Refresca la tabla de usuarios aplicando filtros"""
        self._apply_user_filters()

    def refresh_groups(self):
        for row in self.tree_groups.get_children():
            self.tree_groups.delete(row)
        groups = get_groups()
        show_sys = self.show_system.get()
        count = 0
        for g in groups:
            if not show_sys and g["system"]:
                continue
            tipo = "Sistema" if g["system"] else "Normal"
            members = ", ".join(g["members"]) if g["members"] else "(sin miembros)"
            self.tree_groups.insert(
                "", "end", iid=g["name"],
                values=(g["name"], g["gid"], members, tipo),
                tags=("system",) if g["system"] else ("normal",)
            )
            count += 1
        T = self.T
        self.tree_groups.tag_configure("system", background=T["tag_sys"], foreground=T["tag_sys_fg"])
        self.tree_groups.tag_configure("normal", foreground=T["text"])
        self.lbl_group_count.config(text=f"  {count} grupo(s) mostrado(s)")

    def _full_refresh(self):
        if self._current_frame == "users":
            self.refresh_users()
        else:
            self.refresh_groups()
        self._set_status("Datos actualizados.")

    def _apply_filter(self):
        if hasattr(self, "_current_frame") and self._current_frame == "users":
            self._apply_user_filters()

    # ─── DIÁLOGOS DE USUARIO ─────────────────────────────────────────────────

    def _dlg_new_user(self):
        dlg = UserDialog(self, "Nuevo Usuario", {}, self.T)
        self.wait_window(dlg)
        if dlg.result:
            d = dlg.result
            cmd = f"useradd"
            if d.get("comment"):  cmd += f" -c '{d['comment']}'"
            if d.get("home"):     cmd += f" -d '{d['home']}'"
            if d.get("shell"):    cmd += f" -s '{d['shell']}'"
            if d.get("group"):    cmd += f" -g '{d['group']}'"
            if d.get("groups"):   cmd += f" -G '{d['groups']}'"
            if d.get("create_home", True): cmd += " -m"
            cmd += f" '{d['username']}'"

            if not is_root():
                self._add_notification("warning", "Sin privilegios",
                    "Necesitas ejecutar FENAdmin como root (sudo) para crear usuarios.",
                    f"# sudo {cmd}")
                messagebox.showwarning("Sin privilegios", "Se requiere ejecutar como root (sudo).")
                return

            out, err, rc = run_cmd(cmd)
            if rc == 0:
                # Establecer contraseña si se proporcionó
                if d.get("password"):
                    pw_cmd = f"echo '{d['username']}:{d['password']}' | chpasswd"
                    run_cmd(pw_cmd)
                self._add_notification("success", f"Usuario '{d['username']}' creado",
                    f"Se creó el usuario con los parámetros especificados.", cmd)
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
            current = {
                "username": p.pw_name,
                "comment":  p.pw_gecos,
                "home":     p.pw_dir,
                "shell":    p.pw_shell,
                "uid":      p.pw_uid,
                "gid":      p.pw_gid,
            }
        except KeyError:
            messagebox.showerror("Error", f"Usuario '{username}' no encontrado.")
            return

        dlg = UserDialog(self, f"Editar Usuario: {username}", current, self.T, edit=True)
        self.wait_window(dlg)
        if dlg.result:
            d = dlg.result
            cmd = f"usermod"
            if d.get("comment") != current["comment"]: cmd += f" -c '{d['comment']}'"
            if d.get("home") != current["home"]:       cmd += f" -d '{d['home']}' -m"
            if d.get("shell") != current["shell"]:     cmd += f" -s '{d['shell']}'"
            if d.get("new_name") and d["new_name"] != username: cmd += f" -l '{d['new_name']}'"
            if d.get("groups"):                         cmd += f" -aG '{d['groups']}'"
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

    # ─── MENÚ CONTEXTUAL USUARIO ─────────────────────────────────────────────

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

    # ─── DIÁLOGOS DE GRUPO ────────────────────────────────────────────────────

    def _dlg_new_group(self):
        dlg = GroupDialog(self, "Nuevo Grupo", {}, self.T)
        self.wait_window(dlg)
        if dlg.result:
            d = dlg.result
            cmd = f"groupadd"
            if d.get("gid"):    cmd += f" -g '{d['gid']}'"
            if d.get("system"): cmd += " -r"
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
            # Actualizar miembros
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

    # ─── NOTIFICACIONES ───────────────────────────────────────────────────────

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

        # Borde izquierdo de color
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

        # Aplicar colores del tema
        self._theme_widget(card)
        self._theme_widget(inner)
        self._theme_widget(header_row)
        self._theme_widget(cmd_frame if command else inner)

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

        # Separador
        tk.Frame(self.notif_inner, height=1).pack(fill="x", padx=8)
        self._theme_widget(self.notif_inner.winfo_children()[-1])

        # Scroll al final
        self.notif_canvas.update_idletasks()
        self.notif_canvas.yview_moveto(1.0)

        self.notifications.append(card)

    def _clear_notifications(self):
        for w in self.notif_inner.winfo_children():
            w.destroy()
        self.notifications.clear()
        self._add_notification("info", "Panel limpiado", "Historial de acciones borrado.", "")

    # ─── TEMA ─────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        if self.theme_name.get() == "dark":
            self.theme_name.set("light")
            self.btn_theme.config(text="🌙  Oscuro")
        else:
            self.theme_name.set("dark")
            self.btn_theme.config(text="☀  Claro")
        self.T = THEMES[self.theme_name.get()]
        self._apply_theme()
        self.refresh_users()
        self.refresh_groups()

    def _apply_theme(self):
        T = self.T
        self.configure(bg=T["bg"])

        # Configurar ttk style
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

        # Recorrer todos los widgets
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

    # ─── HELPERS ──────────────────────────────────────────────────────────────

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
        pass  # Responsive por diseño

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
# DIÁLOGO: USUARIO
# ─────────────────────────────────────────────────────────────────────────────

class UserDialog(tk.Toplevel):
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

        # Header
        hdr = tk.Frame(self, bg=T["bg2"], pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=self.title(), font=("Courier New", 13, "bold"),
                 bg=T["bg2"], fg=T["accent"], padx=16).pack(anchor="w")

        tk.Frame(self, height=1, bg=T["border"]).pack(fill="x")

        form = tk.Frame(self, bg=T["bg"], pady=10)
        form.pack(fill="both", expand=True, padx=4)

        fields = [
            ("Nombre de usuario *", "username"),
            ("Nombre completo (GECOS)", "comment"),
            ("Directorio home", "home"),
            ("Shell", "shell"),
            ("Grupo principal", "group"),
            ("Grupos adicionales (separados por coma)", "groups"),
            ("Contraseña (dejar vacío para no cambiar)", "password"),
        ]
        if self.edit:
            fields.insert(1, ("Nuevo nombre de usuario", "new_name"))

        self.entries = {}
        for label, key in fields:
            row = tk.Frame(form, bg=T["bg"])
            row.pack(fill="x", **pad)
            tk.Label(row, text=label, font=("Courier New", 9),
                     bg=T["bg"], fg=T["text2"], width=38, anchor="w").pack(side="left")
            show = "*" if key == "password" else ""
            e = tk.Entry(row, font=("Courier New", 10), show=show,
                         bg=T["entry_bg"], fg=T["entry_fg"],
                         insertbackground=T["accent"],
                         highlightbackground=T["border"],
                         highlightcolor=T["accent"],
                         highlightthickness=1, relief="flat", width=28)
            if data.get(key):
                e.insert(0, str(data[key]))
            e.pack(side="left", ipady=3)
            self.entries[key] = e

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

    def _submit(self):
        d = {k: e.get().strip() for k, e in self.entries.items()}
        if not d.get("username") and not self.edit:
            messagebox.showerror("Error", "El nombre de usuario es obligatorio.", parent=self)
            return
        d["create_home"] = getattr(self, "create_home", tk.BooleanVar(value=True)).get()
        self.result = d
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
                  ("Miembros (separados por coma)", "members")]
        if self.edit:
            fields.insert(1, ("Nuevo nombre", "new_name"))

        self.entries = {}
        for label, key in fields:
            row = tk.Frame(form, bg=T["bg"])
            row.pack(fill="x", **pad)
            tk.Label(row, text=label, font=("Courier New", 9),
                     bg=T["bg"], fg=T["text2"], width=38, anchor="w").pack(side="left")
            e = tk.Entry(row, font=("Courier New", 10),
                         bg=T["entry_bg"], fg=T["entry_fg"],
                         insertbackground=T["accent"],
                         highlightbackground=T["border"],
                         highlightcolor=T["accent"],
                         highlightthickness=1, relief="flat", width=28)
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

        for label, key in [("Nueva contraseña", "pw1"), ("Confirmar contraseña", "pw2")]:
            row = tk.Frame(form, bg=T["bg"])
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=("Courier New", 9),
                     bg=T["bg"], fg=T["text2"], width=24, anchor="w").pack(side="left")
            e = tk.Entry(row, show="*", font=("Courier New", 10),
                         bg=T["entry_bg"], fg=T["entry_fg"],
                         insertbackground=T["accent"],
                         highlightbackground=T["border"],
                         highlightcolor=T["accent"],
                         highlightthickness=1, relief="flat", width=24)
            e.pack(side="left", ipady=3)
            setattr(self, f"entry_{key}", e)

        tk.Frame(self, height=1, bg=T["border"]).pack(fill="x", pady=4)

        btn_row = tk.Frame(self, bg=T["bg"], pady=10)
        btn_row.pack(fill="x", padx=14)

        tk.Button(btn_row, text="Cancelar", font=("Courier New", 9),
                  bg=T["button_bg"], fg=T["text2"], relief="flat", cursor="hand2",
                  padx=14, pady=5, command=self.destroy).pack(side="right", padx=4)
        tk.Button(btn_row, text="Cambiar contraseña", font=("Courier New", 9, "bold"),
                  bg=T["accent2"], fg="#fff", relief="flat", cursor="hand2",
                  padx=14, pady=5, command=self._submit).pack(side="right", padx=4)

    def _submit(self):
        pw1 = self.entry_pw1.get()
        pw2 = self.entry_pw2.get()
        if not pw1:
            messagebox.showerror("Error", "La contraseña no puede estar vacía.", parent=self)
            return
        if pw1 != pw2:
            messagebox.showerror("Error", "Las contraseñas no coinciden.", parent=self)
            return
        if len(pw1) < 6:
            messagebox.showwarning("Advertencia", "Contraseña muy corta (mínimo 6 caracteres).", parent=self)
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
