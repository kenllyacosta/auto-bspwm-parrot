#!/usr/bin/env bash
# Package operations must work with install.sh's tee log and no interactive UI.
apt_run() {
    sudo env DEBIAN_FRONTEND=noninteractive UCF_FORCE_CONFFOLD=1 NEEDRESTART_MODE=l \
        apt-get -o Dpkg::Use-Pty=0 -o Dpkg::Options::=--force-confold \
        --no-remove "$@"
}
