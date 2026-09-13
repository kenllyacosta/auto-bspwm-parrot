import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import io
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load("release")
system = load("whichSystem")


class Releases(unittest.TestCase):
    def test_installer_font_archives(self):
        # Asset names published by nerd-fonts v3.5.1; Hurmit is a font family,
        # whereas the downloadable archive is named Hermit.zip.
        data = {"assets": [{"name": name} for name in
                           ("Hack.zip", "Iosevka.zip", "Hermit.zip")]}
        installer = (ROOT / "install.sh").read_text()
        families = re.search(r"for family in (.+); do", installer).group(1).split()
        for family in families:
            with self.subTest(family=family):
                release.select_asset(data, family + ".zip")
        self.assertLess(installer.index('bash "$ROOT/scripts/apply-config.sh"'),
                        installer.index("for family in"))

    def test_architecture_and_ambiguity(self):
        data = {"assets": [{"name": "bat_1_amd64.deb"}, {"name": "bat_1_arm64.deb"}]}
        self.assertEqual(release.select_asset(data, "bat_*_arm64.deb")["name"], "bat_1_arm64.deb")
        for pattern in ("*.deb", "*i386.deb"):
            with self.assertRaises(ValueError):
                release.select_asset(data, pattern)

    def test_prerelease_refused(self):
        with self.assertRaises(ValueError):
            release.select_asset({"prerelease": True, "assets": []}, "*")

    def test_download_digest(self):
        payload = b"test package"
        for valid in (True, False):
            with self.subTest(valid=valid), tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "asset"
                data = {"tag_name": "v1", "assets": [{
                    "name": "asset", "browser_download_url": "https://github.com/test/repo/releases/download/v1/asset",
                    "digest": "sha256:" + (hashlib.sha256(payload).hexdigest() if valid else "0" * 64)}]}
                def download(args, **kwargs):
                    Path(args[-1]).write_bytes(payload)
                with patch.object(release.sys, "argv", ["release.py", "test/repo", "asset", str(target)]), \
                     patch.object(release.urllib.request, "urlopen", return_value=io.BytesIO(json.dumps(data).encode())), \
                     patch.object(release.subprocess, "run", side_effect=download), patch("sys.stdout", new_callable=io.StringIO):
                    if valid:
                        release.main()
                        self.assertEqual(target.read_bytes(), payload)
                    else:
                        with self.assertRaises(ValueError):
                            release.main()
                        self.assertFalse(target.exists())


class SystemHint(unittest.TestCase):
    def test_no_shell_injection(self):
        with patch.object(system.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                system.get_ttl("127.0.0.1; id")
            run.assert_not_called()

    def test_ping_and_timeout(self):
        result = subprocess.CompletedProcess([], 0, "64 bytes: ttl=63 time=2 ms", "")
        with patch.object(system.subprocess, "run", return_value=result) as run:
            self.assertEqual(system.get_ttl("192.0.2.1"), 63)
            self.assertIsInstance(run.call_args.args[0], list)
            self.assertNotIn("shell", run.call_args.kwargs)
        with patch.object(system.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "")):
            with self.assertRaises(ValueError):
                system.get_ttl("192.0.2.1")


if __name__ == "__main__":
    unittest.main()
