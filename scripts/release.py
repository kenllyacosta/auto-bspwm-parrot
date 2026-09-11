#!/usr/bin/env python3
"""Download one unambiguous asset from the latest stable GitHub release."""
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request


def select_asset(release, pattern):
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("Se requiere una publicación estable")
    matches = [a for a in release["assets"] if fnmatch.fnmatchcase(a["name"], pattern)]
    if len(matches) != 1:
        raise ValueError(f"Se esperaba un archivo para {pattern}; encontrados: {[a['name'] for a in matches]}")
    return matches[0]


def main():
    repo, pattern, destination = sys.argv[1:]
    key = "vscode" if repo == "--vscode" else f"{repo}:{pattern}"
    lock_path = os.environ.get("BSPWM_LOCK_FILE")
    if lock_path:
        lock = json.loads(Path(lock_path).read_text())
        item = lock["artifacts"][key]
        download(item["url"], destination, "sha256:" + item["sha256"], item)
        return
    if repo == "--vscode":
        if not pattern.startswith("https://update.code.visualstudio.com/latest/linux-deb-"):
            raise ValueError("URL de VS Code inesperada")
        download(pattern, destination, None, {"key": key})
        return
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "auto-bspwm"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    request = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/latest", headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        release = json.load(response)
    asset = select_asset(release, pattern)
    url = asset["browser_download_url"]
    if not url.startswith(f"https://github.com/{repo}/releases/download/"):
        raise ValueError("URL de descarga inesperada")
    download(url, destination, asset.get("digest"),
             {"key": key, "repository": repo, "version": release["tag_name"], "asset": asset["name"]})


def download(url, destination, expected, metadata):
    result = subprocess.run(["curl", "--fail", "--location", "--retry", "3", "--connect-timeout", "20",
                    "--max-time", "600", "--proto", "=https", "--proto-redir", "=https",
                    "--write-out", "%{url_effective}", url, "-o", destination],
                    check=True, capture_output=True, text=True)
    sha = hashlib.sha256()
    with open(destination, "rb") as downloaded:
        for chunk in iter(lambda: downloaded.read(1024 * 1024), b""):
            sha.update(chunk)
    if expected and expected != "sha256:" + sha.hexdigest():
        Path(destination).unlink()
        raise ValueError("La suma SHA-256 no coincide")
    if not expected:
        print(f"Aviso: {metadata['key']} sin digest upstream; descarga protegida por HTTPS.", file=sys.stderr)
    # GitHub redirect URLs expire; preserve its versioned release URL.
    # Microsoft's stable channel redirects to a CDN URL containing the exact build.
    pinned_url = result.stdout.strip() if metadata["key"] == "vscode" else url
    if not pinned_url.startswith("https://"):
        raise ValueError("URL final inesperada")
    print(json.dumps({**metadata, "url": pinned_url,
                      "sha256": sha.hexdigest(), "verified_digest": bool(expected)}))


if __name__ == "__main__":
    main()
