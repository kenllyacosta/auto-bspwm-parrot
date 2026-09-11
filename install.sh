#!/usr/bin/env bash
set -Eeuo pipefail
umask 022
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
MODE=latest
UPGRADE=false
CHANGE_SHELL=false
LOCK_FILE=
while (( $# )); do
    arg=$1
    case "$arg" in
        --locked) (( $# >= 2 )) || { printf 'Falta el archivo de versiones\n' >&2; exit 2; }; LOCK_FILE=$(realpath -- "$2"); shift ;;
        --repo-only) MODE=repo ;;
        --upgrade-system) UPGRADE=true ;;
        --change-shell) CHANGE_SHELL=true ;;
        --help|-h) printf 'Uso: bash install.sh [--repo-only] [--upgrade-system] [--change-shell] [--locked ARCHIVO]\n'; exit 0 ;;
        *) printf 'Opción desconocida: %s\n' "$arg" >&2; exit 2 ;;
    esac
    shift
done
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
[[ $(uname -s) == Linux ]] || die 'Ejecuta este instalador en Linux.'
(( EUID != 0 )) || die 'Ejecuta como usuario normal con acceso a sudo.'
# shellcheck disable=SC1091
source /etc/os-release
case "$ID" in
    parrot) [[ ${VERSION_ID%%.*} == 7 ]] || die 'Se requiere Parrot 7.x.' ;;
    kali) ;;
    *) die 'Distribución compatible: Parrot 7.x o Kali Linux.' ;;
esac
ARCH=$(dpkg --print-architecture)
case "$ARCH" in
    amd64) NVARCH=x86_64; KITARCH=x86_64; CODEARCH=x64 ;;
    arm64) NVARCH=arm64; KITARCH=arm64; CODEARCH=arm64 ;;
    *) die 'Arquitectura compatible: amd64 o arm64.' ;;
esac
if [[ -n $LOCK_FILE ]]; then
    "$UPGRADE" && die '--locked no permite actualizar el sistema.'
    command -v python3 >/dev/null || die 'El modo fijo requiere Python 3 instalado.'
    python3 "$ROOT/scripts/pins.py" check "$LOCK_FILE" "$ID" "${VERSION_ID:-rolling}" "$ARCH"
    MODE=$(python3 "$ROOT/scripts/pins.py" get "$LOCK_FILE" mode)
    export BSPWM_LOCK_FILE="$LOCK_FILE"
else
    unset BSPWM_LOCK_FILE
fi
[[ ${XDG_CONFIG_HOME:-$HOME/.config} == "$HOME/.config" ]] || die 'Se requiere XDG_CONFIG_HOME=$HOME/.config.'
command -v sudo >/dev/null || die 'Instala sudo y autoriza a tu usuario primero.'
sudo -v
STATE="$HOME/.local/state/auto-bspwm"
mkdir -p "$STATE"
exec 9>"$STATE/install.lock"
flock -n 9 || die 'Ya hay una instalación en curso.'
RUN=$(date +%Y%m%d-%H%M%S)-$$
BACKUP="$STATE/backups/$RUN"
RUN_DIR="$STATE/runs/$RUN"
mkdir -p "$BACKUP" "$RUN_DIR"
LOG="$STATE/install-$RUN.log"
exec > >(tee -a "$LOG") 2>&1
TMP=$(mktemp -d)
trap 'rm -rf -- "$TMP"' EXIT
trap 'exit 130' INT
trap 'printf "Error en línea %s. Registro: %s; respaldo: %s\n" "$LINENO" "$LOG" "$BACKUP" >&2' ERR
backup() {
    local path=$1
    if [[ -e "$HOME/$path" || -L "$HOME/$path" ]]; then
        mkdir -p "$BACKUP/$(dirname "$path")"
        cp -a -- "$HOME/$path" "$BACKUP/$path"
    fi
}
release() {
    python3 "$ROOT/scripts/release.py" "$1" "$2" "$3" | tee -a "$RUN_DIR/artifacts.jsonl"
}
clone_repo() {
    local name=$1 url=$2 destination=$3 commit
    if [[ -n $LOCK_FILE ]]; then
        commit=$(python3 "$ROOT/scripts/pins.py" get "$LOCK_FILE" "$name")
        git init "$destination"
        git -C "$destination" remote add origin "$url"
        git -C "$destination" fetch --depth=1 origin "$commit"
        git -C "$destination" checkout --detach FETCH_HEAD
        [[ $(git -C "$destination" rev-parse HEAD) == "$commit" ]] || die 'Commit diferente al lock'
    else
        git clone --depth=1 "$url" "$destination"
    fi
    git -C "$destination" rev-parse HEAD > "$RUN_DIR/$name.txt"
}
printf 'Instalando en %s (%s), modo %s. Registro: %s\n' "$PRETTY_NAME" "$ARCH" "$MODE" "$LOG"
find /usr/share/xsessions /usr/share/wayland-sessions -maxdepth 1 -name '*.desktop' \
    -print 2>/dev/null > "$RUN_DIR/sessions-before.txt" || true
