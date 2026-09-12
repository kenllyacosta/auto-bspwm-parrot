import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('hardware', Path(__file__).resolve().parents[1] / 'scripts/hardware.py')
hardware = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hardware)


class HardwarePackages(unittest.TestCase):
    def test_vm_uses_guest_tools_not_host_firmware(self):
        selected = hardware.packages('amd64', 'vmware', 'GenuineIntel', {'0x8086'}, {'iwlwifi'})
        self.assertIn('open-vm-tools-desktop', selected)
        self.assertNotIn('intel-microcode', selected)
        self.assertNotIn('firmware-iwlwifi', selected)

    def test_physical_machine_selects_cpu_gpu_and_wifi(self):
        selected = hardware.packages('amd64', 'none', 'AuthenticAMD', {'0x1002'}, {'iwlwifi', 'r8169'})
        for package in ('amd64-microcode', 'firmware-amd-graphics', 'firmware-iwlwifi', 'firmware-realtek'):
            self.assertIn(package, selected)
        self.assertNotIn('open-vm-tools', selected)

    def test_arm_does_not_get_x86_kernel_or_microcode(self):
        selected = hardware.packages('arm64', 'none', 'ARM', set(), set())
        self.assertNotIn('linux-image-amd64', selected)
        self.assertNotIn('intel-microcode', selected)
