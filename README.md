# ⬡ FENAdmin v1.3
### Gestor de Usuarios y Grupos para Linux (GUI LINUX)
**by [@fenreitsu](https://github.com/fenreitsu)** · *Proyecto en desarrollo*

FENAdmin es una herramienta gráfica para administrar usuarios y grupos en Linux (Kali, Ubuntu, Debian y derivados). Cada acción realizada muestra su **comando equivalente en la terminal integrada**, ideal para aprender mientras trabajas.

---

## 📌 Índice

- [📝 Changelog](#-changelog)
- [📋 Requisitos](#-requisitos)
- [🚀 Instalación y Ejecución](#-instalación-y-ejecución)
- [🖥️ Interfaz](#️-interfaz)
- [👤 Gestión de Usuarios](#-gestión-de-usuarios)
- [👥 Gestión de Grupos](#-gestión-de-grupos)
- [🔐 Permisos Especiales](#-permisos-especiales)
- [⚙️ Configuración de Cuenta](#️-configuración-de-cuenta)
- [⚠️ Seguridad](#️-seguridad)
- [🛠️ Solución de Problemas](#️-solución-de-problemas)
- [💡 Recomendaciones](#-recomendaciones)

---

## 📝 Changelog

### v1.3 (Actual 15/04/2026)
| | Cambio |
|-|--------|
| ✅ | **Nueva lógica completa de tipos de cuenta** (`Admin`, `Desktop User`, `Personalizado`) basada en los grupos reales del sistema |
| ✅ | Detección automática del tipo de cuenta al cargar y editar usuarios |
| ✅ | Aplicación inteligente de plantillas de grupos según el tipo seleccionado |
| ✅ | Mejora significativa en la gestión de **permisos especiales** (switches con animación) para usuarios Personalizados |
| ✅ | Corrección completa de carga y guardado de permisos al editar usuarios |
| ✅ | Animaciones suaves en los interruptores de permisos |
| ✅ | Mejoras en el flujo de desbloqueo de usuarios (solicita nueva contraseña automáticamente si es necesario) |
| ✅ | Optimizaciones en filtros avanzados y rendimiento de las tablas |
| ✅ | Código más modular y limpio (separación clara de lógica de tipos de cuenta) |
| ✅ | Mayor estabilidad general y experiencia de usuario mejorada |


### v1.2
- Mejoras en la interfaz y estabilidad general
- Correcciones menores en la terminal integrada
- Optimizaciones en el renderizado de tablas y filtros

### v1.1
- Terminal interactiva integrada con historial y bloqueo de comandos peligrosos
- Tipos de cuenta con estilo toggle
- Gestión avanzada de permisos especiales
- Listas dinámicas de grupos adicionales
- Correcciones en el layout de configuración de cuenta

### v0.3
- Introducción de tipos de cuenta básicos
- Validación y generador de contraseñas
- Filtros avanzados
- Configuración de UID, grupos y expiración

---

## 📋 Requisitos

| Requisito | Detalle |
|-----------|---------|
| Python | 3.8+ |
| tkinter | Incluido en Python estándar |
| Sistema | Linux (Kali, Ubuntu, Debian) |

**¿Tienes tkinter?** Compruébalo con:
```bash
python3 -c "import tkinter; print('tkinter OK')"
```
Si falta: `sudo apt install python3-tk` (Debian/Ubuntu/Kali) · `sudo pacman -S tk` (Arch)

---

## 🚀 Instalación y Ejecución

> **Recomendado:** ejecutar como root para tener acceso completo. Sin `sudo`, la app funciona en **modo solo lectura**.

```bash
# Acceso completo ✅
sudo python3 fen-admin.py

# Solo lectura (sin modificaciones)
python3 fen-admin.py
```

<details>
<summary>Más opciones de ejecución</summary>

```bash
# Dar permisos y ejecutar directamente
chmod +x fen-admin.py && sudo ./fen-admin.py

# Crear alias permanente en ~/.bashrc o ~/.zshrc
alias fen-admin='sudo python3 /ruta/completa/fen-admin.py'
source ~/.bashrc
```
</details>

---

## 🖥️ Interfaz

```
┌─────────────────────────────────────────────────────────────────┐
│  ⬡ FENAdmin   by @fenreitsu          ● ROOT    [☀ Claro]       │
├──────────┬──────────────────────────────────────────────────────┤
│ 👤 Users │  [+ Nuevo] [🗑] [🔒] [🔓]  🔍                       │
│ 👥 Grupos│  Usuario │UID│GID│Home│Shell│Estado│Tipo             │
│ ──────── │  ─────────────────────────────────────────────────   │
│ ☐ Sistema│  tabla interactiva...                                 │
│ ↻ Actualz├──────────────────────────────────────────────────────┤
│          │  📟 Terminal  $ > _              [▶ Ejecutar] [🗑]   │
├──────────┴──────────────────────────────────────────────────────┤
│  FENAdmin listo.                          2026-04-15  12:00:00  │
└─────────────────────────────────────────────────────────────────┘
```

| Panel | Función |
|-------|---------|
| **Izquierdo** | Navegar entre Usuarios/Grupos, filtrar por sistema, actualizar |
| **Central** | Tabla interactiva — clic para ordenar, doble clic para editar, clic derecho para más opciones |
| **Inferior** | Terminal integrada — muestra comandos en tiempo real y permite ejecutarlos manualmente |

**Terminal integrada** *(nueva en v1.1 en adelante)*: historial con `↑`/`↓`, comandos `cd`/`clear`/`exit`, bloqueo automático de operaciones peligrosas y salida coloreada por tipo (verde/rojo/amarillo/azul).

**Tema visual**: cambia entre 🌙 Oscuro y ☀️ Claro con el botón en la barra superior.

---

## 👤 Gestión de Usuarios

### Crear usuario

1. Clic en **＋ Nuevo Usuario**
2. Completa la pestaña **Información Básica** (nombre, GECOS, home, shell, contraseña)
3. Elige el **Tipo de cuenta**:

| Tipo | Sudo | Expiración | Permisos especiales |
|------|:----:|:----------:|:------------------:|
| Admin | ✅ | Nunca | — |
| Desktop User | ❌ | 90 días | Por defecto del sistema |
| Personalizado | ❌ | 90 días (configurable) | ✅ |

4. *(Opcional)* Ajusta la pestaña **Configuración de cuenta**
5. Clic en **Crear usuario**

```bash
useradd -c 'Nombre' -d /home/user -s /bin/bash -m 'username'
echo 'username:contraseña' | chpasswd
```

---

### Editar usuario

**Doble clic** en la fila o clic derecho → **✏ Editar usuario**.

Puedes modificar nombre, GECOS, home, shell, contraseña, tipo de cuenta y permisos especiales. Si el usuario ya era **Personalizado**, sus permisos se cargan automáticamente.

```bash
usermod -c 'Nuevo Nombre' -d /nuevo/home -m -s /bin/zsh 'usuario'
```

---

### Otras acciones

| Acción | Cómo | Comando |
|--------|------|---------|
| 🔒 Bloquear | Botón o clic derecho | `passwd -l 'usuario'` |
| 🔓 Desbloquear | Botón o clic derecho | `passwd -u 'usuario'` |
| 🗑 Eliminar | Botón o clic derecho | `userdel [-r] 'usuario'` |
| 🔑 Contraseña | Clic derecho | `echo 'user:pass' \| chpasswd` |
| 👥 Ver grupos | Clic derecho | `groups 'usuario'` |

> Al **eliminar**, se pregunta si borrar también el directorio home (`-r`) o solo la cuenta.
> Al **desbloquear**, si el usuario no tiene contraseña válida, FENAdmin pedirá crear una nueva automáticamente.

---

## 👥 Gestión de Grupos

| Acción | Cómo | Comando |
|--------|------|---------|
| ＋ Crear | Botón **＋ Nuevo Grupo** | `groupadd ['nombre']` |
| ✏ Editar | Doble clic o botón Editar | `groupmod -n nuevo 'grupo'` |
| 🗑 Eliminar | Botón Eliminar | `groupdel 'grupo'` |

Al editar, los miembros añadidos se agregan con `usermod -aG` y los eliminados con `gpasswd -d`.

> ⚠️ No se puede eliminar el grupo primario de un usuario activo.

---

## 🔐 Permisos Especiales (Avanzados)

*Disponible únicamente para usuarios de tipo **Personalizado**.*

Se accede desde la pestaña **Configuración de cuenta** al editar un usuario. Cada permiso tiene un switch deslizante y se aplica en tiempo real a la terminal.

| Switch | Grupo | Acceso que otorga |
|--------|-------|-------------------|
| Almacenamiento externo | `plugdev` | USB, tarjetas SD |
| Impresoras | `lpadmin` | Gestión de impresoras |
| Módem | `dialout` | Internet por módem |
| Redes | `netdev` | WiFi / Ethernet |
| Logs | `adm` | Registros del sistema |
| Audio | `audio` | Dispositivos de audio |
| Video | `video` | Dispositivos de video |
| CD-ROM | `cdrom` | Unidades ópticas |
| Escáner | `scanner` | Escáneres |
| Red local | `sambashare` | Compartir archivos (Samba) |
| Fax | `fax` | Envío/recepción de fax |
| Disquete | `floppy` | Disqueteras |
| Cinta | `tape` | Unidades de cinta |

```bash
usermod -aG 'audio' 'usuario'   # Al activar un permiso
gpasswd -d 'usuario' 'audio'    # Al desactivar un permiso
```
**Novedad v1.3: Los permisos ahora se cargan y guardan correctamente al editar.**

---

## ⚙️ Configuración de Cuenta

*Pestaña disponible para todos los tipos de usuario.*

| Campo | Descripción |
|-------|-------------|
| **UID** | Dejar vacío para asignación automática |
| **Grupo principal** | Campo + botón; un solo grupo a la vez |
| **Grupos adicionales** | Lista dinámica: **＋ Agregar** (o `Enter`) / **✕ Eliminar** |
| **Fecha de expiración** | Formato `YYYY-MM-DD` o `never` |
| **Días de inactividad** | `-1` para desactivar |

---

## ⚠️ Seguridad

- Ejecuta siempre con `sudo` para operaciones de escritura.
- Las contraseñas se pasan por `chpasswd` — **no quedan en el historial de bash**.
- Los comandos sobre `nobody` y `nogroup` están **bloqueados** en la interfaz y en la terminal.
- Para auditoría persistente usa `auditd` o revisa `/var/log/auth.log`.
- Ten precaución con usuarios de sistema (UID < 1000): pueden afectar servicios del SO.

**Backup recomendado antes de cambios importantes:**
```bash
sudo cp /etc/passwd /etc/passwd.bak
sudo cp /etc/shadow /etc/shadow.bak
sudo cp /etc/group  /etc/group.bak
```

---

## 🛠️ Solución de Problemas

| Problema | Solución |
|----------|---------|
| `No module named 'tkinter'` | `sudo apt install python3-tk` |
| No puede crear usuarios | Ejecuta con `sudo` |
| Fuente "Courier New" mal renderizada | Instala `fonts-liberation` |
| Ventana muy pequeña | Mínimo recomendado: 900×600 |
| `usermod: user X currently used by process Y` | El usuario tiene sesión activa; ciérrala primero |
| Permisos especiales no aparecen | El tipo de cuenta debe ser **Personalizado** |
| Error de contraseña al desbloquear | FENAdmin pedirá establecer una nueva automáticamente |

---

## 💡 Recomendaciones

- **Kali Linux** — Activa "Mostrar sistema" solo si sabes lo que buscas; algunos usuarios de sistema son críticos para herramientas de pentesting.
- **Aprendizaje** — Cada acción en la GUI muestra el comando real en la terminal. Cópialo y úsalo en tus scripts para automatizar.
- **Filtros** — Usa los filtros por tipo de cuenta, UID o estado para localizar usuarios rápido en sistemas con muchas cuentas.

---

## 📁 Estructura del proyecto

```
FEN-Admin/
├── fen-admin.py              ← Script principal
├── README.md                ← Este documento
└── resources/logo/
    ├── fenreitsu.png        ← Logo modo claro
    └── fenreitsu-white.png  ← Logo modo oscuro
```

---

## 📜 Licencia

Uso libre para fines educativos y administrativos. Se requiere crédito al autor en redistribuciones.

---

*FENAdmin v1.3 — Hecho con ❤️ por [@fenreitsu](https://github.com/fenreitsu) con ayuda de Claude y Deepseek*
