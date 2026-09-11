import os
from pathlib import Path
import platform
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(platform.system() == "Linux" and getattr(os, "geteuid", lambda: 0)() != 0,
                     "Requires a normal Linux user")
class ConfigRepair(unittest.TestCase):
    def test_repairs_shortcuts_and_permissions_with_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            config = home / ".config/sxhkd"
            config.mkdir(parents=True)
            (config / "sxhkdrc").write_text("old terminal shortcut")
            bin_dir = home / "bin"
            bin_dir.mkdir()
            for program in ("bspwm", "sxhkd", "rofi"):
                stub = bin_dir / program
                stub.write_text("#!/bin/sh\nexit 0\n")
                stub.chmod(0o755)
            env = {**os.environ, "HOME": str(home), "XDG_CONFIG_HOME": str(home / ".config"),
                   "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]}
            env.pop("BSPWM_CONFIG_BACKUP", None)
            subprocess.run(["bash", str(ROOT / "scripts/apply-config.sh")], env=env,
                           check=True, capture_output=True, text=True)
            self.assertIn("\tkitty", (config / "sxhkdrc").read_text())
            menu = home / ".config/polybar/scripts/powermenu_alt"
            self.assertTrue(os.access(menu, os.X_OK))
            saved = list((home / ".local/state/auto-bspwm/backups").glob("*/.config/sxhkd/sxhkdrc"))
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0].read_text(), "old terminal shortcut")


if __name__ == "__main__":
    unittest.main()
