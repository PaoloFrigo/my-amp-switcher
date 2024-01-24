from setuptools import setup

APP = ['MyAmpSwitcher.py']
DATA_FILES = [
    ('.', ['profiles']),  # Include the 'profiles' folder and its contents
    ('.', ['icon.icns', 'settings.json']),  # Include 'icon.icns' and 'settings.json' in the root directory
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['mido', 'PyQt5'],
    'includes': ['json', 'os', 'PyQt5.QtWidgets', 'PyQt5.QtGui'],
    'iconfile': 'icon.icns',
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=['python-rtmidi','mido', 'PyQt5'],  # Use install_requires for dependencies
)
