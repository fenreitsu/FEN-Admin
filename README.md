FEN-Admin
GUI generada para facilitar la gestión y control de usuarios de un sistema. Proyecto en desarrollo
⬡ FENAdmin v1.1 — Gestor de Usuarios y Grupos para Linux
by @fenreitsu
FENAdmin es una herramienta gráfica interactiva para la administración de usuarios y grupos en sistemas Linux (Kali Linux, Ubuntu, Debian y derivados). Está diseñada para que cualquier administrador pueda gestionar su sistema de forma visual, cómoda y educativa, ya que por cada acción realizada se muestra el comando equivalente en la terminal interactiva integrada.
---
📋 Requisitos
Requisito	Versión mínima
Python	3.8+
tkinter	Incluido en Python estándar
Sistema	Linux (probado en Kali, Ubuntu, Debian)
Verificar que tienes tkinter disponible
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
🚀 Instalación y Ejecución
Opción 1 — Ejecución directa (solo lectura, sin modificaciones)
```bash
python3 fenadmin.py
```
> En este modo puedes \*\*ver\*\* todos los usuarios y grupos, pero no podrás crear, modificar ni eliminar nada. Ideal para inspeccionar el sistema de forma segura.
Opción 2 — Ejecución como root (acceso completo) ✅ Recomendado
```bash
sudo python3 fenadmin.py
```
Opción 3 — Dar permisos de ejecución y lanzar
```bash
chmod +x fenadmin.py
sudo ./fenadmin.py
```
Opción 4 — Crear un alias permanente (opcional)
Añade esta línea a tu `\~/.bashrc` o `\~/.zshrc`:
```bash
alias fenadmin='sudo python3 /ruta/completa/fenadmin.py'
```
Luego recarga el shell:
```bash
source \~/.bashrc
```
---
🖥️ Interfaz — Descripción de paneles
```
┌─────────────────────────────────────────────────────────────────┐
│  ⬡ FENAdmin   by @fenreitsu          ● ROOT    \[☀ Claro]       │  ← Barra superior
├──────────┬──────────────────────────────────────────────────────┤
│          │  Gestión de Usuarios                                  │
│ NAVEG.   │  \[+ Nuevo] \[🗑] \[🔒] \[🔓]  🔍                       │
│          ├──────────────────────────────────────────────────────┤
│ 👤 Users │  Usuario │UID│GID│Info │Home│Shell│Estado│Tipo      │
│ 👥 Grupos│  ────────────────────────────────────────────────    │
│          │  tabla interactiva...                                 │
│ FILTROS  │                                                       │
│ ☐ Sistema├──────────────────────────────────────────────────────┤
│ ↻ Actualz│  📟 Terminal Interactiva                             │
│          │  $ > \_                          \[▶ Ejecutar]\[🗑]     │
├──────────┴──────────────────────────────────────────────────────┤
│  FENAdmin listo.                          2025-01-01  12:00:00  │  ← Status bar
└─────────────────────────────────────────────────────────────────┘
```
Panel izquierdo — Navegación
👤 Usuarios — Cambia a la vista de gestión de usuarios
👥 Grupos — Cambia a la vista de gestión de grupos
☐ Mostrar sistema — Muestra/oculta usuarios y grupos del sistema (UID/GID < 1000)
↻ Actualizar — Recarga los datos desde el sistema
Panel central — Tabla principal
Haz clic en una columna para ordenar
Doble clic en una fila para editar el usuario/grupo
Clic derecho en un usuario para el menú contextual
Panel inferior — Terminal Interactiva 📟 (nuevo en v1.1)
Reemplaza el panel de actividad estático de versiones anteriores. Es una terminal funcional integrada que:
Muestra en tiempo real cada comando ejecutado por FENAdmin con su resultado
Permite ejecutar comandos del sistema directamente desde la interfaz
Soporta historial de comandos con las teclas `↑` / `↓`
Incluye los comandos `cd`, `clear` y `exit`
Bloquea automáticamente comandos peligrosos (ej: modificar `nobody` o `nogroup`)
Diferencia visualmente éxitos (verde), errores (rojo), advertencias (amarillo) e info (azul)
---
👤 Gestión de Usuarios
Crear un nuevo usuario
Clic en ＋ Nuevo Usuario
Rellena los campos en la pestaña Información Básica:
Nombre de usuario (obligatorio)
Nombre completo / comentario (GECOS)
Directorio home
Shell (selector desplegable con shells disponibles del sistema)
Contraseña inicial (obligatoria, con validación de seguridad)
Marcar si crear directorio home (`-m`)
Selecciona el Tipo de cuenta usando los botones de selección:
`Personalizado` — Usuario estándar sin privilegios especiales
`Desktop User` — Usuario de escritorio con configuraciones básicas
`Admin` — Usuario con privilegios de administrador (sudo, sin expiración)
(Opcional) Configura la pestaña Configuración de cuenta para ajustes avanzados
Clic en Crear usuario
Comando equivalente generado:
```bash
useradd -c 'Nombre Completo' -d /home/user -s /bin/bash -g users -G sudo,docker -m 'username'
echo 'username:contraseña' | chpasswd
```
> ⚠️ Los usuarios de tipo \*\*Admin\*\* no tienen fecha de expiración. Los demás tipos expiran automáticamente a los \*\*90 días\*\*.
Editar un usuario
Doble clic en la fila del usuario, o bien
Clic derecho → ✏ Editar usuario
Puedes modificar: nombre, GECOS, home, shell, contraseña (opcional), tipo de cuenta y permisos avanzados. Si el usuario ya era de tipo Personalizado, los permisos avanzados se cargan automáticamente sin necesidad de reconfigurar el tipo.
Comando equivalente:
```bash
usermod -c 'Nuevo Nombre' -d /nuevo/home -m -s /bin/zsh -l nuevo\_nombre 'usuario'
```
Tipos de cuenta
Tipo	Sudo	Expiración	Permisos avanzados
Admin	✅	Nunca	—
Desktop User	❌	90 días	—
Personalizado	❌	90 días (configurable)	✅ Disponibles
Bloquear un usuario (baja temporal)
Selecciona el usuario → botón 🔒 Bloquear (o clic derecho).
El usuario queda con estado `🔒 Bloqueado` y no puede iniciar sesión, pero su cuenta y datos se conservan intactos.
```bash
passwd -l 'usuario'
```
Desbloquear un usuario
Selecciona el usuario bloqueado → botón 🔓 Desbloquear.
> Si el usuario no tiene contraseña válida, FENAdmin ofrecerá establecer una nueva antes de desbloquear.
```bash
passwd -u 'usuario'
```
Eliminar un usuario (baja definitiva)
Selecciona el usuario → botón 🗑 Eliminar.
Aparece un diálogo con tres opciones:
🗑 SÍ A TODO — Eliminar usuario y su directorio home (`userdel -r`)
✓ Solo usuario — Eliminar solo el usuario, conservar home (`userdel`)
✗ Cancelar — Abortar la operación
```bash
userdel -r 'usuario'    # Con eliminación de home
userdel 'usuario'       # Sin eliminar home
```
Cambiar contraseña
Clic derecho → 🔑 Cambiar contraseña.
```bash
# FENAdmin usa internamente:
echo 'usuario:nuevapass' | chpasswd
```
Ver grupos de un usuario
Clic derecho → 👥 Ver grupos.
---
🔐 Permisos Avanzados (solo tipo Personalizado)
Al editar un usuario de tipo Personalizado, la pestaña Configuración de cuenta habilita una sección de permisos avanzados con switches deslizantes estilo moderno para cada grupo del sistema:
Permiso	Grupo	Descripción
Almacenamiento externo	`plugdev`	Acceder a USB, tarjetas SD, etc.
Impresoras	`lpadmin`	Configurar y gestionar impresoras
Módem/Internet	`dialout`	Conectar a Internet por módem
Redes	`netdev`	Conectar a redes WiFi/Ethernet
Logs del sistema	`adm`	Monitorear registros del sistema
Fax	`fax`	Enviar/recibir faxes
Red local	`sambashare`	Compartir archivos en red local
Audio	`audio`	Usar dispositivos de audio
CD-ROM	`cdrom`	Usar unidades ópticas
Disquete	`floppy`	Usar disqueteras
Escáner	`scanner`	Usar escáneres
Cinta	`tape`	Usar unidades de cinta
Video	`video`	Usar dispositivos de video
Cada cambio se registra en la terminal:
```bash
usermod -aG 'audio' 'usuario'      # Al activar
gpasswd -d 'usuario' 'audio'       # Al desactivar
```
> Si el usuario \*\*ya tenía\*\* algún permiso configurado previamente, los switches se cargan con su estado actual al abrir el diálogo de edición.
---
⚙️ Configuración de cuenta (pestaña avanzada)
Disponible para todos los tipos de usuario. Permite ajustar:
UID — Identificador numérico del usuario (vacío para asignación automática)
Grupo principal — Se establece de uno en uno mediante un campo + botón; reemplaza al usuario anterior si ya había uno
Grupos adicionales — Lista dinámica: agrega grupos uno a uno con ＋ Agregar (o tecla `Enter`) y elimina con ✕ Eliminar
Fecha de expiración — Formato `YYYY-MM-DD` o `never`
Días de inactividad — `-1` para nunca
> Los labels y campos de esta sección se muestran en líneas separadas para mayor claridad visual.
---
👥 Gestión de Grupos
Crear un nuevo grupo
Clic en ＋ Nuevo Grupo
Rellena: nombre del grupo, GID (opcional), miembros iniciales separados por coma, si es grupo de sistema
```bash
groupadd 'nombre\_grupo'
groupadd -g 1500 'nombre\_grupo'        # Con GID específico
groupadd -r 'nombre\_grupo'             # Grupo de sistema
usermod -aG 'nombre\_grupo' 'usuario'   # Añadir miembro
```
Editar un grupo
Doble clic en la fila del grupo o botón ✏ Editar.
Puedes cambiar el nombre, GID y miembros. Los miembros eliminados son removidos con `gpasswd -d`.
```bash
groupmod -n nuevo\_nombre 'grupo'
groupmod -g 1600 'grupo'
usermod -aG 'grupo' 'nuevo\_miembro'
gpasswd -d 'miembro\_removido' 'grupo'
```
Eliminar un grupo
Selecciona el grupo → botón 🗑 Eliminar.
> ⚠️ No se puede eliminar el grupo primario de ningún usuario activo.
```bash
groupdel 'grupo'
```
---
🎨 Modos de color
Usa el botón ☀ Claro / 🌙 Oscuro en la barra superior para cambiar el tema al instante.
Modo	Recomendado para
Oscuro (por defecto)	Terminales de Kali, uso nocturno, menor fatiga visual
Claro	Entornos de oficina, presentaciones, pantallas brillantes
---
⚠️ Notas de seguridad
Siempre ejecuta como root para operaciones de escritura. En modo normal solo se pueden leer datos.
Las contraseñas se pasan via `chpasswd` y no quedan en el historial de bash.
FENAdmin no guarda ningún log propio; usa la terminal interactiva inferior para auditoría visual en sesión.
Para auditoría persistente, combina con `auditd` o revisa `/var/log/auth.log`.
Ten cuidado al eliminar usuarios del sistema (UID < 1000); pueden afectar servicios del SO.
Los comandos `userdel nobody`, `groupdel nogroup` y similares están bloqueados tanto en la interfaz como en la terminal integrada.
---
🛠️ Solución de problemas
Problema	Solución
`ModuleNotFoundError: No module named 'tkinter'`	`sudo apt install python3-tk`
La app abre pero no puede crear usuarios	Ejecuta con `sudo python3 fenadmin.py`
La fuente "Courier New" no se ve bien	Instala `fonts-liberation` o `ttf-liberation`
Ventana muy pequeña / grande	Redimensiona libremente; mínimo 900×600
Error `usermod: user X is currently used by process Y`	El usuario tiene sesión abierta; ciérrala primero
Los permisos avanzados no aparecen	Asegúrate de que el tipo de cuenta sea Personalizado
Al desbloquear un usuario sale error de contraseña	FENAdmin pedirá establecer una nueva contraseña automáticamente
---
💡 Recomendaciones del creador
Kali Linux: Algunos usuarios de sistema son críticos para herramientas de pentesting. Activa "Mostrar sistema" solo si sabes lo que buscas.
Backups: Antes de eliminar usuarios o grupos importantes, haz una copia de `/etc/passwd`, `/etc/shadow` y `/etc/group`:
```bash
  sudo cp /etc/passwd /etc/passwd.bak
  sudo cp /etc/shadow /etc/shadow.bak
  sudo cp /etc/group /etc/group.bak
  ```
