import os
import logging
import json
from PyQt5.QtWidgets import QMessageBox, QFileDialog


def is_json_file(filename):
    try:
        with open(filename, "r") as f:
            json.load(f)
        return True
    except ValueError as e:
        logging.error("invalid json: %s" % e)
        return False


class ProfileNotValid(Exception):
    pass


class ProfileManager:
    def __init__(self, script_directory, version, profile_data=None, window=None):
        self.script_directory = script_directory
        self.window = window
        self.profile_data = profile_data
        self.version = version
        self.settings = self.load_settings()

    def reload_window(self, window):
        self.window = window

    def reload_profile_data(self, profile_data):
        self.profile_data = profile_data

    def ensure_directories_exist(self):
        profiles_directory = os.path.join(self.script_directory, "profiles")
        os.makedirs(profiles_directory, exist_ok=True)

    def load_profile_data(self, profile_name):
        json_file_path = os.path.join(self.script_directory, "profiles", profile_name)
        if not os.path.isfile(json_file_path):
            logging.warning(
                f"Profile file not found: {profile_name}. Creating a new one."
            )
            return {"name": "New Profile", "channel": 0, "buttons": []}
        if not is_json_file(json_file_path):
            logging.error(f"Invalid JSON profile: {profile_name}. Creating a new one.")
            QMessageBox.warning(
                None,
                "Invalid JSON profile",
                f"Error loading the file: {json_file_path}. \nPlease make sure the file content is a valid JSON file.",
            )
            return {"name": "New Profile", "channel": 0, "buttons": []}
        try:
            with open(json_file_path) as json_file:
                return json.load(json_file)
        except Exception as e:
            logging.error(f"Error loading profile data: {e}")
            raise ProfileNotValid("Error loading profile data") from e

    def load_settings(self, settings_filename="settings.json"):
        settings_file_path = os.path.join(self.script_directory, settings_filename)
        default_settings = {
            "port_name": "",
            "channel": 0,
            "profile": "default.json",
            "icon": "icon.icns",
        }

        if not os.path.isfile(settings_file_path):
            logging.warning("Settings file not found. Using default settings.")
            return default_settings

        try:
            with open(settings_file_path) as settings_file:
                return json.load(settings_file)
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            return default_settings

    def save_settings(
        self, profile_name=None, channel=0, profile_data=None, port_name=None
    ):
        try:
            if port_name:
                self.settings["port_name"] = port_name
            if profile_name:
                self.settings["profile"] = profile_name
                with open(
                    os.path.join(self.script_directory, "settings.json"), "w"
                ) as settings_file:
                    json.dump(self.settings, settings_file, indent=4)
                logging.info("Saved settings.json")

            if profile_data:
                new_profile_data = profile_data.copy()
                new_profile_data["channel"] = new_profile_data.get("channel", channel)

        except Exception as e:
            logging.error(f"Error saving settings: {e}")
            QMessageBox.warning(None, "Save Error", f"Error saving settings: {e}")

    def change_profile(self, selected_file=None):
        # Importing the profile
        if selected_file is None:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.ExistingFile)
            file_dialog.setNameFilter("JSON files (*.json)")
            file_dialog.setDirectory(os.path.join(self.script_directory, "profiles"))
            file_dialog.setWindowTitle("Select Profile JSON File")

            if file_dialog.exec_() == QFileDialog.Accepted:
                selected_file = file_dialog.selectedFiles()[0]
            else:
                self.window.update_status_bar("No profile selected")
                return

        new_profile_name = os.path.basename(selected_file)
        new_profile_data = self.load_profile_data(new_profile_name)

        self.settings["profile"] = new_profile_name
        self.profile_data = new_profile_data

        channel = new_profile_data.get("channel", 0)

        self.save_settings(os.path.basename(selected_file), channel)

        self.window.update_content(self.profile_data, self.settings)
        self.window.update_status_bar("Profile loaded")
        return new_profile_data
