import json
import mido
import logging
import os
from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QComboBox,
    QLabel,
    QHBoxLayout,
    QFileDialog,
    QMessageBox,
    QGridLayout,
    QMainWindow,
    QAction,
    QMenuBar,
    QMenu,
    QDialog,
    QTextEdit,
)
from PyQt5.QtGui import QIcon, QFont

# Global variables
script_directory = os.path.dirname(os.path.realpath(__file__))
settings = None
profile_data = None
output_port = None
window = None
midi_channel_combobox = None

# Configure logging
log_file_path = os.path.join(script_directory, "MyAmpSwitcher.log")
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class MainWindow(QMainWindow):
    def __init__(self, profile_data):
        super(MainWindow, self).__init__()

        self.profile_data = profile_data

        # Create menu bar
        menubar = self.menuBar()

        # Create Profile menu
        profile_menu = menubar.addMenu("Profile")

        # Add actions to Profile menu
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_profile)
        profile_menu.addAction(new_action)

        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(self.edit_profile)
        profile_menu.addAction(edit_action)

        load_action = QAction("Load", self)
        load_action.triggered.connect(self.load_profile)
        profile_menu.addAction(load_action)

        # MIDI Output ComboBox
        midi_output_label = QLabel("MIDI Output:")
        midi_output_combobox = QComboBox()
        midi_output_combobox.addItems(mido.get_output_names())
        midi_output_combobox.setCurrentText(settings["port_name"])
        midi_output_combobox.currentIndexChanged.connect(select_midi_output)

        # MIDI Channel ComboBox
        global midi_channel_combobox
        midi_channel_label = QLabel("Channel:")
        midi_channel_combobox = QComboBox()
        midi_channel_combobox.addItems(map(str, range(128)))  # Adding values 0 to 127
        midi_channel_combobox.setCurrentText(
            str(profile_data.get("channel", settings["channel"]))
        )
        midi_channel_combobox.currentIndexChanged.connect(select_midi_channel)

        # Save Button
        save_button = QPushButton("Save")
        save_button.clicked.connect(save_settings)

        # Create a horizontal layout for MIDI output, channel, save, and profile change buttons
        midi_layout = QHBoxLayout()
        midi_layout.addWidget(midi_output_label)
        midi_layout.addWidget(midi_output_combobox)
        midi_layout.addWidget(midi_channel_label)
        midi_layout.addWidget(midi_channel_combobox)
        midi_layout.addWidget(save_button)

        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.addLayout(midi_layout)

        sorted_buttons = sorted(
            profile_data.get("buttons", []), key=lambda x: x.get("order", 0)
        )

        # Create a grid layout for channel buttons
        channel_buttons_layout = QGridLayout()

        for idx, button_info in enumerate(sorted_buttons):
            pc_number = button_info.get("program_change", 0)
            name = button_info.get("name", "Unknown")
            button = QPushButton(name)
            button.setMinimumHeight(40)
            button.setFont(QFont("Arial", 12))
            button.clicked.connect(lambda _, ch=pc_number: send_program_change(ch))

            # Calculate row and column indices
            row, col = divmod(idx, 4)
            channel_buttons_layout.addWidget(button, row, col)

        central_layout.addLayout(channel_buttons_layout)

        self.setCentralWidget(central_widget)

        title_width = len(profile_data["name"]) * 10 + 50
        self.resize(title_width, 100)

        # Set the application icon
        app_icon = QIcon(os.path.join(script_directory, settings["icon"]))
        self.setWindowIcon(app_icon)

    def new_profile(self):
        template_json = {
            "name": "Template",
            "channel": 0,
            "buttons": [
                {"order": 0, "color": "green", "program_change": 1, "name": "clean"}
            ],
        }

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.setDirectory(os.path.join(script_directory, "profiles"))
        file_dialog.setWindowTitle("Save New Profile JSON File")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            new_profile_name = os.path.basename(selected_file)

            # Save the new profile file
            with open(
                os.path.join(script_directory, "profiles", new_profile_name), "w"
            ) as profile_file:
                json.dump(template_json, profile_file, indent=4)
            logging.info(f"Saved new profile: {new_profile_name}")

            # Load the new profile data
            new_profile_data = load_profile_data(new_profile_name)

            # Update the settings and profile_data
            settings["profile"] = new_profile_name
            global profile_data
            profile_data = new_profile_data

            save_settings()  # Save the changes to settings.json

            # Reload the main window with the new profile data
            self.setWindowTitle(
                new_profile_name
            )  # Update window title with the new profile name
            self.close()
            self.__init__(profile_data)
            self.show()

    def edit_profile(self):
        edit_profile_window = EditProfileWindow(profile_data)
        edit_profile_window.exec_()

    def load_profile(self):
        change_profile()


