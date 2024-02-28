import json
import os
import logging
from PyQt5.QtWidgets import QDialog, QTextEdit, QPushButton, QVBoxLayout, QMessageBox


class EditProfileWindow(QDialog):
    def __init__(self, profile_data, main_window, script_directory):
        super(EditProfileWindow, self).__init__()

        self.setting_filename = "settings.json"
        self.profile_data = profile_data
        self.main_window = main_window
        self.script_directory = script_directory

        self.settings = self.load_settings()

        self.setWindowTitle("Edit Profile")
        self.setGeometry(100, 100, 600, 400)

        # Create a text area to display JSON content
        self.json_text = QTextEdit(self)
        self.json_text.setPlainText(json.dumps(profile_data, indent=4))

        # Save Button
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_and_close)

        layout = QVBoxLayout()
        layout.addWidget(self.json_text)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_and_close(self):
        try:
            new_profile_data = json.loads(self.json_text.toPlainText())
            self.update_profile_data(new_profile_data)
            self.save_profile_data()
            self.reload_main_window()

        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"Error in JSON format: {e}")

    def update_profile_data(self, new_profile_data):
        self.profile_data.update(new_profile_data)

    def save_profile_data(self):
        profile_path = os.path.join(
            self.script_directory, "profiles", self.settings["profile"]
        )

        try:
            with open(profile_path, "w") as profile_file:
                json.dump(self.profile_data, profile_file, indent=4)
            logging.info(f"Saved {self.settings['profile']}")

        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Error saving profile: {e}")

    def reload_main_window(self):
        self.main_window.update_content(self.profile_data, self.settings)
        self.main_window.update_status_bar("Profile saved successfully")

        self.accept()

    def load_settings(self):
        settings_path = os.path.join(self.script_directory, self.setting_filename)

        try:
            with open(settings_path) as settings_file:
                return json.load(settings_file)

        except Exception as e:
            QMessageBox.warning(self, "Settings Error", f"Error loading settings: {e}")
            return {}
