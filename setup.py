import glob
from setuptools import setup

required_libraries = ["mido==1.2.9", "PyQt5==5.15.2", "python-rtmidi"]

APP = ["MyAmpSwitcher.py"]
DATA_FILES = [
    (
        "profiles",
        glob.glob("profiles/**/*", recursive=True),
    ),
    ("", ["settings.json"]),
]
OPTIONS = {
    "argv_emulation": True,
    "resources": [
        "icon.icns",
        "icon.ico",
        "settings.json",
    ]
    + glob.glob("profiles/**/*", recursive=True),
    "includes": required_libraries,
    "packages": ["PyQt5", "mido"],
    "plist": {
        "CFBundleIconFile": "icon.icns",
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
