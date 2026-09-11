#!/bin/sh
target="$HOME/.config/bin/target"
if [ -s "$target" ]; then
    # Remove Polybar formatting/action delimiters from user-supplied content.
    printf 'TARGET %s\n' "$(head -n 1 "$target" | tr -d '%{}')"
else
    printf 'No target\n'
fi