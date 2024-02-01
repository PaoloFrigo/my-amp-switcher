import json
import mido
import logging
import os
import sys
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
    QDialog,
    QTextEdit,
    QStatusBar
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

# Global variables
script_directory = os.path.dirname(os.path.realpath(__file__))
settings = None
profile_data = None
output_port = None
window = None
midi_channel_combobox = None
__version__ = "1.0.0 (BETA)"

# Configure logging
log_file_path = os.path.join(script_directory, "MyAmpSwitcher.log")
logging.basicConfig(
    filename=log_file_path,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def ensure_directories_exist():
    profiles_directory = os.path.join(script_directory, "profiles")
    if not os.path.exists(profiles_directory):
        os.makedirs(profiles_directory)


def load_settings():
    settings_file_path = os.path.join(script_directory, "settings.json")
    default_settings = {
        "port_name": "",
        "channel": 0,
        "profile": "default.json",  # Provide a default profile
        "icon": "icon.icns",  # Assuming there is an icon.icns file
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


def load_profile_data(profile_name):
    json_file_path = os.path.join(script_directory, "profiles", profile_name)
    if not os.path.isfile(json_file_path):
        logging.warning(f"Profile file not found: {profile_name}. Creating a new one.")
        return {"name": "New Profile", "channel": 0, "buttons": []}

    try:
        with open(json_file_path) as json_file:
            return json.load(json_file)
    except Exception as e:
        logging.error(f"Error loading profile data: {e}")
        return {"name": "Error Profile", "channel": 0, "buttons": []}


class MainWindow(QMainWindow):
    def __init__(self, profile_data, settings):
        super(MainWindow, self).__init__()

        self.profile_data = profile_data
        self.settings = settings

        # Create menu bar
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

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

        profile_menu.addSeparator()

        import_action = QAction("Import", self)
        import_action.triggered.connect(self.import_profile)
        profile_menu.addAction(import_action)

        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_profile)
        profile_menu.addAction(export_action)

        settings_menu = menubar.addMenu("Settings")
        settings_action = QAction("Edit", self)
        settings_action.triggered.connect(self.edit_settings)
        settings_menu.addAction(settings_action)

        help_menu = menubar.addMenu("About")
        about_action = QAction("Version", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        # MIDI Output ComboBox
        midi_output_label = QLabel("MIDI Output:")
        global midi_output_combobox
        midi_output_combobox = QComboBox()
        midi_outputs = self.reload_midi_output()
        # midi_output_combobox.addItems(midi_outputs)
        # midi_output_combobox.setCurrentText(settings["port_name"])
        midi_output_combobox.currentIndexChanged.connect(select_midi_output)

        refresh_midi_button = QPushButton("Refresh")
        refresh_midi_button.clicked.connect(self.reload_midi_output)

        # MIDI Channel ComboBox
        global midi_channel_combobox
        midi_channel_label = QLabel("Channel:")
        midi_channel_combobox = QComboBox()
        midi_channel_combobox.addItems(map(str, range(128)))  # Adding values 0 to 127
        midi_channel_combobox.setCurrentText(
            str(profile_data.get("channel", 0))
        )
        midi_channel_combobox.currentIndexChanged.connect(self.select_midi_channel)

        # Save Button
        save_button = QPushButton("Save")
        save_button.clicked.connect(save_channel)

        # Create a horizontal layout for MIDI output, channel, save, and profile change buttons
        midi_layout = QHBoxLayout()
        midi_layout.addWidget(midi_output_label)
        midi_layout.addWidget(midi_output_combobox)
        midi_layout.addWidget(refresh_midi_button)   
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
            pc_number = button_info.get("program_change", None)
            cc_number = button_info.get("cc_number", None)
            cc_value = button_info.get("cc_value", None)
            name = button_info.get("name", "Unknown")
            button = QPushButton(name)
            button.setMinimumHeight(40)
            button.setFont(QFont(settings["font"], settings["size"]))
            button.clicked.connect(
                lambda _, pc=button_info.get(
                    "program_change", None
                ), cc_num=button_info.get("cc_number", None), cc_val=button_info.get(
                    "cc_value", None
                ): send_midi_message(
                    pc, cc_num, cc_val
                )
            )

            # Calculate row and column indices
            row, col = divmod(idx, settings["buttons_per_row"])
            channel_buttons_layout.addWidget(button, row, col)

        central_layout.addLayout(channel_buttons_layout)

        self.setCentralWidget(central_widget)

        title_width = len(profile_data["name"]) * 10 + 50
        self.resize(title_width, 100)

        # Set status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.statusBar.showMessage("Ready", 2000) 

        # Set the application icon
        app_icon = QIcon(os.path.join(script_directory, settings["icon"]))
        self.setWindowIcon(app_icon)

    def update_status_bar(self, message, timeout=2000):
        self.statusBar.showMessage(message, timeout)

    def new_profile(self):
        template_json = {
            "name": "Template",
            "channel": 0,
            "buttons": [
                {"order": 0, "color": "green", "program_change": 1, "name": "clean"}
            ],
        }

        settings = load_settings()

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
            self.__init__(profile_data,load_settings())
            
            window.update_status_bar(f"New profile {new_profile_name} created successfully")

            self.show()

    def edit_profile(self):
        edit_profile_window = EditProfileWindow(profile_data)
        edit_profile_window.exec_()

    def edit_settings(self):
        edit_settings__window = EditSettingsWindow(profile_data)
        edit_settings__window.exec_()

    def load_profile(self):
        change_profile()

    def import_profile(self):
        settings = load_settings()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.setDirectory(os.path.join(script_directory, "profiles"))
        file_dialog.setWindowTitle("Import Profile JSON File")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            new_profile_name = os.path.basename(selected_file)

            # Copy the selected file to the profiles directory
            destination_path = os.path.join(
                script_directory, "profiles", new_profile_name
            )
            shutil.copy(selected_file, destination_path)

            # Load the new profile data
            new_profile_data = load_profile_data(new_profile_name)

            # Update the settings and profile_data
            settings["profile"] = new_profile_name
            global profile_data
            profile_data = new_profile_data

            save_settings(new_profile_name)  # Save the changes to settings.json

            self.close()
            self.__init__(profile_data)
            self.show()

    def export_profile(self):
        settings = load_settings()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)  # Fix this line
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.setDirectory(os.path.join(script_directory, "profiles"))
        file_dialog.setWindowTitle("Export Profile JSON File")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            export_profile_name = os.path.basename(selected_file)

            # Save the current profile data to the selected file
            with open(
                os.path.join(script_directory, "profiles", export_profile_name), "w"
            ) as profile_file:
                json.dump(profile_data, profile_file, indent=4)
            logging.info(f"Exported profile: {export_profile_name}")

    def select_midi_channel(self, index):
        profile = profile_data

        selected_channel = midi_channel_combobox.itemText(index)
        profile["channel"] = int(selected_channel)

    def reload_midi_output(self):
        midi_outputs = mido.get_output_names()
        current_items = list(set([midi_output_combobox.itemText(index) for index in range(midi_output_combobox.count())]))
        if  midi_outputs != current_items:
            midi_output_combobox.clear()
            midi_output_combobox.addItems(midi_outputs)
            midi_output_combobox.setCurrentText(settings["port_name"])
        else :
            pass
        return midi_outputs

    def show_about_dialog(self):
        about_text = f"""<h2>MyAmpSwitcher v{__version__}</h2>
                        MyAmpSwitcher was created by Paolo Frigo and released as an open source 
                        project under the MIT License.
                        <br><br>
                        Visit the <a href='https://github.com/paolofrigo/my-amp-switcher'>official page on GitHub</a> 
                        for more information and check for new releases. 
                        <h2>SHOW YOUR SUPPORT</h2>
                        Don't forget to give a ⭐️ on github you found this app useful!
                        <h2>DISCLAIMER</h2>
                        THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, 
                        EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
                        MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
                        IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
                        DAMAGES OR OTHER LIABILITY,
                        WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
                        CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About MyAmpSwitcher")
        about_dialog.setGeometry(200, 200, 400, 500)

        about_label = QLabel()
        about_label.setTextFormat(Qt.RichText)
        about_label.setOpenExternalLinks(True)
        about_label.setText(about_text)
        about_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(about_label)
        about_dialog.setLayout(layout)

        about_dialog.exec_()


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
        settings = load_settings()
        window = MainWindow(profile_data, settings)
        window.setWindowTitle(profile_data["name"])
        window.update_status_bar(f"Profile saved successfully")

        window.show()



class EditSettingsWindow(QDialog):
    def __init__(self, profile_data):
        super(EditSettingsWindow, self).__init__()

        self.profile_data = profile_data

        self.setWindowTitle("Edit Settings")
        self.setGeometry(100, 100, 600, 400)
        
        self.settings_data = load_settings()

        # Create a text area to display JSON content
        self.json_text = QTextEdit(self)
        self.json_text.setPlainText(json.dumps(self.settings_data, indent=4))

        # Save Button
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_and_close)

        layout = QVBoxLayout()
        layout.addWidget(self.json_text)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_and_close(self):
        # Update settings_data based on user modifications
        try:
            new_settings_data = json.loads(self.json_text.toPlainText())
            self.settings_data.update(new_settings_data)

            # Save the changes to the settings file
            with open(os.path.join(script_directory, "settings.json"), "w") as settings_file:
                json.dump(self.settings_data, settings_file, indent=4)
            logging.info("Saved settings")

            self.accept()  # Close the window
            # Close the current instance of the app
            # Close the current instance of the app
            self.reload_main_window()

        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", f"Error in JSON format: {e}")

    def reload_main_window(self):
        global window
        window.close()
        settings = load_settings()
        window = MainWindow(profile_data, settings)
        window.setWindowTitle(profile_data["name"])
        window.update_status_bar("Settings saved successfully")
        window.show()


def load_settings():
    with open(os.path.join(script_directory, "settings.json")) as settings_file:
        return json.load(settings_file)


def load_profile_data(profile_name):
    json_file_path = os.path.join(script_directory, "profiles", profile_name)
    with open(json_file_path) as json_file:
        return json.load(json_file)


def send_midi_message(pc_number, cc_number, cc_value):
    if output_port is None:
        QMessageBox.warning(
            None,
            "MIDI output port not found",
            "Please connect a valid MIDI output port and try again",
        )
        return

    try:
        status_message = "Midi "
        if pc_number is not None:
            program_change = mido.Message(
                "program_change", channel=profile_data["channel"], program=pc_number
            )
            output_port.send(program_change)
            status_message += f"Program: {pc_number}"

        if cc_number is not None and cc_value is not None:
            cc_message = mido.Message(
                "control_change",
                channel=profile_data["channel"],
                control=cc_number,
                value=cc_value,
            )
            output_port.send(cc_message)
            status_message += (f"Control: {cc_number} Value: {cc_value}")
        window.update_status_bar(status_message)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


def select_midi_output(index):
    selected_port = midi_output_combobox.itemText(index)
    settings["port_name"] = selected_port
    global output_port
    if output_port is not None:
        output_port.close()
    try:
        output_port = mido.open_output(selected_port)
    except Exception as e:
        logging.error(f"Error opening MIDI port: {e}")
        QMessageBox.warning(None, "MIDI Output Error", f"Error opening MIDI port: {e}")


def save_channel():
    try:
        if profile_data:
            new_profile_data = profile_data.copy()
            new_profile_data["channel"] = int(midi_channel_combobox.currentText())

        with open(
            os.path.join(script_directory, "profiles", settings["profile"]), "w"
        ) as profile_file:
            json.dump(new_profile_data, profile_file, indent=4)
        window.update_status_bar(f"Midi Channel saved successfully on profile '{settings['profile']}'")
        logging.info(f"Saved {settings['profile']}")
    except Exception as e:
        logging.error(f"Error saving profile data: {e}")
        QMessageBox.warning(
            None, "Save Error", f"Error saving profile data: {e}"
        )

def save_settings(profile_name=None):
    try:
        if profile_name is not None or profile_name is not False:
            settings["profile"]= profile_name
            with open(
                os.path.join(script_directory, "settings.json"), "w"
            ) as settings_file:
                json.dump(settings, settings_file, indent=4)
            logging.info("Saved settings.json")

        if profile_data:
            new_profile_data = profile_data.copy()
            new_profile_data["channel"] = int(midi_channel_combobox.currentText())

        # with open(
        #     os.path.join(script_directory, "profiles", settings["profile"]), "w"
        # ) as profile_file:
        #     json.dump(new_profile_data, profile_file, indent=4)
        # logging.info(f"Saved {settings['profile']}")
    except Exception as e:
        logging.error(f"Error saving settings: {e}")
        QMessageBox.warning(
            None, "Save Error", f"Error saving settings: {e}"
        )


def change_profile():
    global window, profile_data
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    file_dialog.setNameFilter("JSON files (*.json)")
    file_dialog.setDirectory(os.path.join(script_directory, "profiles"))
    file_dialog.setWindowTitle("Select Profile JSON File")

    settings = load_settings()
    if file_dialog.exec_():
        selected_file = file_dialog.selectedFiles()[0]
        new_profile_name = os.path.basename(selected_file)

        # Load the new profile data
        new_profile_data = load_profile_data(new_profile_name)

        # Update the settings and profile_data
        settings["profile"] = new_profile_name
        profile_data = new_profile_data

        save_settings(os.path.basename(selected_file))  # Save the changes to settings.json

        window.close()
        window = MainWindow(profile_data, settings)
        window.setWindowTitle(profile_data["name"])
        window.update_status_bar("Profile loaded successfully")
        window.show()


def main():
    global settings, profile_data, output_port, window, midi_channel_combobox

    logging.info("Application started")
    logging.info(f"Version {__version__}")

    ensure_directories_exist()

    app = QApplication([])

    # SETTINGS
    settings = load_settings()
    try:
        profile_data = load_profile_data(settings["profile"])
    except:
        profile_data = load_profile_data("sample.json")
        save_settings("sample.json")

    port_name = settings["port_name"]
    output_port = None

    

    for port in mido.get_output_names():
        if port_name in port:
            output_port = mido.open_output(port)
            break
    if not output_port:
        #window.update_status_bar(f"Error: MIDI port '{port_name}' not found.")
        logging.error(f"Error: MIDI port '{port_name}' not found.")

    window = MainWindow(profile_data, settings)
    if len(mido.get_output_names()) == 0:
        window.update_status_bar(f"No MIDI output found.")
    window.setWindowTitle(profile_data["name"])
    window.show()

    def cleanup():
        logging.info("Cleaning up resources...")
        if output_port:
            output_port.close()

    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()
