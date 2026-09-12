#!/usr/bin/env python3
"""Preserve a local static desktop wallpaper as a feh startup file."""
import configparser
import os
from pathlib import Path
import shlex
import shutil
import subprocess
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


def local_image(value):
    value = value.strip().strip("'\"")
    parsed = urlsplit(value)
    if parsed.scheme == 'file':
        if parsed.netloc not in ('', 'localhost'):
            return None
        path = Path(unquote(parsed.path))
    elif parsed.scheme:
        return None
    else:
        path = Path(value).expanduser()
    if not path.is_absolute():
        return None
    if path.is_dir():
        # KDE may store a wallpaper package rather than an image file.
        images = sorted((path / 'contents/images').glob('*'))
        path = next((p for p in images if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')), path)
    return path if path.is_file() else None


def kde_images(home):
    config = configparser.ConfigParser(interpolation=None, strict=False)
    config.read(home / '.config/plasma-org.kde.plasma.desktop-appletsrc', encoding='utf-8')
    for section in config.sections():
        if '[Wallpaper][org.kde.image][General' in section:
            value = config.get(section, 'Image', fallback='')
            if value:
                yield value


def xfce_images(home):
    file = home / '.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml'
    if file.is_file():
        for prop in ET.parse(file).iter('property'):
            if prop.get('name') in ('last-image', 'image-path') and prop.get('value'):
                yield prop.get('value')


def settings_images(desktop):
    schemas = []
    if 'mate' in desktop:
        schemas = [('org.mate.background', 'picture-filename')]
    elif 'cinnamon' in desktop:
        schemas = [('org.cinnamon.desktop.background', 'picture-uri')]
    elif 'gnome' in desktop:
        dark = False
        if shutil.which('gsettings'):
            try:
                preference = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                                            text=True, capture_output=True, timeout=5)
                dark = preference.returncode == 0 and 'prefer-dark' in preference.stdout
            except (OSError, subprocess.TimeoutExpired):
                pass
        keys = ['picture-uri-dark', 'picture-uri'] if dark else ['picture-uri']
        schemas = [('org.gnome.desktop.background', key) for key in keys]
    if shutil.which('gsettings'):
        for schema, key in schemas:
            try:
                result = subprocess.run(['gsettings', 'get', schema, key], text=True,
                                        capture_output=True, timeout=5)
                if result.returncode == 0:
                    yield result.stdout.strip()
            except (OSError, subprocess.TimeoutExpired):
                pass


def preserve(home, desktop):
    target = home / '.fehbg'
    desktop = desktop.lower()
    # An existing bspwm/feh choice is already the authoritative background.
    if target.is_file() and (not desktop or 'bspwm' in desktop):
        return 'Se conserva ~/.fehbg existente.'
    readers = [kde_images, xfce_images]
    if 'xfce' in desktop:
        readers.reverse()
    values = list(settings_images(desktop))
    for reader in readers:
        try:
            values.extend(reader(home))
        except (OSError, configparser.Error, ET.ParseError, UnicodeError):
            pass
    for value in values:
        path = local_image(value)
        if path is not None:
            # Quoting is essential: a wallpaper path is data, never shell code.
            target.write_text('#!/bin/sh\nfeh --no-fehbg --bg-fill -- ' + shlex.quote(str(path)) + '\n', encoding='utf-8')
            target.chmod(0o700)
            return 'Fondo conservado desde la configuración del escritorio: ' + str(path)
    return 'No se detectó una imagen local; se conserva ~/.fehbg si existe. No se modifica el escritorio original.'


if __name__ == '__main__':
    print(preserve(Path.home(), os.environ.get('XDG_CURRENT_DESKTOP', '')))
