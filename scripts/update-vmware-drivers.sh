#!/usr/bin/env bash
# Update the guest kernel, graphics stack and VMware integration from APT.
set -Eeuo pipefail
[[ $(uname -s) == Linux ]] || { echo 'Se requiere Linux.' >&2; exit 1; }
[[ $(systemd-detect-virt --vm) == vmware ]] || { echo 'Solo para invitados VMware.' >&2; exit 1; }
source /etc/os-release
[[ $ID == parrot || $ID == kali ]] || { echo 'Se requiere Parrot o Kali.' >&2; exit 1; }
[[ $(dpkg --print-architecture) == amd64 ]] || { echo 'Este script requiere amd64.' >&2; exit 1; }
sudo apt-get update
sudo apt-get --no-remove install -y linux-image-amd64 open-vm-tools \
    open-vm-tools-desktop libgl1-mesa-dri mesa-vulkan-drivers xserver-xorg-video-vmware
printf '\nActualización finalizada. Reinicia para cargar cualquier núcleo o controlador actualizado.\n'
