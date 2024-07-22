#!/bin/bash

# Colours
greenColour="\e[0;32m\033[1m"
redColour="\e[0;31m\033[1m"
blueColour="\e[0;34m\033[1m"
endColour="\033[0m\e[0m"

if [ "$(whoami)" == "root" ]; then
    exit 1
fi

trap ctrl_c INT

function ctrl_c(){
	echo -e "\n\n${redColour}[!] Saliendo...\n${endColour}"
	exit 1
}

# Comentamos la primera línea de este archivo /etc/apt/sources.list para evitar errores de actualización
if [ $(wc -l < /etc/apt/sources.list) -eq 2 ]; then
    sudo sed -i '1s/^/#/' /etc/apt/sources.list
fi

ruta=$(pwd)

echo -e "\n\n${blueColour}[*] Actualizando el sistema, por favor espere...\n${endColour}"
sleep 2

# Actualizando el sistema
sudo apt update
sudo parrot-upgrade
if [ $? != 0 ] && [ $? != 130 ]; then
	echo -e "\n${redColour}[-] Falló la actualización del sistema.\n${endColour}"
	exit 1
else
	echo -e "\n${greenColour}[+] Done\n${endColour}"
	sleep 1.5
fi

echo -e "\n\n${blueColour}[*] Instalando dependencias.\n${endColour}"
sleep 2
# Instalando dependencias del Entorno
sudo apt install -y build-essential git vim xcb libxcb-util0-dev libxcb-ewmh-dev libxcb-randr0-dev libxcb-icccm4-dev libxcb-keysyms1-dev libxcb-xinerama0-dev libasound2-dev libxcb-xtest0-dev libxcb-shape0-dev
if [ $? != 0 ] && [ $? != 130 ]; then
	echo -e "\n${redColour}[-] Falló la instalación de dependencias del entorno.\n${endColour}"
	exit 1
else
	echo -e "\n${greenColour}[+] Done\n${endColour}"
	sleep 1.5
fi

echo -e "\n\n${blueColour}[*] Instalando dependencias de la Polybar.\n${endColour}"
sleep 2
# Instalando requerimientos para la Polybar
sudo apt install -y cmake cmake-data pkg-config python3-sphinx libcairo2-dev libxcb1-dev libxcb-util0-dev libxcb-randr0-dev libxcb-composite0-dev python3-xcbgen xcb-proto libxcb-image0-dev libxcb-ewmh-dev libxcb-icccm4-dev libxcb-xkb-dev libxcb-xrm-dev libxcb-cursor-dev libasound2-dev libpulse-dev libjsoncpp-dev libmpdclient-dev libuv1-dev libnl-genl-3-dev
if [ $? != 0 ] && [ $? != 130 ]; then
	echo -e "\n${redColour}[-] Falló la instalación de dependencias de la Polybar.\n${endColour}"
	exit 1
else
	echo -e "\n${greenColour}[+] Done\n${endColour}"
	sleep 1.5
fi

echo -e "\n\n${blueColour}[*] Instalando dependencias de Picom.\n${endColour}"
sleep 2
# Dependencias de Picom
sudo apt install -y meson libxext-dev libxcb1-dev libxcb-damage0-dev libxcb-xfixes0-dev libxcb-shape0-dev libxcb-render-util0-dev libxcb-render0-dev libxcb-composite0-dev libxcb-image0-dev libxcb-present-dev libxcb-xinerama0-dev libpixman-1-dev libdbus-1-dev libconfig-dev libgl1-mesa-dev libpcre2-dev libevdev-dev uthash-dev libev-dev libx11-xcb-dev libxcb-glx0-dev libpcre3 libpcre3-dev
if [ $? != 0 ] && [ $? != 130 ]; then
	echo -e "\n${redColour}[-] Falló la instalación de dependencias de Picom.\n${endColour}"
	exit 1
else
	echo -e "\n${greenColour}[+] Done\n${endColour}"
	sleep 1.5
fi

echo -e "\n\n${blueColour}[*] Instalando paquetes adicionales.\n${endColour}"
sleep 2
# Instalamos paquetes adionales
sudo apt install -y feh scrot scrub zsh rofi xclip bat locate neofetch wmname acpi bspwm sxhkd imagemagick ranger kitty seclists
if [ $? != 0 ] && [ $? != 130 ]; then
	echo -e "\n${redColour}[-] Falló la instalación de paquetes adicionales.\n${endColour}"
	exit 1
