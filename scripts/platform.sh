#!/usr/bin/env bash
# Shared distribution detection. Keep Debian-derived systems opt-in by identity.
detect_platform() {
    local release_file=${1:-/etc/os-release}
    if [[ ! -r $release_file && $release_file == /etc/os-release ]]; then
        release_file=/usr/lib/os-release
    fi
    [[ -r $release_file ]] || { printf 'ERROR: No se puede leer %s\n' "$release_file" >&2; return 1; }
    ID= NAME= PRETTY_NAME= VERSION_ID=
    # shellcheck disable=SC1090
    source "$release_file"
    OS_RELEASE_ID=$ID
    # Some clean Parrot 7 images identify their Debian base in ID.
    # ID_LIKE=debian alone must never qualify another Debian derivative.
    if [[ $ID == debian && ( $NAME == 'Parrot Security' || $NAME == 'Parrot Home' ) ]]; then
        ID=parrot
    fi
    case "$ID" in
        parrot)
            if [[ ! $VERSION_ID =~ ^7([.][0-9]+)*$ ]]; then
                printf 'ERROR: Se requiere Parrot 7.x; detectado NAME=%s, ID=%s, VERSION_ID=%s\n' "$NAME" "$OS_RELEASE_ID" "${VERSION_ID:-ausente}" >&2
                return 1
            fi ;;
        kali) ;;
        *)
            printf 'ERROR: Distribución compatible: Parrot 7.x o Kali Linux. Detectado NAME=%s, ID=%s, VERSION_ID=%s (%s)\n' "$NAME" "${ID:-ausente}" "${VERSION_ID:-ausente}" "$release_file" >&2
            return 1 ;;
    esac
    PRETTY_NAME=${PRETTY_NAME:-${NAME:-$ID}}
}
