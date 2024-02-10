rm -rf build dist

pyinstaller --name 'MyAmpSwitcher' \
            --icon 'icon.icns' \
            --noconsole  \
            --windowed  \
            --add-data './settings.json:.' \
            --add-data './icon.icns:.' \
            --add-data './profiles/*:profiles' \
            --add-data='./.venv/lib/python3.11/site-packages/PyQt5/Qt5/plugins/platforms:./PyQt5/Qt/plugins/platforms'\
            --additional-hooks-dir='./' \
            --hidden-import mido.backends.rtmidi \
            --hidden-import pyqt5 \
            MyAmpSwitcher.py



mkdir -p dist/dmg
cp -r "dist/MyAmpSwitcher.app" dist/dmg

create-dmg \
  --volname "MyAmpSwitcher" \
  --volicon "icon.ico" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "MyAmpSwitcher.app" 175 120 \
  --hide-extension "MyAmpSwitcher.app" \
  --app-drop-link 425 120 \
  "dist/MyAmpSwitcher.dmg" \
  "dist/dmg/"

