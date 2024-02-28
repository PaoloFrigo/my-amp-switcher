import json
import logging
import os
from PyQt5.QtWidgets import QDialog, QMessageBox, QPushButton, QTextEdit, QVBoxLayout


class EditSettingsWindow(QDialog):
    def __init__(self, profile_data, main_window, script_directory):
        super(EditSettingsWindow, self).__init__()

        self.setting_filename = "settings.json"
        self.profile_data = profile_data
        self.main_window = main_window
        self.script_directory = script_directory

        self.setWindowTitle("Edit Settings")
        self.setGeometry(100, 100, 600, 400)

        self.settings_data = self.load_settings()

        self.json_text = QTextEdit(self)
        self.json_text.setPlainText(json.dumps(self.settings_data, indent=4))

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_and_close)

        layout = QVBoxLayout()
        layout.addWidget(self.json_text)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_and_close(self):
        try:
            new_settings_data = json.loads(self.json_text.toPlainText())
            self.settings_data.update(new_settings_data)

            with open(
                os.path.join(self.script_directory, self.setting_filename), "w"
            ) as settings_file:
                json.dump(self.settings_data, settings_file, indent=4)
            logging.info("Saved settings")

            self.accept()
            self.reload_main_window()

        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"Error in JSON format: {e}")

    def reload_main_window(self):
        new_settings_data = json.loads(self.json_text.toPlainText())
        new_settings = self.main_window.settings.copy()
        new_settings.update(new_settings_data)

        self.main_window.update_content(self.profile_data, new_settings)
        self.main_window.update_status_bar("Settings saved successfully")
        self.accept()

    def load_settings(self):
        with open(
            os.path.join(self.script_directory, self.setting_filename)
        ) as settings_file:
            return json.load(settings_file)