Usa la terminal interactiva como aprendizaje: Cada acción realizada desde la GUI muestra el comando real ejecutado. Cópialo y úsalo en tus scripts.
Automatización: Una vez que conozcas los comandos del panel, puedes crear scripts bash para gestión masiva de usuarios.
Filtros avanzados: Usa los filtros por tipo de cuenta, UID, estado o shell para localizar usuarios rápidamente en sistemas con muchas cuentas.
---
📁 Estructura de archivos
```
fenadmin/
├── fenadmin.py           ← Script principal (todo en un archivo)
├── README.md             ← Este documento
└── resources/
    └── logo/
        ├── fenreitsu.png         ← Logo modo claro
        └── fenreitsu-white.png   ← Logo modo oscuro
```
---
📝 Changelog
v1.1
✅ Terminal interactiva funcional en panel inferior (reemplaza panel de actividad estático)
✅ Historial de comandos navegable con `↑` / `↓` en la terminal
✅ Bloqueo de comandos peligrosos en terminal (`nobody`, `nogroup`)
✅ Botones de tipo de cuenta con estilo toggle (azul = seleccionado, gris = no seleccionado)
✅ Permisos avanzados se cargan automáticamente si el usuario ya era Personalizado
✅ Mensaje de advertencia de PERMISOS AVANZADOS visible para cuentas no-Personalizado
✅ Grupo principal y Grupos adicionales ahora son listas dinámicas (agregar/eliminar uno a uno)
✅ Layout de Configuración de cuenta corregido (labels y campos en líneas separadas)
✅ Permisos avanzados reflejados en terminal (activaciones y desactivaciones)
✅ `permisos\_seleccionados` guardado antes del `destroy()` del diálogo (bugfix)
✅ Desbloqueo de usuario solicita nueva contraseña si el usuario no tiene una válida
v0.3
Panel de actividad con tarjetas de notificación
Tipos de cuenta (Admin, Desktop User, Personalizado)
Validación y generador de contraseñas
Filtros avanzados de usuario
Configuración avanzada básica (UID, grupos, expiración)
---
📜 Licencia
Uso libre para fines educativos y administrativos. Créditos al autor original requeridos en redistribuciones.
---
FENAdmin v1.1 — Hecho con ❤️ por @fenreitsu
