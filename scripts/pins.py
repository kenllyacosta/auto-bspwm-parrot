#!/usr/bin/env python3
"""Capture/replay installation pins. Never treats a lock as proof of VM validation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPOS = {"p10k": "https://github.com/romkatv/powerlevel10k.git",
         "nvchad": "https://github.com/NvChad/starter.git"}


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def source_hash():
    digest = hashlib.sha256()
    paths = [ROOT / "install.sh", ROOT / ".zshrc", ROOT / ".p10k.zsh"]
    for folder in ("scripts", "Config", "rofi"):
        paths += [p for p in (ROOT / folder).rglob("*") if p.is_file()
                  and "__pycache__" not in p.parts and p.suffix != ".pyc"]
    for path in sorted(paths):
        digest.update(path.relative_to(ROOT).as_posix().encode() + b"\0")
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()


def load(path):
    data = json.loads(Path(path).read_text())
    if data.get("schema") != 1:
        raise ValueError("Formato de lock no compatible")
    if data["platform"]["mode"] not in ("latest", "repo"):
        raise ValueError("Modo de instalación inválido")
    if not data["apt"] or not data["artifacts"] or not data["lazy_lock"]:
        raise ValueError("El lock está incompleto")
    if not {"p10k", "nvchad", "lazy"}.issubset(data["git"]):
        raise ValueError("Faltan commits del entorno")
    for plugin in data["lazy_lock"].values():
        if not re.fullmatch(r"[a-f0-9]{40}", plugin["commit"]):
            raise ValueError("Plugin sin commit exacto")
    for item in data["artifacts"].values():
        if not re.fullmatch(r"[a-f0-9]{64}", item["sha256"]):
            raise ValueError("SHA-256 inválido")
        if not item["url"].startswith("https://"):
            raise ValueError("El lock requiere HTTPS")
    for commit in data["git"].values():
        if not re.fullmatch(r"[a-f0-9]{40}", commit):
            raise ValueError("Se requiere un commit Git completo")
    for package in data["apt"]:
        if not re.fullmatch(r"[a-z0-9][a-z0-9+.:\-]*=[a-zA-Z0-9.+:~\-]+", package):
            raise ValueError("Paquete APT inválido")
    for spec in data["python"]:
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+==[a-zA-Z0-9_.+!\-]+", spec):
            raise ValueError("Dependencia Python sin versión exacta")
    if not any(x.lower().startswith("pwntools==") for x in data["python"]):
        raise ValueError("Falta pwntools")
    return data


def capture(run_dir, output):
    run_dir = Path(run_dir)
    platform = json.loads((run_dir / "platform.json").read_text())
    if not (run_dir / "complete").is_file():
        raise ValueError("La instalación no terminó; no se puede congelar")
    if (run_dir / "source.sha256").read_text().strip() != source_hash():
        raise ValueError("El código cambió desde la instalación; vuelve a validar e instalar")
    artifacts = {}
    for line in (run_dir / "artifacts.jsonl").read_text().splitlines():
        item = json.loads(line)
        artifacts[item["key"]] = item
    git = {key: (run_dir / f"{key}.txt").read_text().strip() for key in REPOS}
    apt = (run_dir / "apt.txt").read_text().splitlines()
    python = (run_dir / "python.txt").read_text().splitlines()
    lazy = Path.home() / ".config/nvim/lazy-lock.json"
    if not lazy.is_file():
        raise ValueError("Abre nvim, termina la instalación de plugins y vuelve a congelar")
    lazy_data = json.loads(lazy.read_text())
    if not lazy_data:
        raise ValueError("lazy-lock.json está vacío")
    # Pin the package manager too; starter normally bootstraps its moving stable branch.
    lazy_dir = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "nvim/lazy/lazy.nvim"
    git["lazy"] = run("git", "-C", str(lazy_dir), "rev-parse", "HEAD")
    data = {"schema": 1, "platform": platform, "source_sha256": source_hash(),
            "artifacts": artifacts, "git": git, "apt": apt, "python": python,
            "lazy_lock": lazy_data, "validation": "not-certified"}
    destination = Path(output)
    # Refuse accidental replacement of a previously validated set.
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write("\n")
    try:
        load(destination)
    except Exception:
        destination.unlink()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fingerprint")
    freeze = sub.add_parser("freeze")
    freeze.add_argument("run")
    freeze.add_argument("output")
    check = sub.add_parser("check")
    check.add_argument("lock")
    check.add_argument("distro")
    check.add_argument("version")
    check.add_argument("arch")
    get = sub.add_parser("get")
    get.add_argument("lock")
    get.add_argument("field", choices=["apt", "python", "mode", "p10k", "nvchad", "lazy", "lazy_lock"])
    args = parser.parse_args()
    if args.command == "fingerprint":
        print(source_hash())
        return
    if args.command == "freeze":
        capture(args.run, args.output)
        return
    data = load(args.lock)
    if args.command == "check":
        for key, expected in (("id", args.distro), ("version", args.version), ("arch", args.arch)):
            if data["platform"][key] != expected:
                raise ValueError(f"El lock no corresponde a {key}={expected}")
        if data["source_sha256"] != source_hash():
            raise ValueError("El proyecto cambió: usa el mismo código con el que se creó el lock")
        return
    if args.field in ("apt", "python"):
        print("\n".join(data[args.field]))
    elif args.field == "mode":
        print(data["platform"]["mode"])
    elif args.field == "lazy_lock":
        print(json.dumps(data["lazy_lock"]))
    else:
        print(data["git"][args.field])


if __name__ == "__main__":
    main()