[[ -s "$RUN_DIR/sessions-before.txt" ]] || die 'Se requiere un escritorio original para recuperación.'
readlink -f /etc/systemd/system/display-manager.service > "$RUN_DIR/display-manager.txt" || true
sudo apt-get update
if "$UPGRADE"; then
    sudo apt-get --no-remove full-upgrade -y
fi
PACKAGES=(bspwm sxhkd polybar picom xserver-xorg xinit dbus-x11 \
    x11-xserver-utils x11-utils xauth curl ca-certificates git python3 python3-venv \
    python3-pip pipx build-essential pkg-config libssl-dev libffi-dev \
    unzip xz-utils fontconfig fonts-dejavu-core feh scrot zsh rofi xclip \
    plocate fastfetch wmname acpi fzf ripgrep numlockx iproute2 iputils-ping scrub \
    libnotify-bin dunst i3lock xss-lock network-manager-gnome lxpolkit \
    zsh-syntax-highlighting zsh-autosuggestions ranger file firefox-esr pavucontrol kitty-terminfo \
    libgl1 libegl1 libxkbcommon-x11-0 libfontconfig1)
if [[ -n $LOCK_FILE ]]; then
    python3 "$ROOT/scripts/pins.py" get "$LOCK_FILE" apt > "$TMP/apt.txt"
    mapfile -t PACKAGES < "$TMP/apt.txt"
fi
# Abort dependency resolution instead of removing the original desktop or login manager.
sudo apt-get --no-remove install -y "${PACKAGES[@]}"
python3 -c 'import json,sys; print(json.dumps(dict(zip(("id","version","arch","mode"), sys.argv[1:]))))' \
    "$ID" "${VERSION_ID:-rolling}" "$ARCH" "$MODE" > "$RUN_DIR/platform.json"
python3 "$ROOT/scripts/pins.py" fingerprint > "$RUN_DIR/source.sha256"
mkdir -p "$HOME/.local/bin" "$HOME/.local/opt" "$HOME/.local/share/fonts/auto-bspwm"
export PATH="$HOME/.local/bin:$PATH"
if [[ $MODE == latest ]]; then
    release neovim/neovim "nvim-linux-$NVARCH.tar.gz" "$TMP/nvim.tar.gz"
    tar -xzf "$TMP/nvim.tar.gz" -C "$TMP"
    backup .local/opt/nvim
    rm -rf -- "$HOME/.local/opt/nvim"
    mv "$TMP/nvim-linux-$NVARCH" "$HOME/.local/opt/nvim"
    release kovidgoyal/kitty "kitty-*-$KITARCH.txz" "$TMP/kitty.txz"
    mkdir "$TMP/kitty"
    tar -xJf "$TMP/kitty.txz" -C "$TMP/kitty"
    backup .local/opt/kitty
    rm -rf -- "$HOME/.local/opt/kitty"
    mv "$TMP/kitty" "$HOME/.local/opt/kitty"
    for app in nvim kitty; do
        backup ".local/bin/$app"
        ln -sfn "$HOME/.local/opt/$app/bin/$app" "$HOME/.local/bin/$app"
    done
    backup .local/bin/kitten
    ln -sfn "$HOME/.local/opt/kitty/bin/kitten" "$HOME/.local/bin/kitten"
    backup .local/share/applications/kitty.desktop
    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/kitty.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Kitty
Exec="$HOME/.local/bin/kitty"
Icon=$HOME/.local/opt/kitty/share/icons/hicolor/256x256/apps/kitty.png
Terminal=false
Categories=System;TerminalEmulator;
EOF
    release sharkdp/bat "bat_*_${ARCH}.deb" "$TMP/bat.deb"
    release lsd-rs/lsd "lsd_*_${ARCH}.deb" "$TMP/lsd.deb"
    release --vscode "https://update.code.visualstudio.com/latest/linux-deb-$CODEARCH/stable" "$TMP/code.deb"
    chmod 755 "$TMP"
    printf 'code code/add-microsoft-repo boolean false\n' | sudo debconf-set-selections
    sudo env DEBIAN_FRONTEND=noninteractive apt-get --no-remove install -y "$TMP/bat.deb" "$TMP/lsd.deb" "$TMP/code.deb"
