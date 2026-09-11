#!/bin/sh
iface=${BSPWM_NETWORK_INTERFACE:-$(ip -4 route show default | awk 'NR==1 {for(i=1;i<=NF;i++) if($i=="dev") {print $(i+1); exit}}')}
address=
[ -z "$iface" ] || address=$(ip -o -4 addr show dev "$iface" 2>/dev/null | awk 'NR==1 {split($4,a,"/"); print a[1]}')
printf 'NET %s\n' "${address:-Disconnected}"