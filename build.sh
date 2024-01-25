#!/bin/zsh

python3 setup.py py2app
rm releases/MyAmpSwitcher.dmg
hdiutil create -format UDZO -srcfolder dist/MyAmpSwitcher.app -o releases/MyAmpSwitcher.dmg 
hdiutil attach MyAmpSwitcher.dmg
cp icon.jpeg /Volumes/MyAmpSwitcher/.background