#!/usr/bin/env python3
"""Heuristic OS hint from ping TTL, never a reliable OS fingerprint."""
import ipaddress
import os
import re
import subprocess
import sys


def get_ttl(address):
    address = str(ipaddress.ip_address(address))
    result = subprocess.run(["ping", "-n", "-c", "1", "-W", "2", address],
                            capture_output=True, text=True, timeout=5,
                            env={**os.environ, "LC_ALL": "C"})
    match = re.search(r"\b(?:ttl|hlim)=(\d+)\b", result.stdout, re.I)
    if result.returncode or not match:
        raise ValueError("Sin respuesta ICMP con TTL")
    return int(match.group(1))


def get_os(ttl):
    if 0 < ttl <= 64:
        return "Linux/Unix probable"
    if ttl <= 128 and ttl > 64:
        return "Windows probable"
    return "Desconocido"


def main():
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <IP>", file=sys.stderr)
        return 2
    try:
        ttl = get_ttl(sys.argv[1])
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(f"{sys.argv[1]} (TTL {ttl}): {get_os(ttl)}; estimación, no identificación.")
    return 0


if __name__ == "__main__":
    sys.exit(main())