else
	echo -e "\n${greenColour}[+] Done\n${endColour}"
	sleep 1.5
fi

# Creando carpeta de Reposistorios
mkdir ~/github

# Descargar Repositorios Necesarios
cd ~/github
git clone --recursive https://github.com/polybar/polybar
git clone https://github.com/ibhagwan/picom.git
git clone https://github.com/NvChad/starter ~/.config/nvim
git clone https://github.com/meskarune/i3lock-fancy.git
sudo mkdir /root/.config/nvim
sudo git clone https://github.com/NvChad/starter /root/.config/nvim
wget https://github.com/neovim/neovim/releases/download/v0.10.0/nvim-linux64.tar.gz

# Desinstalamos las apps que no necesitamos
sudo apt remove -y neovim
sudo apt remove -y kitty 

echo -e "\n\n${blueColour}[*] Instalando nvim y otras apps...\n${endColour}"
sleep 2
# Instalamos Neovim
cd ~/github
tar -xf nvim-linux64.tar.gz
rm nvim-linux64.tar.gz
sudo cp -rv nvim-linux64 /opt/nvim/

# Instalamos i3lock-fancy
cd ~/github/i3lock-fancy
sudo make install

# Instalando Polybar
cd ~/github/polybar
mkdir build
cd build
cmake ..
make -j$(nproc)
sudo make install

# Instalando Picom
cd ~/github/picom
git submodule update --init --recursive
meson --buildtype=release . build
ninja -C build
sudo ninja -C build install

# Instalando p10k
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/.powerlevel10k
echo 'source ~/.powerlevel10k/powerlevel10k.zsh-theme' >>~/.zshrc

# Instalando p10k root
sudo git clone --depth=1 https://github.com/romkatv/powerlevel10k.git /root/.powerlevel10k

# Configuramos el tema Nord de Rofi:
mkdir -p ~/.config/rofi/themes
cp $ruta/rofi/nord.rasi ~/.config/rofi/themes/

echo -e "\n\n${blueColour}[*] Instalando LSD.\n${endColour}"
sleep 2
# Instando lsd
sudo dpkg -i $ruta/lsd.deb
sleep 2
if [ $? != 0 ] && [ $? != 130 ]; then
	echo -e "\n${redColour}[-] Falló la instalación de lsd.\n${endColour}"
	sleep 3
else
	echo -e "\n${greenColour}[+] Done\n${endColour}"
	sleep 1.5
fi

echo -e "\n\n${blueColour}[*] Instalando bat.\n${endColour}"
sleep 2
# Instando lsd
sudo dpkg -i $ruta/bat.deb
sleep 2
if [ $? != 0 ] && [ $? != 130 ]; then
	echo -e "\n${redColour}[-] Falló la instalación de bat.\n${endColour}"
	sleep 3
else
	echo -e "\n${greenColour}[+] Done\n${endColour}"
	sleep 1.5
fi

echo -e "\n\n${blueColour}[*] Instalando Visual Studio Code.\n${endColour}"
sleep 2
# Instalando Visual Studio Code
sudo dpkg -i $ruta/vscode.deb
if [ $? != 0 ] && [ $? != 130 ]; then
	echo -e "\n${redColour}[-] Falló la instalación de Visual Studio Code.\n${endColour}"
	sleep 3
else
	echo -e "\n${greenColour}[+] Done\n${endColour}"
	sleep 1.5
fi

echo -e "\n\n${blueColour}[*] Instalando Python2.7.18.\n${endColour}"
sleep 2
# Instalamos python2.7.18
cd $ruta/
wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
tar xzf Python-2.7.18.tgz
cd $ruta/Python-2.7.18/
./configure --enable-optimizations
sudo make install
if [ $? != 0 ] && [ $? != 130 ]; then
	echo -e "\n${redColour}[-] Falló la instalación de Python2.7.18.\n${endColour}"
	sleep 3
else
	echo -e "\n${greenColour}[+] Done\n${endColour}"
	sleep 1.5
fi

echo -e "\n\n${blueColour}[*] Instalando pip2.\n${endColour}"
sleep 2
# Instalando pip2
curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py
sudo python2 get-pip.py
if [ $? != 0 ] && [ $? != 130 ]; then
	echo -e "\n${redColour}[-] Falló la instalación de pip2.\n${endColour}"
	sleep 3
