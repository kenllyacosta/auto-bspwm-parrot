# auto-bspwm — Parrot 7 y Kali Linux

Entorno bspwm para **Parrot OS 7.x y Kali Rolling**, en **amd64 y arm64**.
Instalar en una edición de escritorio con usuario normal y sudo, conexión a Internet
y repositorios oficiales funcionando. No mezclar repositorios de Kali y Parrot.

Parrot 7 usa KDE Plasma 6/Wayland por defecto. Este proyecto añade una sesión
**bspwm sobre X11**; selecciona bspwm en el gestor de acceso después de cerrar sesión.
No sustituye KDE/Xfce ni configura bspwm como compositor Wayland.

## Instalación

Desde el repositorio:

```bash
bash install.sh
```

Se puede ejecutar desde cualquier directorio. Opciones:

```bash
bash install.sh --help
bash install.sh --change-shell
bash install.sh --upgrade-system
bash install.sh --repo-only
bash install.sh --locked parrot7-amd64.lock.json
```

- Por defecto instala las últimas publicaciones estables de Neovim, Kitty, bat,
  lsd y Nerd Fonts (Hack, Iosevka y Hurmit), consultando GitHub al ejecutar.
  VS Code se descarga del canal estable oficial de Microsoft.
- bspwm, sxhkd, Polybar, Picom, Python 3, fzf y el resto de herramientas usan el
  candidato más reciente de los repositorios de la distribución tras actualizar
  sus índices. Esto **no equivale necesariamente a la última versión upstream**.
- NvChad starter y Powerlevel10k se clonan desde sus ramas predeterminadas actuales;
  se registra el commit. NvChad instala sus plugins al abrir Neovim por primera vez.
  El antiguo `Config/nvim/init.lua` queda como referencia y no se instala.
- pwntools se instala/actualiza con pipx, aislado del Python del sistema.
  Para importar `pwn` desde tus propios scripts, crea un entorno con
  `python3 -m venv .venv`, actívalo e instala allí `pwntools`.
- `--repo-only` usa APT para Neovim, Kitty, bat y lsd y omite VS Code; las fuentes,
  NvChad, Powerlevel10k y pwntools siguen requiriendo Internet.
- `--upgrade-system` solicita además `apt-get --no-remove full-upgrade`.
  Todas las operaciones APT abortan si requieren eliminar paquetes; se conserva
  el escritorio original y su gestor de acceso. No se combina con `--locked`.
- `--change-shell` cambia a Zsh la shell de tu usuario; Kitty ya inicia Zsh.

El instalador reemplaza las configuraciones administradas, pero antes guarda una
copia bajo `~/.local/state/auto-bspwm/backups/<ejecución>/`.
Repetirlo vuelve a consultar versiones y aplicar la configuración del proyecto:
**guarda tus ajustes personales antes de actualizar**. No es una transacción:
si falla, puede haber paquetes ya instalados y configuraciones parcialmente aplicadas.
Corrige el error indicado en el registro y vuelve a ejecutar.

Registros, versiones APT, commits y sumas SHA-256 se guardan en
`~/.local/state/auto-bspwm/`. Se verifica el digest de GitHub cuando está disponible;
si upstream no lo publica se avisa y se usa HTTPS, sin afirmar verificación
criptográfica independiente. VS Code usa HTTPS y APT valida estructura/dependencias
del paquete local, no una firma de repositorio para esa descarga.
Ante límites de API puede proporcionarse `GITHUB_TOKEN`; no se imprime en registros.

Los antiguos `*.deb`, `kitty/`, `fonts/HNF/` y las fuentes binarias de Polybar
**se retiraron del árbol de trabajo** y están excluidos por `.gitignore`.
El historial Git no se reescribió. Se usan las Nerd Fonts descargadas con sus
avisos de licencia, sin depender de Helvetica ni de archivos de licencia incierta.
No se instala Python 2, pip2 ni el fork antiguo de Picom.
No se alteran fuentes APT ni claves, no se modifica root, no se borra el repositorio
y no se reinicia automáticamente.

## Uso del escritorio

- Super + Enter: Kitty; Super + D: Rofi.
- Super + Shift + L: bloquear; Super + Alt + Q: cerrar sesión bspwm.
- Print: selección; Ctrl + Print: pantalla; Alt + Print: ventana.
- Capturas en `~/ScreenShots/`.
- `settarget IP nombre`: objetivo de la barra; `settarget` lo limpia.
- Red: interfaz de la ruta predeterminada. VPN: primera tun/tap/wg numerada.
  Para nombres diferentes, exporta `BSPWM_NETWORK_INTERFACE` y
  `BSPWM_VPN_INTERFACE` antes del inicio de la sesión.
- La batería se detecta y su módulo se omite en equipos sin batería.
- La barra predeterminada ocupa el ancho del monitor y se inicia en cada salida.
  Omite módulos secundarios en resoluciones pequeñas. Para recuperar el diseño
  anterior exporta `BSPWM_BAR_LAYOUT=classic` antes de iniciar bspwm.