else
    if [[ -z $LOCK_FILE ]]; then sudo apt-get --no-remove install -y neovim kitty bat lsd; fi
    for app in nvim kitty kitten; do
        if [[ -L "$HOME/.local/bin/$app" && $(readlink "$HOME/.local/bin/$app") == "$HOME/.local/opt/"* ]]; then
            backup ".local/bin/$app"
            rm -- "$HOME/.local/bin/$app"
        fi
    done
    if [[ -f "$HOME/.local/share/applications/kitty.desktop" ]] &&
        grep -Fq "$HOME/.local/bin/kitty" "$HOME/.local/share/applications/kitty.desktop"; then
        backup .local/share/applications/kitty.desktop
        rm -- "$HOME/.local/share/applications/kitty.desktop"
    fi
fi
for family in Hack Iosevka Hurmit; do
    release ryanoasis/nerd-fonts "$family.zip" "$TMP/$family.zip"
    mkdir "$TMP/$family"
    unzip -q "$TMP/$family.zip" -d "$TMP/$family"
    backup ".local/share/fonts/auto-bspwm/$family"
    mkdir -p "$HOME/.local/share/fonts/auto-bspwm/$family"
    find "$TMP/$family" -type f \( -name '*.ttf' -o -name '*.otf' -o -iname '*license*' -o -iname '*ofl*' \) \
        -exec cp -t "$HOME/.local/share/fonts/auto-bspwm/$family" -- {} +
done
fc-cache -f
clone_repo p10k https://github.com/romkatv/powerlevel10k.git "$TMP/p10k"
backup .powerlevel10k
rm -rf -- "$HOME/.powerlevel10k"
mv "$TMP/p10k" "$HOME/.powerlevel10k"
clone_repo nvchad https://github.com/NvChad/starter.git "$TMP/nvim-config"
backup .config/nvim
mkdir -p "$HOME/.config"
rm -rf -- "$HOME/.config/nvim"
mv "$TMP/nvim-config" "$HOME/.config/nvim"
if [[ -n $LOCK_FILE ]]; then
    python3 "$ROOT/scripts/pins.py" get "$LOCK_FILE" lazy_lock > "$HOME/.config/nvim/lazy-lock.json"
    clone_repo lazy https://github.com/folke/lazy.nvim.git "$TMP/lazy.nvim"
    lazy_dir="${XDG_DATA_HOME:-$HOME/.local/share}/nvim/lazy/lazy.nvim"
    [[ $lazy_dir == "$HOME/"* ]] || die 'XDG_DATA_HOME debe estar dentro de HOME.'
    backup "${lazy_dir#"$HOME/"}"
    rm -rf -- "$lazy_dir"
    mkdir -p "$(dirname "$lazy_dir")"
    mv "$TMP/lazy.nvim" "$lazy_dir"
fi
BSPWM_CONFIG_BACKUP="$BACKUP" bash "$ROOT/scripts/apply-config.sh"
if [[ -n $LOCK_FILE ]]; then
    python3 "$ROOT/scripts/pins.py" get "$LOCK_FILE" python > "$TMP/constraints.txt"
    PIP_CONSTRAINT="$TMP/constraints.txt" pipx install --force pwntools
    nvim --headless '+Lazy! restore' +qa
else
    pipx install --force pwntools
fi
[[ -f /usr/share/xsessions/bspwm.desktop ]] || die 'No se encontró la sesión X11 de bspwm.'
if "$CHANGE_SHELL"; then sudo chsh -s /usr/bin/zsh "$USER"; fi
dpkg-query -W bspwm sxhkd polybar picom neovim kitty bat lsd code 2>/dev/null \
    > "$STATE/packages-$RUN.txt" || true
dpkg-query -W -f='${binary:Package}=${Version} ${db:Status-Status}\n' |
    awk '$2 == "installed" { print $1 }' > "$RUN_DIR/apt-all.txt"
if [[ $MODE == latest ]]; then
    grep -Ev '^(bat|lsd|code)(:[^=]+)?=' "$RUN_DIR/apt-all.txt" > "$RUN_DIR/apt.txt"
else
    cp "$RUN_DIR/apt-all.txt" "$RUN_DIR/apt.txt"
fi
pipx runpip pwntools freeze > "$RUN_DIR/python.txt"
touch "$RUN_DIR/complete"
printf '\nInstalación completada. Cierra sesión y elige bspwm (X11).\nRespaldo: %s\nNvChad descargará sus plugins al abrir nvim.\n' "$BACKUP"
printf 'Tras verificar el escritorio y abrir nvim, congela las versiones:\npython3 "%s/scripts/pins.py" freeze "%s" parrot-kali.lock.json\n' "$ROOT" "$RUN_DIR"