else
	echo -e "\n${greenColour}[+] Done\n${endColour}"
	sleep 1.5
fi

echo -e "\n\n${blueColour}[*] Instalando paquetes de python.\n${endColour}"
# Instalando paquetes de Python
sudo pip3 install pwntools --break-system-packages
sudo pip2 install pwntools
if [ $? != 0 ] && [ $? != 130 ]; then
	echo -e "\n${redColour}[-] Falló la instalación de pwntools.\n${endColour}"
	sleep 3
else
	echo -e "\n${greenColour}[+] Done\n${endColour}"
	sleep 1.5
fi

# Instalamos las HackNerdFonts
sudo cp -v $ruta/fonts/HNF/* /usr/local/share/fonts/

# Instalando Fuentes de Polybar
sudo cp -v $ruta/Config/polybar/fonts/* /usr/share/fonts/truetype/

# Copiando Archivos de Configuración
cp -rv $ruta/Config/* ~/.config/
sudo cp -rv $ruta/Config/* /root/.config/
sudo cp -rv $ruta/kitty /opt/

# Kitty Root
sudo cp -rv $ruta/Config/kitty /root/.config/

# Copia de configuracion de .p10k.zsh y .zshrc
rm -rf ~/.zshrc
cp -v $ruta/.zshrc ~/.zshrc

cp -v $ruta/.p10k.zsh ~/.p10k.zsh
sudo cp -v $ruta/.p10k.zsh-root /root/.p10k.zsh

# Script
sudo cp -v $ruta/scripts/whichSystem.py /usr/local/bin/
sudo cp -v $ruta/scripts/screenshot /usr/local/bin/

# Plugins ZSH
sudo apt install -y zsh-syntax-highlighting zsh-autosuggestions zsh-autocomplete
sudo mkdir /usr/share/zsh-sudo
cd /usr/share/zsh-sudo
sudo wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/plugins/sudo/sudo.plugin.zsh

# Cambiando de SHELL a zsh
chsh -s /usr/bin/zsh
sudo usermod --shell /usr/bin/zsh root
sudo ln -s -fv ~/.zshrc /root/.zshrc

# Asignamos Permisos a los Scritps
chmod +x ~/.config/bspwm/bspwmrc
chmod +x ~/.config/bspwm/scripts/bspwm_resize
chmod +x ~/.config/bin/ethernet_status.sh
chmod +x ~/.config/bin/htb_status.sh
chmod +x ~/.config/bin/htb_target.sh
chmod +x ~/.config/polybar/launch.sh
sudo chmod +x /usr/local/bin/whichSystem.py
sudo chmod +x /usr/local/bin/screenshot

# Configuramos el Tema de Rofi
rofi-theme-selector
sleep 3

echo -e "\n\n${blueColour}[*] Limpiando archivos temporales usados...\n${endColour}"
sleep 2
# Removiendo Repositorio
sudo rm -rf ~/github
sudo rm -rf $ruta
if [ $? != 0 ] && [ $? != 130 ]; then
	echo -e "\n${redColour}[-] Falló la limpieza de archivos temporales.\n${endColour}"
	sleep 3
else
	echo -e "\n${greenColour}[+] Done\n${endColour}"
	sleep 1.5
fi

# Actualizando la base de datos de locate
sudo updatedb
sudo umount /run/user/1000/gvfs 
sudo umount /run/user/1000/doc

# Actualizando de los paquetes instalados
sudo apt update
sudo parrot-upgrade

sudo apt autoremove -y

# Mensaje de instalación completada
notify-send "BSPWM INSTALADO"

while true; do
	echo -en "\n${yellowColour}[?] Instalación completada, es necesario reiniciar el sistema. ¿Deseas reiniciar ahora? ([y]/n) ${endColour}"
	read -r
	REPLY=${REPLY:-"y"}
	if [[ $REPLY =~ ^[Yy]$ ]]; then
		echo -e "\n\n${greenColour}[+] Restarting the system...\n${endColor}"
		sleep 1
		sudo reboot
	elif [[ $REPLY =~ ^[Nn]$ ]]; then
		exit 0
	else
		echo -e "\n${redColour}[!] Invalid response, please try again\n${endColour}"
	fi
done