#!/bin/sh
iface=${BSPWM_VPN_INTERFACE:-$(ip -o link show | awk -F': ' '$2 ~ /^(tun|tap|wg)[0-9]+/ {sub(/@.*/, "", $2); print $2; exit}')}
address=
[ -z "$iface" ] || address=$(ip -o -4 addr show dev "$iface" 2>/dev/null | awk 'NR==1 {split($4,a,"/"); print a[1]}')
printf 'VPN %s\n' "${address:-Disconnected}"