- El audio usa PulseAudio o la compatibilidad PulseAudio de PipeWire.
- Para el fondo ejecuta `feh --bg-fill /ruta/imagen.jpg`; se recupera en el próximo inicio.
- Burp Suite y SecLists no forman parte de la instalación básica; instálalos
  desde los repositorios si los necesitas. El atajo de Burp requiere ese paquete.

## Versiones fijas y recuperación

Cada instalación completa guarda sus descargas con SHA-256, commits y versiones
de APT/Python en `~/.local/state/auto-bspwm/runs/<ejecución>/`. Abre Neovim para
inicializar sus plugins y prueba el escritorio. Después ejecuta:

```bash
python3 scripts/validate.py "$HOME/.local/state/auto-bspwm/runs/<ejecución>"
python3 scripts/pins.py freeze "$HOME/.local/state/auto-bspwm/runs/<ejecución>" parrot7-amd64.lock.json
```

Para reproducir esa selección en un clon de la misma imagen base:

```bash
bash install.sh --locked parrot7-amd64.lock.json
```

El lock fija los archivos descargados (incluido VS Code), sus sumas, Powerlevel10k,
NvChad starter, lazy.nvim, el lock de plugins, las versiones APT instaladas y las
dependencias Python de pwntools. Requiere la misma distribución, versión,
arquitectura y contenido del proyecto; no cae silenciosamente a `latest`.
El inventario APT incluye el escritorio de la máquina de referencia: utiliza
un clon de la misma base, no una máquina con un escritorio diferente.

La congelación requiere una ejecución completa y no sobrescribe locks existentes.
Un lock **no certifica** una prueba gráfica: se genera con `validation: not-certified`.
No hay un lock validado predefinido hasta terminar las pruebas en las VMs.
Los paquetes tienen que seguir disponibles en sus servidores; conserva una
instantánea para restauraciones duraderas. Los paquetes Python se fijan por versión,
no por hash de wheel, y los compiladores/build dependencies de PyPI pueden variar.
No incluye herramientas LSP/Mason ni configuraciones personales ajenas al proyecto.
Se trata de reproducir la selección de versiones, no de una imagen bit a bit idéntica.

Protocolo y estado real de las pruebas: [validación en VMware](docs/vm-validation.md).

1. Prueba primero en una VM con instantánea de Parrot 7 y otra de Kali Rolling.
   Las comprobaciones automatizadas no sustituyen un arranque gráfico real.
2. Mantén el escritorio original y el gestor de acceso para poder recuperar
   configuraciones desde otra sesión. Copia desde el respaldo únicamente los
   archivos que quieras restaurar; los paquetes del sistema no se revierten.
3. Conserva el lock, el código correspondiente y la instantánea de la VM validada.
   Cada nueva actualización debe pasar por una VM antes de sustituir ese conjunto.
4. Los binarios antiguos se retiraron; los `.deb` y bundles descargados no deben
   volver al repositorio. Las fuentes decorativas se sustituyeron por Nerd Fonts.
5. Algunas aplicaciones o plugins pueden necesitar dependencias adicionales
   (por ejemplo servidores LSP). Instálalas según tu lenguaje y flujo de trabajo.
6. Revisa escalado e iconos en tu hardware; el diseño clásico sigue siendo opcional
   y está pensado para pantallas amplias.
7. Usa un laboratorio aislado para herramientas heredadas que requieran Python 2.

## Validación

Si la instalación se interrumpió y los atajos o botones conservan rutas antiguas,
puedes reparar la configuración sin reinstalar paquetes:

```bash
bash scripts/apply-config.sh
```

Ejecuta como tu usuario habitual. Guarda un respaldo antes de sustituir la
configuración; después cierra sesión y selecciona **bspwm (X11)**.

En una VM VMware amd64, actualiza el núcleo, Mesa y la integración del invitado
con `bash scripts/update-vmware-drivers.sh`. Usa las versiones candidatas de los
repositorios configurados, conserva sus prioridades y no reinicia automáticamente.

```bash
bash -n install.sh
python3 -m unittest discover -s tests -v
```

CI comprueba sintaxis, selección de assets, integridad, rechazo de locks inválidos,
reproducción sin consultar latest y procesamiento de ping. No ejecuta una
instalación con privilegios ni prueba una sesión gráfica.
La compatibilidad con Parrot/Kali es el objetivo de esta refactorización y requiere
validación final en esas distribuciones; no se garantiza compatibilidad con
versiones futuras arbitrarias.

Referencias oficiales:
[Parrot 7](https://parrotsec.org/blog/2025-12-24-parrot-7.0-release-notes/),
[escritorios Kali](https://www.kali.org/docs/general-use/switching-desktop-environments/),
[Neovim](https://github.com/neovim/neovim/blob/master/INSTALL.md),
[Kitty](https://sw.kovidgoyal.net/kitty/binary/),
[VS Code Linux](https://code.visualstudio.com/docs/setup/linux).