class EditProfileWindow(QDialog):
    def __init__(self, profile_data):
        super(EditProfileWindow, self).__init__()

        self.profile_data = profile_data

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
        # Update profile_data based on user modifications
        try:
            new_profile_data = json.loads(self.json_text.toPlainText())
            profile_data.update(new_profile_data)

            # Save the changes to the profile file
            with open(
                os.path.join(script_directory, "profiles", settings["profile"]), "w"
            ) as profile_file:
                json.dump(profile_data, profile_file, indent=4)
            logging.info(f"Saved {settings['profile']}")

            self.accept()  # Close the window
            self.reload_main_window()  # Reload the main window with the updated profile data
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"Error in JSON format: {e}")

    def reload_main_window(self):
        global window
        window.close()
        window = MainWindow(profile_data)
        window.setWindowTitle(profile_data["name"])
        window.show()


def load_settings():
    with open(os.path.join(script_directory, "settings.json")) as settings_file:
        return json.load(settings_file)


def load_profile_data(profile_name):
    json_file_path = os.path.join(script_directory, "profiles", profile_name)
    with open(json_file_path) as json_file:
        return json.load(json_file)


def send_program_change(pc_number):
    if output_port is None:
        QMessageBox.warning(
            None,
            "MIDI output port not found",
            "Please connect a valid MIDI output port and try again",
        )
        return
    program_change = mido.Message(
        "program_change", channel=settings["channel"], program=pc_number
    )
    try:
        output_port.send(program_change)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


def select_midi_output(index):
    selected_port = midi_output_combobox.itemText(index)
    settings["port_name"] = selected_port
    global output_port
    if output_port is not None:
        output_port.close()
    output_port = mido.open_output(selected_port)


def select_midi_channel(index):
    selected_channel = midi_channel_combobox.itemText(index)
    settings["channel"] = int(selected_channel)


def save_settings():
    with open(os.path.join(script_directory, "settings.json"), "w") as settings_file:
        json.dump(settings, settings_file, indent=4)
    logging.info("Saved settings.json")

    new_profile_data = profile_data.copy()
    new_profile_data["channel"] = int(midi_channel_combobox.currentText())

    with open(
        os.path.join(script_directory, "profiles", settings["profile"]), "w"
    ) as profile_file:
        json.dump(new_profile_data, profile_file, indent=4)
    logging.info(f"Saved {settings['profile']}")


def change_profile():
    global window, profile_data
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    file_dialog.setNameFilter("JSON files (*.json)")
    file_dialog.setDirectory(os.path.join(script_directory, "profiles"))
    file_dialog.setWindowTitle("Select Profile JSON File")
    if file_dialog.exec_():
        selected_file = file_dialog.selectedFiles()[0]
        new_profile_name = os.path.basename(selected_file)

        # Load the new profile data
        new_profile_data = load_profile_data(new_profile_name)

        # Update the settings and profile_data
        settings["profile"] = new_profile_name
        profile_data = new_profile_data

        save_settings()  # Save the changes to settings.json

        window.close()
        window = MainWindow(profile_data)
        window.setWindowTitle(profile_data["name"])

        window.show()


if __name__ == "__main__":
    app = QApplication([])

    # SETTINGS
    settings = load_settings()
    profile_data = load_profile_data(settings["profile"])

    port_name = settings["port_name"]
    output_port = None

    for port in mido.get_output_names():
        if port_name in port:
            output_port = mido.open_output(port)
            break
    if not output_port:
        logging.error(f"Error: MIDI port '{port_name}' not found.")

    window = MainWindow(profile_data)
    window.setWindowTitle(profile_data["name"])
    window.show()

    app.exec_()
