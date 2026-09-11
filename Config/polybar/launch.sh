#!/bin/sh
uid=$(id -u)
pkill -u "$uid" -x polybar 2>/dev/null || true
attempt=0
while pgrep -u "$uid" -x polybar >/dev/null; do
    attempt=$((attempt + 1))
    [ "$attempt" -lt 30 ] || { printf 'Polybar no terminó.\n' >&2; exit 1; }
    sleep 0.1
done
export BSPWM_BATTERY_MODULE=
export BSPWM_BATTERY=
export BSPWM_ADAPTER=
for supply in /sys/class/power_supply/*; do
    [ -f "$supply/type" ] || continue
    case "$(cat "$supply/type")" in
        Battery) BSPWM_BATTERY=$(basename "$supply"); BSPWM_BATTERY_MODULE=battery ;;
        Mains) BSPWM_ADAPTER=$(basename "$supply") ;;
    esac
done
if [ "${BSPWM_BAR_LAYOUT:-responsive}" != classic ]; then
    polybar --list-monitors | while IFS=: read -r monitor geometry; do
        export MONITOR="$monitor"
        width=${geometry%%x*}
        width=$(printf '%s' "$width" | tr -d ' ')
        case "$width" in *[!0-9]*|'') width=1920 ;; esac
        export BSPWM_STATUS_MODULES="pulseaudio ${BSPWM_BATTERY_MODULE} date powermenu"
        if [ "$width" -ge 1500 ]; then
            BSPWM_STATUS_MODULES="ethernet_status htb_status htb_target $BSPWM_STATUS_MODULES"
        elif [ "$width" -ge 1100 ]; then
            BSPWM_STATUS_MODULES="ethernet_status $BSPWM_STATUS_MODULES"
        fi
        polybar main -c "$HOME/.config/polybar/responsive.ini" &
    done
    exit 0
fi
for bar in log secondary terciary quaternary quinary top primary; do
    polybar "$bar" -c "$HOME/.config/polybar/current.ini" &
done
polybar primary -c "$HOME/.config/polybar/workspace.ini" &
