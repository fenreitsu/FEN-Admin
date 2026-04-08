# FEN-Admin
GUI generada para facilitar la gestion y control de usuarios de un sistema. Proyecto en desarrollo

# ⬡ FENAdmin — Gestor de Usuarios y Grupos para Linux

**by [@fenreitsu](https://github.com/fenreitsu)**

FENAdmin es una herramienta gráfica interactiva para la administración de usuarios y grupos en sistemas Linux (Kali Linux, Ubuntu, Debian y derivados). Está diseñada para que cualquier administrador pueda gestionar su sistema de forma visual, cómoda y educativa, ya que por cada acción realizada se muestra el **comando equivalente en consola**.

---

## 📋 Requisitos

| Requisito | Versión mínima |
|-----------|---------------|
| Python    | 3.8+          |
| tkinter   | Incluido en Python estándar |
| Sistema   | Linux (probado en Kali, Ubuntu, Debian) |

### Verificar que tienes tkinter disponible

```bash
python3 -c "import tkinter; print('tkinter OK')"
```

Si no está disponible, instálalo:

```bash
# Debian / Ubuntu / Kali Linux
sudo apt install python3-tk

# Arch Linux
sudo pacman -S tk
```

---

## 🚀 Instalación y Ejecución

### Opción 1 — Ejecución directa (solo lectura, sin modificaciones)

```bash
python3 fenadmin.py
```

> En este modo puedes **ver** todos los usuarios y grupos, pero no podrás crear, modificar ni eliminar nada. Ideal para inspeccionar el sistema de forma segura.

### Opción 2 — Ejecución como root (acceso completo) ✅ Recomendado

```bash
sudo python3 fenadmin.py
```

### Opción 3 — Dar permisos de ejecución y lanzar

```bash
chmod +x fenadmin.py
sudo ./fenadmin.py
```

### Opción 4 — Crear un alias permanente (opcional)

Añade esta línea a tu `~/.bashrc` o `~/.zshrc`:

```bash
alias fenadmin='sudo python3 /ruta/completa/fenadmin.py'
```

Luego recarga el shell:

```bash
source ~/.bashrc
```

---

## 🖥️ Interfaz — Descripción de paneles

```
┌─────────────────────────────────────────────────────────────────┐
│  ⬡ FENAdmin   by @fenreitsu          ● ROOT    [☀ Claro]       │  ← Barra superior
├──────────┬──────────────────────────────────┬───────────────────┤
│          │  Gestión de Usuarios             │ ⚡ Actividad      │
│ NAVEG.   │  [+ Nuevo] [🗑] [🔒] [🔓]  🔍  │                   │
│          ├──────────────────────────────────┤  ✔ Usuario crea.. │
│ 👤 Users │  Usuario │UID│GID│Info │Home│..  │  $ useradd -m ..  │
│ 👥 Grupos│  ──────────────────────────────  │                   │
│          │  tabla interactiva...            │  ⚠ Sin privile.. │
│ FILTROS  │                                  │  # sudo useradd.. │
│ ☐ Sistema│                                  │                   │
│ ↻ Actualz│                                  │  [✕ Limpiar]      │
├──────────┴──────────────────────────────────┴───────────────────┤
│  FENAdmin listo.                          2025-01-01  12:00:00  │  ← Status bar
└─────────────────────────────────────────────────────────────────┘
```

### Panel izquierdo — Navegación

- **👤 Usuarios** — Cambia a la vista de gestión de usuarios
- **👥 Grupos** — Cambia a la vista de gestión de grupos
- **☐ Mostrar sistema** — Muestra/oculta usuarios y grupos del sistema (UID/GID < 1000)
- **↻ Actualizar** — Recarga los datos desde el sistema

### Panel central — Tabla principal

- Haz **clic en una columna** para ordenar
- **Doble clic** en una fila para editar el usuario/grupo
- **Clic derecho** en un usuario para el menú contextual

### Panel derecho — Actividad / Comandos

Cada acción realizada registra una tarjeta con:
- ✔ **Éxito** (verde)
- ⚠ **Advertencia** (amarillo)
- ✖ **Error** (rojo)
- ℹ **Información** (azul)

Y muestra el **comando exacto ejecutado**, para que puedas aprenderlo o reproducirlo en terminal.

---

## 👤 Gestión de Usuarios

### Crear un nuevo usuario

1. Clic en **＋ Nuevo Usuario**
2. Rellena los campos:
   - **Nombre de usuario** *(obligatorio)*
   - Nombre completo / comentario (GECOS)
   - Directorio home (por defecto `/home/usuario`)
   - Shell (por defecto `/bin/bash`)
   - Grupo principal
   - Grupos adicionales (separados por coma: `sudo,docker,www-data`)
   - Contraseña inicial
   - Marcar si crear directorio home (`-m`)
3. Clic en **Crear usuario**

**Comando equivalente generado:**
```bash
useradd -c 'Nombre Completo' -d /home/user -s /bin/bash -g users -G sudo,docker -m 'username'
echo 'username:contraseña' | chpasswd
```

### Editar un usuario

- **Doble clic** en la fila del usuario, o bien
- Clic derecho → **✏ Editar usuario**

Puedes modificar: nombre, GECOS, home, shell, grupos adicionales y contraseña.

**Comando equivalente:**
```bash
usermod -c 'Nuevo Nombre' -d /nuevo/home -m -s /bin/zsh -l nuevo_nombre 'usuario'
```

### Bloquear un usuario (baja temporal)

Selecciona el usuario → botón **🔒 Bloquear** (o clic derecho).

El usuario queda con estado `🔒 Bloqueado` y **no puede iniciar sesión**, pero su cuenta y datos se conservan intactos.

```bash
usermod -L 'usuario'
```

### Desbloquear un usuario

Selecciona el usuario bloqueado → botón **🔓 Desbloquear**.

```bash
usermod -U 'usuario'
```

### Eliminar un usuario (baja definitiva)

Selecciona el usuario → botón **🗑 Eliminar**.

Aparece un diálogo con tres opciones:
- **Sí** — Eliminar usuario **y** su directorio home (`userdel -r`)
- **No** — Eliminar solo el usuario, conservar home (`userdel`)
- **Cancelar** — Abortar la operación

```bash
userdel -r 'usuario'    # Con eliminación de home
userdel 'usuario'       # Sin eliminar home
```

### Cambiar contraseña

Clic derecho → **🔑 Cambiar contraseña**.

```bash
passwd usuario
# (FENAdmin usa: echo 'usuario:nuevapass' | chpasswd)
```

### Ver grupos de un usuario

Clic derecho → **👥 Ver grupos**.

---

## 👥 Gestión de Grupos

### Crear un nuevo grupo

1. Clic en **＋ Nuevo Grupo**
2. Rellena: nombre del grupo, GID (opcional), miembros iniciales, si es grupo de sistema

```bash
groupadd 'nombre_grupo'
groupadd -g 1500 'nombre_grupo'        # Con GID específico
groupadd -r 'nombre_grupo'             # Grupo de sistema
usermod -aG 'nombre_grupo' 'usuario'   # Añadir miembro
```

### Editar un grupo

Doble clic en la fila del grupo o botón **✏ Editar**.

Puedes cambiar el nombre, GID y miembros. Los miembros eliminados son removidos con `gpasswd -d`.

```bash
groupmod -n nuevo_nombre 'grupo'
groupmod -g 1600 'grupo'
usermod -aG 'grupo' 'nuevo_miembro'
gpasswd -d 'miembro_removido' 'grupo'
```

### Eliminar un grupo

Selecciona el grupo → botón **🗑 Eliminar**.

> ⚠️ No se puede eliminar el grupo primario de ningún usuario activo.

```bash
groupdel 'grupo'
```

---

## 🎨 Modos de color

Usa el botón **☀ Claro / 🌙 Oscuro** en la barra superior para cambiar el tema al instante.

| Modo | Recomendado para |
|------|-----------------|
| Oscuro (por defecto) | Terminales de Kali, uso nocturno, menor fatiga visual |
| Claro | Entornos de oficina, presentaciones, pantallas brillantes |

---

## ⚠️ Notas de seguridad

1. **Siempre ejecuta como root** para operaciones de escritura. En modo normal solo se pueden leer datos.
2. Las contraseñas se pasan via `chpasswd` y **no quedan en el historial de bash**.
3. FENAdmin no guarda ningún log propio; usa el panel de actividad para auditoría visual.
4. Para auditoría persistente, combina con `auditd` o revisa `/var/log/auth.log`.
5. Ten cuidado al eliminar usuarios del sistema (UID < 1000); pueden afectar servicios del SO.

---

## 🛠️ Solución de problemas

| Problema | Solución |
|----------|---------|
| `ModuleNotFoundError: No module named 'tkinter'` | `sudo apt install python3-tk` |
| La app abre pero no puede crear usuarios | Ejecuta con `sudo python3 fenadmin.py` |
| La fuente "Courier New" no se ve bien | Instala `fonts-liberation` o `ttf-liberation` |
| Ventana muy pequeña / grande | Redimensiona libremente; mínimo 900×600 |
| Error `usermod: user X is currently used by process Y` | El usuario tiene sesión abierta; ciérrala primero |

---

## 💡 Recomendaciones del creador

- **Kali Linux**: Algunos usuarios de sistema son críticos para herramientas de pentesting. Activa "Mostrar sistema" solo si sabes lo que buscas.
- **Backups**: Antes de eliminar usuarios o grupos importantes, haz una copia de `/etc/passwd`, `/etc/shadow` y `/etc/group`:
  ```bash
  sudo cp /etc/passwd /etc/passwd.bak
  sudo cp /etc/shadow /etc/shadow.bak
  sudo cp /etc/group /etc/group.bak
  ```
- **Usa el panel de actividad como aprendizaje**: Cada acción muestra el comando real. Cópialo y ejecútalo en terminal para aprender la equivalencia CLI.
- **Automatización**: Una vez que conozcas los comandos del panel, puedes crear scripts bash para gestión masiva de usuarios.

---

## 📁 Estructura de archivos

```
fenadmin/
├── fenadmin.py     ← Script principal (todo en un archivo)
└── README.md       ← Este documento
```

---

## 📜 Licencia

Uso libre para fines educativos y administrativos. Créditos al autor original requeridos en redistribuciones.

---

*FENAdmin — Hecho con ❤️ por @fenreitsu*
