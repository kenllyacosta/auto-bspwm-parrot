# auto bspwm-parrot
## Configuración de Entorno para Parrot OS con bspwm

Este script de Bash automatiza la configuración de un entorno profesional para Parrot OS utilizando el gestor de ventanas en mosaico bspwm.

### Descripción
El script realiza las siguientes acciones:

- Actualiza el sistema y lo mejora con parrot-upgrade.
- Instala las dependencias necesarias para el entorno bspwm, Polybar y Picom.
- Descarga y configura diversos repositorios necesarios.
- Instala paquetes adicionales y aplicaciones útiles para hacking.
- Configura temas y plugins para una experiencia de usuario mejorada.
- Limpia archivos temporales y realiza un reinicio opcional del sistema.

### Instalaciones
- kitty v0.35.1
- Neovim v0.10.0
- Visual Studio Code v1.90.0
- bspwm v0.9.10
- sxhkd v0.6.2
- polybar 3.7.1-11
- python2 v2.7.18
- python3 v3.11.2
- pip2 20.3.4
- Picom vgit-c4107
- zsh
- feh
- rofi
- imagemagick
- seclists
- powerlevel10k
- pwntools
- i3lock-fancy
- fzf

### Requisitos
- Parrot OS
- Acceso a internet
- Permisos de superusuario

### Uso
Clone este repositorio y navegue al directorio del script.

```bash
git clone https://github.com/kenllyacosta/auto-bspwm-parrot.git
cd auto-bspwm-parrot
```

Ejecute el script:

```bash
./install.sh
```
> Notas: Asegúrese de ejecutar el script como un usuario normal, no como root.
###
El script comentará la primera línea del archivo /etc/apt/sources.list si el archivo tiene solo dos líneas para evitar errores de actualización.
Durante la ejecución, el script le pedirá que reinicie el sistema al final del proceso de instalación.

## Entorno

### Escritorio
![image](https://github.com/kenllyacosta/auto-bspwm-parrot/assets/7442445/32199466-888b-4416-82f0-03cf73450081)

### Python2 y Phython3
![image](https://github.com/kenllyacosta/auto-bspwm-parrot/assets/7442445/3a678901-ed95-4870-8c52-84236d931943)

### Pip2 y Pip3
![image](https://github.com/kenllyacosta/auto-bspwm-parrot/assets/7442445/27a9169d-13b5-4499-b725-34f29bd587c3)


### Visual Studio Code
![image](https://github.com/kenllyacosta/auto-bspwm-parrot/assets/7442445/f1505cb9-980f-4fd6-a027-cd7fb0a9a9cb)

### Neovim
![image](https://github.com/kenllyacosta/auto-bspwm-parrot/assets/7442445/874b772c-8f22-453e-af5e-aa183e4f623c)

## Contribuciones

Si te apasiona la ciberseguridad y la automatización, únete a nosotros para mejorar el entorno de hacking con bspwm.

Cómo puedes ayudar:

- Reporta bugs
- Propón mejoras
- Mejora la documentación
