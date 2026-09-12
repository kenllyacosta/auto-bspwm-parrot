#!/usr/bin/env bash
# Called after curl, GnuPG and CA certificates are installed.
configure_cloudflare_one() {
    local backup_dir=$1 temp_dir=$2 arch=$3
    local key=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
    local source=/etc/apt/sources.list.d/cloudflare-client.list
    curl --fail --location --proto '=https' --tlsv1.2 --retry 3 \
        https://pkg.cloudflareclient.com/pubkey.gpg -o "$temp_dir/cloudflare.pub"
    gpg --batch --yes --dearmor --output "$temp_dir/cloudflare.gpg" "$temp_dir/cloudflare.pub"
    # Use Cloudflare's Debian 13 suite, never the derivative's echo/kali-rolling codename.
    printf 'deb [arch=%s signed-by=%s] https://pkg.cloudflareclient.com/ trixie main\n' \
        "$arch" "$key" > "$temp_dir/cloudflare.list"
    mkdir -p "$backup_dir"
    if [[ -e $key ]]; then sudo cp -a "$key" "$backup_dir/cloudflare-warp-archive-keyring.gpg"; fi
    if [[ -e $source ]]; then sudo cp -a "$source" "$backup_dir/cloudflare-client.list"; fi
    sudo install -m 644 "$temp_dir/cloudflare.gpg" "$key"
    sudo install -m 644 "$temp_dir/cloudflare.list" "$source"
}
