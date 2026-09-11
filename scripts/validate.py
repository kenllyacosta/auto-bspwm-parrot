#!/usr/bin/env python3
"""Run inside the installed bspwm session; save evidence without certifying manual checks."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path, help="Directorio runs/<fecha> mostrado por el instalador")
    args = parser.parse_args()
    run = args.run.resolve()
    if not (run / "complete").is_file():
        parser.error("No es una instalación completa")
    checks = []

    def check(name, success, detail=""):
        checks.append({"name": name, "passed": bool(success), "detail": detail})

    def command(name, argv):
        try:
            result = subprocess.run(argv, text=True, capture_output=True, timeout=30)
            check(name, result.returncode == 0, (result.stdout + result.stderr)[-4000:])
        except (OSError, subprocess.TimeoutExpired) as error:
            check(name, False, str(error))

    check("Linux", platform.system() == "Linux")
    check("Sesión X11", os.environ.get("XDG_SESSION_TYPE") == "x11")
    check("DISPLAY", bool(os.environ.get("DISPLAY")))
    command("bspwm activo", ["bspc", "query", "-M", "--names"])
    command("Polybar activa", ["pgrep", "-u", str(os.getuid()), "-x", "polybar"])
    command("sxhkd activo", ["pgrep", "-u", str(os.getuid()), "-x", "sxhkd"])
    command("Picom activo", ["pgrep", "-u", str(os.getuid()), "-x", "picom"])
    for app in ("kitty", "nvim", "bat", "lsd", "rofi", "zsh"):
        command(f"{app} ejecutable", [app, "--version"])
    command("pwntools aislado", ["pipx", "runpip", "pwntools", "check"])
    before = (run / "sessions-before.txt").read_text().splitlines()
    check("Escritorio original conservado", bool(before) and all(Path(p).is_file() for p in before),
          "\n".join(before))
    check("Sesión bspwm disponible", Path("/usr/share/xsessions/bspwm.desktop").is_file())
    original_dm = (run / "display-manager.txt").read_text().strip()
    current_dm = Path("/etc/systemd/system/display-manager.service")
    check("Gestor de acceso conservado", bool(original_dm) and str(current_dm.resolve()) == original_dm)
    check("Plugins NvChad inicializados", (Path.home() / ".config/nvim/lazy-lock.json").is_file())
    if shutil.which("scrot") and os.environ.get("XDG_SESSION_TYPE") == "x11":
        command("Captura de sesión", ["scrot", str(run / "desktop.png")])
    report = {"created_at": datetime.now(timezone.utc).isoformat(), "checks": checks,
              "automatic_pass": all(c["passed"] for c in checks),
              "manual_pending": ["Abrir Kitty y Rofi con atajos", "Audio y conectividad",
                                 "Bloquear y desbloquear", "Cerrar sesión y entrar al escritorio original",
                                 "Reiniciar y volver a bspwm", "Escalado e iconos en todos los monitores"]}
    (run / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
    for item in checks:
        print(f"{'OK' if item['passed'] else 'FAIL'}: {item['name']}")
    print(f"Informe: {run / 'validation.json'}; las pruebas manuales siguen pendientes.")
    return 0 if report["automatic_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
