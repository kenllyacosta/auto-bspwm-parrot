import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_scripts import load

pins = load("pins")
release = load("release")


def fixture():
    return {"schema": 1, "platform": {"id": "parrot", "version": "7.0", "arch": "amd64", "mode": "latest"},
            "source_sha256": pins.source_hash(),
            "artifacts": {"repo:asset": {"key": "repo:asset", "url": "https://example.com/fixed-1",
                                        "sha256": hashlib.sha256(b"asset").hexdigest()}},
            "git": {"p10k": "a" * 40, "nvchad": "b" * 40, "lazy": "c" * 40},
            "apt": ["bspwm=0.9.10-2", "libc6:amd64=2.41-12"],
            "python": ["pwntools==4.15.0"], "lazy_lock": {"plugin": {"commit": "d" * 40}}}


class Pins(unittest.TestCase):
    def test_capture_round_trip_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            run = base / "run"
            run.mkdir()
            home = base / "home"
            nvim = home / ".config/nvim"
            nvim.mkdir(parents=True)
            data = fixture()
            (run / "platform.json").write_text(json.dumps(data["platform"]))
            (run / "source.sha256").write_text(data["source_sha256"])
            (run / "complete").touch()
            (run / "artifacts.jsonl").write_text(json.dumps(data["artifacts"]["repo:asset"]) + "\n")
            for name in ("p10k", "nvchad"):
                (run / f"{name}.txt").write_text(data["git"][name])
            (run / "apt.txt").write_text("\n".join(data["apt"]))
            (run / "python.txt").write_text("\n".join(data["python"]))
            (nvim / "lazy-lock.json").write_text(json.dumps(data["lazy_lock"]))
            output = base / "versions.json"
            with patch.object(pins.Path, "home", return_value=home), \
                 patch.object(pins, "run", return_value=data["git"]["lazy"]):
                pins.capture(run, output)
                captured = pins.load(output)
                self.assertEqual(captured["artifacts"], data["artifacts"])
                self.assertEqual(captured["git"], data["git"])
                self.assertEqual(captured["validation"], "not-certified")
                original = output.read_bytes()
                with self.assertRaises(FileExistsError):
                    pins.capture(run, output)
                self.assertEqual(output.read_bytes(), original)

    def test_reject_unpinned_inputs(self):
        for field, value in (("git", {"p10k": "main"}), ("apt", ["bspwm"]),
                             ("python", ["pwntools"]), ("python", ["--index-url=evil"])):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                data = fixture()
                data[field] = value
                path = Path(tmp) / "lock.json"
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    pins.load(path)

    def test_platform_and_code_must_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lock.json"
            path.write_text(json.dumps(fixture()))
            with patch("sys.argv", ["pins.py", "check", str(path), "kali", "7.0", "amd64"]):
                with self.assertRaises(ValueError):
                    pins.main()
            with patch("sys.argv", ["pins.py", "check", str(path), "parrot", "7.0", "amd64"]):
                pins.main()
                with patch.object(pins, "source_hash", return_value="different"):
                    with self.assertRaises(ValueError):
                        pins.main()

    def test_locked_download_never_resolves_latest(self):
        for correct in (True, False):
            with self.subTest(correct=correct), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "lock.json"
                path.write_text(json.dumps(fixture()))
                target = Path(tmp) / "download"
                def download(args, **kwargs):
                    target.write_bytes(b"asset" if correct else b"changed")
                    return subprocess.CompletedProcess(args, 0, "https://example.com/fixed-1", "")
                with patch.dict("os.environ", {"BSPWM_LOCK_FILE": str(path)}), \
                     patch("sys.argv", ["release.py", "repo", "asset", str(target)]), \
                     patch.object(release.urllib.request, "urlopen") as latest, \
                     patch.object(release.subprocess, "run", side_effect=download), \
                     patch("sys.stdout", new_callable=io.StringIO):
                    if correct:
                        release.main()
                    else:
                        with self.assertRaises(ValueError):
                            release.main()
                        self.assertFalse(target.exists())
                    latest.assert_not_called()

    def test_incomplete_install_cannot_freeze(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            (run / "platform.json").write_text(json.dumps(fixture()["platform"]))
            with self.assertRaises(ValueError):
                pins.capture(run, run / "lock.json")
            self.assertFalse((run / "lock.json").exists())

    def test_vscode_pins_the_final_cdn_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "code.deb"
            final_url = "https://update.code.visualstudio.com/commit:abc/linux-deb-x64/stable"
            def download(args, **kwargs):
                target.write_bytes(b"deb")
                return subprocess.CompletedProcess(args, 0, final_url, "")
            with patch.dict("os.environ", {}, clear=True), \
                 patch("sys.argv", ["release.py", "--vscode", "https://update.code.visualstudio.com/latest/linux-deb-x64/stable", str(target)]), \
                 patch.object(release.subprocess, "run", side_effect=download), \
                 patch("sys.stdout", new_callable=io.StringIO) as output, \
                 patch("sys.stderr", new_callable=io.StringIO):
                release.main()
                data = json.loads(output.getvalue())
                self.assertEqual(data["url"], final_url)
                self.assertEqual(data["sha256"], hashlib.sha256(b"deb").hexdigest())


if __name__ == "__main__":
    unittest.main()
