from setuptools import setup

# Version and GitHub link
VERSION = "1.0.0"
GITHUB_URL = "https://github.com/paolofrigo/my-amp-switcher"

APP = ["MyAmpSwitcher.py"]
DATA_FILES = [
    ("profiles", ["profiles"]),  # Include the 'profiles' folder and its contents
    (
        ".",
        ["icon.icns", "icon.ico", "settings.json"],
    ),  # Include 'icon.icns', 'icon.ico', and 'settings.json' in the root directory
]

# macOS options for py2app
MAC_OPTIONS = {
    "argv_emulation": True,
    "packages": ["mido", "PyQt5"],
    "includes": ["json"],
    "iconfile": "icon.icns",
    "plist": {"CFBundleVersion": VERSION},  # Set the CFBundleVersion
}

# Windows options for pyinstaller
WINDOWS_OPTIONS = {
    'packages': ['mido', 'PyQt5'],
    'includes': ['json'],
    'icon': 'icon.ico',
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={
        'py2app': MAC_OPTIONS,
        'pyinstaller': WINDOWS_OPTIONS,
    },
    install_requires=[
        'mido==1.3.2',
        'PyQt5==5.15.10',
        'python-rtmidi==1.5.8',
    ],
    version=VERSION,
    url=GITHUB_URL,
)
