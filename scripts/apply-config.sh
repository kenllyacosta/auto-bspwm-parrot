#!/usr/bin/env bash
# Repair user configuration independently of package installation.
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
[[ $(uname -s) == Linux && $EUID -ne 0 ]] || { echo 'Ejecuta como usuario normal en Linux.' >&2; exit 1; }
[[ ${XDG_CONFIG_HOME:-$HOME/.config} == "$HOME/.config" ]] || { echo 'Se requiere ~/.config.' >&2; exit 1; }
export PATH="$HOME/.local/bin:$PATH"
for program in bspwm sxhkd rofi; do
    command -v "$program" >/dev/null || { printf 'Falta %s; ejecuta install.sh primero.\n' "$program" >&2; exit 1; }
done
mkdir -p "$HOME/.local/state/auto-bspwm/backups"
BACKUP=${BSPWM_CONFIG_BACKUP:-$(mktemp -d "$HOME/.local/state/auto-bspwm/backups/config-XXXXXX")}
mkdir -p "$BACKUP"
backup() {
    if [[ -e "$HOME/$1" || -L "$HOME/$1" ]]; then
        mkdir -p "$BACKUP/$(dirname "$1")"
        cp -a -- "$HOME/$1" "$BACKUP/$1"
    fi
}
mkdir -p "$HOME/.config" "$HOME/.local/bin"
backup .fehbg
python3 "$ROOT/scripts/preserve-wallpaper.py"
for config in bspwm sxhkd polybar picom kitty; do
    backup ".config/$config"
    rm -rf -- "$HOME/.config/$config"
    cp -a "$ROOT/Config/$config" "$HOME/.config/$config"
done
backup .config/bin
mkdir -p "$HOME/.config/bin"
cp "$ROOT"/Config/bin/*.sh "$HOME/.config/bin/"
backup .config/rofi
mkdir -p "$HOME/.config/rofi/themes"
cp "$ROOT/rofi/nord.rasi" "$HOME/.config/rofi/themes/"
printf '@theme "themes/nord.rasi"\n' > "$HOME/.config/rofi/config.rasi"
for config in .zshrc .p10k.zsh; do backup "$config"; cp "$ROOT/$config" "$HOME/$config"; done
for script in screenshot whichSystem.py; do
    backup ".local/bin/$script"
    install -m 755 "$ROOT/scripts/$script" "$HOME/.local/bin/$script"
done
if ! command -v bat >/dev/null && command -v batcat >/dev/null; then
    backup .local/bin/bat
    ln -sfn /usr/bin/batcat "$HOME/.local/bin/bat"
fi
chmod +x "$HOME/.config/bspwm/bspwmrc" "$HOME/.config/bspwm/scripts/"* \
    "$HOME/.config/bin/"*.sh "$HOME/.config/polybar/launch.sh" \
    "$HOME/.config/polybar/scripts/"{launcher,powermenu,powermenu_alt}
printf 'Configuración aplicada. Respaldo: %s\n' "$BACKUP"
