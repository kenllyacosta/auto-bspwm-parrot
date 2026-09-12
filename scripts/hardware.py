#!/usr/bin/env python3
"""Print distro package candidates for detected Linux hardware, one per line."""
from pathlib import Path
import subprocess
import sys


def packages(arch, virtual, cpu, gpu_vendors, net_modules):
    result = ['libgl1-mesa-dri', 'mesa-vulkan-drivers']
    if arch == 'amd64':
        result.append('linux-image-amd64')
    if virtual == 'vmware':
        return result + ['open-vm-tools', 'open-vm-tools-desktop', 'xserver-xorg-video-vmware']
    if virtual == 'oracle':
        return result + ['virtualbox-guest-utils', 'virtualbox-guest-x11']
    if virtual in ('kvm', 'qemu'):
        return result + ['qemu-guest-agent', 'spice-vdagent']
    if virtual != 'none':
        return result
    if arch == 'amd64':
        if 'GenuineIntel' in cpu:
            result.append('intel-microcode')
        elif 'AuthenticAMD' in cpu:
            result.append('amd64-microcode')
    if '0x1002' in gpu_vendors:
        result.append('firmware-amd-graphics')
    if '0x8086' in gpu_vendors:
        result.append('firmware-intel-graphics')
    if '0x10de' in gpu_vendors:
        result.append('firmware-nvidia-graphics')
        print('NVIDIA detectada: se conserva el controlador actual; revisa nvidia-driver y Secure Boot si necesitas el controlador propietario.', file=sys.stderr)
    firmware = {'iwlwifi': 'firmware-iwlwifi', 'r8169': 'firmware-realtek',
                'r8168': 'firmware-realtek', 'brcmfmac': 'firmware-brcm80211',
                'brcmsmac': 'firmware-brcm80211', 'ath9k': 'firmware-atheros',
                'ath10k_pci': 'firmware-atheros', 'ath11k_pci': 'firmware-atheros',
                'ath12k': 'firmware-atheros'}
    for module in net_modules:
        package = firmware.get(module)
        if module.startswith(('rtw', 'rtl')):
            package = 'firmware-realtek'
        elif module.startswith('mt7'):
            package = 'firmware-mediatek'
        if package:
            result.append(package)
    return list(dict.fromkeys(result))


def main():
    arch = subprocess.check_output(['dpkg', '--print-architecture'], text=True).strip()
    detection = subprocess.run(['systemd-detect-virt', '--vm'], capture_output=True, text=True)
    virtual = detection.stdout.strip() or 'unknown'
    cpu = Path('/proc/cpuinfo').read_text()
    vendors = {p.read_text().strip() for p in Path('/sys/class/drm').glob('card[0-9]*/device/vendor')}
    modules = {p.resolve().name for p in Path('/sys/class/net').glob('*/device/driver/module')}
    if arch != 'amd64':
        print('Arquitectura no amd64: se conserva el metapaquete del núcleo del fabricante; APT actualizará sus paquetes ya instalados.', file=sys.stderr)
    print('\n'.join(packages(arch, virtual, cpu, vendors, modules)))


if __name__ == '__main__':
    main()
