from setuptools import setup

APP = ["MyAmpSwitcher.py"]
DATA_FILES = [
    (".", ["profiles"]),  # Include the 'profiles' folder and its contents
    (
        ".",
        ["icon.icns", "settings.json"],
    ),  # Include 'icon.icns' and 'settings.json' in the root directory
]
OPTIONS = {
    "argv_emulation": True,
    "packages": ["mido", "PyQt5"],
    "includes": ["json", "PyQt5.QtWidgets", "PyQt5.QtGui"],
    "iconfile": "icon.icns",
}
# Version and GitHub link
VERSION = "1.0.0"  
GITHUB_URL = "https://github.com/your-username/your-project"


setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
    install_requires=[
        "python-rtmidi",
        "mido",
        "PyQt5",
    ], 
    version=VERSION,
    url=GITHUB_URL,
)
