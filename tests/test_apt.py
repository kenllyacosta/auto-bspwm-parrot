from pathlib import Path
import os
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASH = shutil.which('bash')
if os.name == 'nt' and Path('C:/Program Files/Git/bin/bash.exe').is_file():
    BASH = 'C:/Program Files/Git/bin/bash.exe'


@unittest.skipUnless(BASH, 'Requires Bash')
class AptInvocation(unittest.TestCase):
    def test_noninteractive_logging_and_quoted_package_path(self):
        result = subprocess.run([BASH, '-eu', '-c',
            'source scripts/apt.sh; sudo() { printf "%s\\n" "$@"; }; apt_run install -y "/tmp/package with spaces.deb"',
        ], cwd=ROOT, capture_output=True, text=True, check=True)
        args = result.stdout.splitlines()
        for required in ('DEBIAN_FRONTEND=noninteractive', 'UCF_FORCE_CONFFOLD=1',
                         'NEEDRESTART_MODE=l', 'Dpkg::Use-Pty=0',
                         'Dpkg::Options::=--force-confold', '--no-remove'):
            self.assertIn(required, args)
        self.assertEqual(args[-3:], ['install', '-y', '/tmp/package with spaces.deb'])

    def test_apt_failure_is_not_hidden(self):
        result = subprocess.run([BASH, '-c',
            'source scripts/apt.sh; sudo() { return 17; }; apt_run install -y example',
        ], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 17)
