import importlib.util
from pathlib import Path
import shlex
import platform
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('wallpaper', ROOT / 'scripts/preserve-wallpaper.py')
wallpaper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wallpaper)


@unittest.skipUnless(platform.system() == 'Linux', 'Uses Linux wallpaper paths')
class PreserveWallpaper(unittest.TestCase):
    def test_kde_package_and_quoted_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            image = home / "Pictures" / "my wallpaper ' $(echo test).jpg"
            image.parent.mkdir()
            image.write_bytes(b'image fixture')
            (home / '.config').mkdir()
            (home / '.config/plasma-org.kde.plasma.desktop-appletsrc').write_text(
                '[Containments][1][Wallpaper][org.kde.image][General]\nImage=' + image.as_uri() + '\n')
            (home / '.fehbg').write_text('old background')
            wallpaper.preserve(home, 'KDE')
            command = (home / '.fehbg').read_text().splitlines()[1]
            self.assertEqual(shlex.split(command), ['feh', '--no-fehbg', '--bg-fill', '--', str(image)])
            package = home / 'wallpaper-package'
            (package / 'contents/images').mkdir(parents=True)
            (package / 'contents/images/1920x1080.png').write_bytes(b'image fixture')
            self.assertEqual(wallpaper.local_image(str(package)), package / 'contents/images/1920x1080.png')

    def test_existing_bspwm_background_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / '.fehbg').write_text('personal settings')
            wallpaper.preserve(home, 'bspwm')
            self.assertEqual((home / '.fehbg').read_text(), 'personal settings')

    def test_missing_or_remote_image_does_not_replace_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / '.fehbg').write_text('personal settings')
            wallpaper.preserve(home, 'KDE')
            self.assertEqual((home / '.fehbg').read_text(), 'personal settings')
            self.assertIsNone(wallpaper.local_image('https://example.invalid/image.jpg'))
            self.assertIsNone(wallpaper.local_image('file://remotehost/image.jpg'))

    def test_xfce_current_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            image = home / 'desktop.png'
            image.write_bytes(b'image fixture')
            config = home / '.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml'
            config.parent.mkdir(parents=True)
            import xml.etree.ElementTree as ET
            channel = ET.Element('channel')
            ET.SubElement(channel, 'property', name='last-image', value=str(image))
            ET.ElementTree(channel).write(config)
            wallpaper.preserve(home, 'XFCE')
            self.assertIn(shlex.quote(str(image)), (home / '.fehbg').read_text())


if __name__ == '__main__':
    unittest.main()
