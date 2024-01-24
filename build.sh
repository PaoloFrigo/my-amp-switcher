
pyinstaller --onefile --add-data "settings.json:." --add-data "icon.icns:." --add-data "profiles:profiles" MyAmpSwitcher.py
mkdir -p MyAmpSwitcher.app/Contents/MacOS
mv dist/MyAmpSwitcher MyAmpSwitcher.app/Contents/MacOS/MyAmpSwitcher
cp icon.icns MyAmpSwitcher.app/Contents/Resources/
cp settings.json MyAmpSwitcher.app/Contents/Resources/
cp -r profiles MyAmpSwitcher.app/Contents/Resources/
chmod +x MyAmpSwitcher.app/Contents/MacOS/MyAmpSwitcher