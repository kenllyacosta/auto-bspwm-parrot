import os
from pathlib import Path
import platform
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(platform.system() == 'Linux', 'Requires Bash on Linux')
class PlatformDetection(unittest.TestCase):
    def detect(self, content):
        with tempfile.TemporaryDirectory() as tmp:
            release = Path(tmp) / 'os-release'
            release.write_text(content)
            return subprocess.run(
                ['bash', '-eu', '-c', 'source "$1"; detect_platform "$2"; printf "%s/%s" "$ID" "$VERSION_ID"',
                 'test', str(ROOT / 'scripts/platform.sh'), str(release)],
                env={**os.environ, 'ID': 'parrot', 'VERSION_ID': '7.3'},
                capture_output=True, text=True)

    def test_clean_parrot_71_identifies_as_debian(self):
        result = self.detect('NAME="Parrot Security"\nPRETTY_NAME="Parrot Security 7.1 (echo)"\nID=debian\nVERSION_ID="7.1"\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'parrot/7.1')

    def test_native_parrot_and_kali(self):
        for content, expected in [
            ('ID=parrot\nVERSION_ID=7.3\n', 'parrot/7.3'),
            ('ID=parrot\nVERSION_ID=7\n', 'parrot/7'),
            ('ID=kali\nVERSION_ID=2026.3\n', 'kali/2026.3'),
            ('ID=kali\n', 'kali/'),
        ]:
            with self.subTest(content=content):
                result = self.detect(content)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected)

    def test_other_distributions_and_versions_still_rejected(self):
        for content in [
            'ID=debian\nNAME="Debian GNU/Linux"\nVERSION_ID=7.1\n',
            'ID=ubuntu\nID_LIKE=debian\nVERSION_ID=24.04\n',
            'ID=debian\nNAME="Parrot Security"\nVERSION_ID=6.4\n',
            'ID=parrot\nVERSION_ID=8.0\n',
            'ID=parrot\n',
            'NAME="Parrot Security"\nVERSION_ID=7.1\n',
        ]:
            with self.subTest(content=content):
                result = self.detect(content)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('ERROR:', result.stderr)
                self.assertIn('ID=', result.stderr)


if __name__ == '__main__':
    unittest.main()
