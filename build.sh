#!/bin/zsh

python3 setup.py py2app
hdiutil create -format UDZO -srcfolder dist/MyAmpSwitcher.app -o MyAmpSwitcher.dmg --overwrite
hdiutil attach MyAmpSwitcher.dmg
cp icon.jpeg /Volumes/MyAmpSwitcher/.background