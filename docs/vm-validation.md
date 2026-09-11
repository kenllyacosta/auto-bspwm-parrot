# Validación en VMware

Utilizar una VM de Parrot 7 y otra de Kali Rolling, con usuario normal y sudo,
escritorio original instalado y espacio para una instantánea. No usar una VM con
trabajo sin guardar. Mantener la misma imagen base al reproducir un archivo de versiones.

## Matriz de aceptación

| Prueba | Parrot 7 | Kali Rolling |
| --- | --- | --- |
| Instantánea previa | Creada: `auto-bspwm-before-refactor-20260911` | Pendiente |
| Instalación latest completa | Pendiente | Pendiente |
| Arranque X11, barra, Kitty, red y audio | Pendiente | Pendiente |
| Bloqueo y desbloqueo | Pendiente | Pendiente |
| Volver al escritorio original | Pendiente | Pendiente |
| Reiniciar y volver a bspwm | Pendiente | Pendiente |
| Reinstalación con versiones fijas | Pendiente | Pendiente |

Esta tabla registra el estado real; CI no acredita una prueba de escritorio.

## Procedimiento

1. Con la VM apagada, crear una instantánea desde VMware. La VM Parrot indicada
   por el propietario ya tiene la instantánea de la tabla. No se restaura ni elimina
   automáticamente: una restauración descartaría el trabajo posterior.
2. Iniciar la VM y transferir el código actualizado a una carpeta del usuario.
3. Ejecutar `bash install.sh` en una terminal como usuario normal. Introducir la
   contraseña de sudo localmente cuando se solicite. Guardar el directorio
   `~/.local/state/auto-bspwm/runs/<ejecución>` que muestra el instalador.
4. Cerrar sesión, elegir **bspwm** y abrir Neovim para terminar la instalación
   de plugins. Ejecutar desde una terminal de esa sesión:

   ```bash
   python3 scripts/validate.py "$HOME/.local/state/auto-bspwm/runs/<ejecución>"
   ```

   El informe JSON y la captura quedan dentro del directorio de la ejecución.
   Las pruebas manuales pendientes se enumeran en el informe.
5. Comprobar los atajos, audio, red, VPN si existe, bloqueo/desbloqueo y capturas.
   Cerrar sesión y comprobar que el escritorio original sigue accesible.
   Reiniciar y probar de nuevo. Ajustar resolución o probar un segundo monitor.
6. Volver a bspwm y congelar las versiones, sin editar el código entre instalación
   y congelación:

   ```bash
   python3 scripts/pins.py freeze "$HOME/.local/state/auto-bspwm/runs/<ejecución>" parrot7-amd64.lock.json
   ```

   No sobrescribe archivos existentes. El lock conserva `validation: not-certified`:
   las versiones exactas no prueban por sí solas la compatibilidad gráfica.
7. En un clon de la misma imagen base y con el mismo código, instalar con:

   ```bash
   bash install.sh --locked parrot7-amd64.lock.json
   ```

   No utiliza latest ni cambia de versiones si un servidor deja de publicarlas:
   debe fallar. Guardar la instantánea y los instaladores externos si se necesita
   reconstruir el entorno años después. Los repositorios Rolling retiran versiones.
8. Repetir en Kali y usar un lock distinto por distribución y arquitectura.

## Acceso al invitado

La instantánea y el arranque se pueden hacer sin la contraseña del invitado.
Para instalar dentro de Parrot hace falta una sesión local o SSH autorizado.
No guardar contraseñas en scripts, argumentos de vmrun, locks ni registros.
Si se usa SSH, limitarlo a la red de laboratorio y utilizar una clave temporal
que se retire al finalizar la validación.
