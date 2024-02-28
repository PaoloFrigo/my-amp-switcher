import os
import logging
import json
import shutil
import plistlib
from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QLabel,
    QComboBox,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QStatusBar,
    QMessageBox,
    QFileDialog,
    QDialog,
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

# Custom Modules
from gui.edit_settings_window import EditSettingsWindow
from gui.edit_profile_window import EditProfileWindow
from gui.profile_recorder_window import ProfileRecorderWindow
from common.profile_manager import ProfileManager, ProfileNotValid
from midi.midi_handler import MidiHandler


class MainWindow(QMainWindow):
    MIDI_LAYOUT_ORDER = [
        ("midi_output_label", 0),
        ("midi_output_combobox", 1),
        ("refresh_midi_button", 2),
        ("midi_channel_label", 3),
        ("midi_channel_combobox", 4),
        ("save_button", 5),
    ]

    def __init__(self, script_directory):
        super(MainWindow, self).__init__()

        self.script_directory = script_directory
        plist_path = os.path.join(script_directory, "Info.plist")

        # Load version from Info.plist
        with open(plist_path, "rb") as plist_file:
            plist_data = plistlib.load(plist_file)

        self.version = plist_data.get("CFBundleShortVersionString", "Unknown")
        self.midi_handler = MidiHandler(self, [])

        logging.info(f"Version {self.version}")

        self.profile_manager = ProfileManager(
            script_directory, self.version, window=self
        )
        self.profile_manager.ensure_directories_exist()
        self.settings = self.profile_manager.load_settings()

        try:
            self.profile_data = self.profile_manager.load_profile_data(
                self.settings["profile"]
            )
        except ProfileNotValid:
            logging.error(
                f"Profile {self.settings['profile']} cannot be loaded. Loading sample profile instead."
            )
            self.profile_data = self.profile_manager.load_profile_data("sample.json")
            self.profile_manager.save_settings(
                "sample.json", self.profile_data["channel"]
            )

        port_name = self.settings["port_name"]
        output_port = None

        for port in self.midi_handler.get_output():
            if port_name in port:
                output_port = self.midi_handler.set_midi_output(port_name)
                break

        if not output_port:
            logging.error(f"Error: MIDI port '{port_name}' not found.")

        self.midi_handler.set_midi_channel(self.profile_data["channel"])
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(self.profile_data["name"])
        self.setGeometry(100, 100, 600, 400)

        self.setup_menu_bar()
        self.setup_midi_layout()
        self.setup_buttons_layout()

        self.set_status_bar()
        self.set_window_icon()

    def setup_menu_bar(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)

        profile_menu = menubar.addMenu("Profile")
        self.add_menu_action(profile_menu, "New", self.new_profile)
        self.add_menu_action(profile_menu, "Edit", self.edit_profile)
        self.add_menu_action(profile_menu, "Load", self.load_profile)
        profile_menu.addSeparator()
        self.add_menu_action(profile_menu, "Record", self.record_profile)
        profile_menu.addSeparator()
        self.add_menu_action(profile_menu, "Import", self.import_profile)
        self.add_menu_action(profile_menu, "Export", self.export_profile)

        settings_menu = menubar.addMenu("Settings")
        self.add_menu_action(settings_menu, "Edit", self.edit_settings)

        help_menu = menubar.addMenu("About")
        self.add_menu_action(help_menu, "Version", self.show_about_dialog)

    def add_menu_action(self, menu, action_text, method):
        action = QAction(action_text, self)
        action.triggered.connect(method)
        menu.addAction(action)

    def setup_midi_layout(self):
        self.midi_output_label = QLabel("MIDI Output:")
        self.midi_output_combobox = QComboBox()
        self.reload_midi_output()
        self.midi_output_combobox.currentIndexChanged.connect(self.select_midi_output)

        self.refresh_midi_button = QPushButton("Refresh")
        self.refresh_midi_button.clicked.connect(self.reload_midi_output)

        self.midi_channel_label = QLabel("Channel:")
        self.midi_channel_combobox = QComboBox()
        self.midi_channel_combobox.addItems(map(str, range(17)))
        self.midi_channel_combobox.setCurrentText(
            str(self.profile_data.get("channel", 0))
        )
        self.midi_channel_combobox.currentIndexChanged.connect(self.select_midi_channel)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_channel)

        self.midi_layout = QHBoxLayout()
        for widget_name, order in self.MIDI_LAYOUT_ORDER:
            widget = getattr(self, widget_name)
            self.midi_layout.addWidget(widget)

        self.central_widget = QWidget(self)
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.addLayout(self.midi_layout)

    def setup_buttons_layout(self):
        sorted_buttons = sorted(
            self.profile_data.get("buttons", []), key=lambda x: x.get("order", 0)
        )

        self.channel_buttons_layout = QGridLayout()

        for idx, button_info in enumerate(sorted_buttons):
            button = self.create_button_from_info(button_info)
            row, col = divmod(idx, self.settings["buttons_per_row"])
            self.channel_buttons_layout.addWidget(button, row, col)

        self.central_layout.addLayout(self.channel_buttons_layout)
        self.setCentralWidget(self.central_widget)

    def create_button_from_info(self, button_info):
        name = button_info.get("name", "Unknown")
        button = QPushButton(name)
        button.setMinimumHeight(40)
        color = button_info.get("color", None)

        if color is not None:
            button.setStyleSheet(
                f"QPushButton:pressed{{background: #000;}}"
                f"QPushButton{{background: {color}; border-radius: 10px; border: 1px solid #8f8f91; padding: 1px;}}"
            )

        button.setFont(QFont(self.settings["font"], self.settings["size"]))
        button.clicked.connect(
            lambda _, pc=button_info.get(
                "program_change", None
            ), cc_num=button_info.get("cc_number", None), cc_val=button_info.get(
                "cc_value", None
            ): self.midi_handler.send_midi_message(
                pc, cc_num, cc_val
            )
        )
        return button

    def save_channel(self):
        try:
            new_profile_data = self.profile_data.copy()
            new_profile_data["channel"] = int(self.midi_channel_combobox.currentText())

            with open(
                os.path.join(
                    self.profile_manager.script_directory,
                    "profiles",
                    self.settings["profile"],
                ),
                "w",
            ) as profile_file:
                json.dump(new_profile_data, profile_file, indent=4)
            self.update_status_bar(
                f"Midi Channel saved successfully on profile '{self.settings['profile']}'"
            )
            logging.info(f"Saved {self.settings['profile']}")
        except Exception as e:
            logging.error(f"Error saving profile data: {e}")
            QMessageBox.warning(None, "Save Error", f"Error saving profile data: {e}")

    def set_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready", 2000)

    def set_window_icon(self):
        app_icon = QIcon(
            os.path.join(self.profile_manager.script_directory, self.settings["icon"])
        )
        self.setWindowIcon(app_icon)

    def update_status_bar(self, message, timeout=2000):
        self.statusBar.showMessage(message, timeout)

    def update_midi_channel_combobox(self, new_channel):
        current_index = self.midi_channel_combobox.findText(str(new_channel))
        if current_index != -1:
            self.midi_channel_combobox.setCurrentIndex(current_index)

    def update_buttons_layout(self, sorted_buttons):
        for button in self.findChildren(QPushButton):
            button.deleteLater()

        for idx, button_info in enumerate(sorted_buttons):
            pc_number = button_info.get("program_change", None)
            cc_number = button_info.get("cc_number", None)
            cc_value = button_info.get("cc_value", None)
            name = button_info.get("name", "Unknown")
            button = QPushButton(name)
            button.setMinimumHeight(40)
            color = button_info.get("color", None)
            if color is not None:
                color = button_info.get(
                    "color", "black"
                )  # Default to black if color is not specified
                button.setStyleSheet(
                    f"QPushButton:pressed{{background: #000;}}"
                    f"QPushButton{{background: {color}; border-radius: 10px; border: 1px solid #8f8f91; padding: 1px;}}"
                )
            button.setFont(QFont(self.settings["font"], self.settings["size"]))
            button.clicked.connect(
                lambda _, pc=pc_number, cc_num=cc_number, cc_val=cc_value: self.midi_handler.send_midi_message(
                    pc, cc_num, cc_val
                )
            )

            row, col = divmod(idx, self.settings["buttons_per_row"])
            self.channel_buttons_layout.addWidget(button, row, col)

    def update_content(self, new_profile_data, new_settings):
        self.profile_data = new_profile_data
        self.settings = new_settings

        self.setWindowTitle(self.profile_data["name"])

        self.update_midi_channel_combobox(self.profile_data.get("channel", 0))

        self.update_buttons_layout(
            sorted(
                self.profile_data.get("buttons", []), key=lambda x: x.get("order", 0)
            )
        )

        self.refresh_midi_button = QPushButton("Refresh")
        self.refresh_midi_button.clicked.connect(self.reload_midi_output)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_channel)

        components = [
            (self.midi_output_label, 0),
            (self.midi_output_combobox, 1),
            (self.refresh_midi_button, 2),
            (self.midi_channel_label, 3),
            (self.midi_channel_combobox, 4),
            (self.save_button, 5),
        ]
        sorted_components = sorted(components, key=lambda x: x[1])

        for widget, _ in sorted_components:
            self.midi_layout.addWidget(widget)

        self.update_status_bar("Settings saved successfully")

        self.show()

    def new_profile(self):
        template_json = {
            "name": "Template",
            "channel": 0,
            "buttons": [
                {"order": 0, "color": "green", "program_change": 1, "name": "clean"}
            ],
        }

        settings = self.profile_manager.load_settings()

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.setDirectory(
            os.path.join(self.profile_manager.script_directory, "profiles")
        )
        file_dialog.setWindowTitle("Save New Profile JSON File")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            new_profile_name = os.path.basename(selected_file)

            # Save the new profile file
            with open(
                os.path.join(
                    self.profile_manager.script_directory, "profiles", new_profile_name
                ),
                "w",
            ) as profile_file:
                json.dump(template_json, profile_file, indent=4)
            logging.info(f"Saved new profile: {new_profile_name}")

            new_profile_data = self.profile_manager.load_profile_data(new_profile_name)

            settings["profile"] = new_profile_name

            self.profile_data = new_profile_data

            self.profile_manager.save_settings(
                channel=int(self.midi_channel_combobox.currentText())
            )

            self.setWindowTitle(new_profile_name)
            self.close()
            self.__init__(self.profile_data, self.profile_manager.load_settings())

            self.update_status_bar(
                f"New profile {new_profile_name} created successfully"
            )

            self.show()

    def edit_profile(self):
        edit_profile_window = EditProfileWindow(
            self.profile_data, self, self.profile_manager.script_directory
        )
        edit_profile_window.exec_()

    def edit_settings(self):
        edit_settings__window = EditSettingsWindow(
            self.profile_data, self, self.profile_manager.script_directory
        )
        edit_settings__window.exec_()

    def load_profile(self):
        self.profile_data = self.profile_manager.change_profile()

    def import_profile(self):
        settings = self.profile_manager.load_settings()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.setDirectory(
            os.path.join(self.profile_manager.script_directory, "profiles")
        )
        file_dialog.setWindowTitle("Import Profile JSON File")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            new_profile_name = os.path.basename(selected_file)

            # Copy the selected file to the profiles directory
            destination_path = os.path.join(
                self.profile_manager.script_directory, "profiles", new_profile_name
            )
            shutil.copy(selected_file, destination_path)

            # Load the new profile data
            self.profile_data = self.profile_manager.load_profile_data(new_profile_name)

            # Update the settings and profile_data
            settings["profile"] = new_profile_name
            self.profile_manager.change_profile()

    def record_profile(self):
        record_window = ProfileRecorderWindow()
        record_window.exec_()

    def export_profile(self):
        self.profile_manager.load_settings()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)  # Fix this line
        file_dialog.setNameFilter("JSON files (*.json)")
        file_dialog.setDirectory(
            os.path.join(self.profile_manager.script_directory, "profiles")
        )
        file_dialog.setWindowTitle("Export the this profile as JSON File")
        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            export_profile_name = os.path.basename(selected_file)

            with open(selected_file, "w") as profile_file:
                json.dump(self.profile_data, profile_file, indent=4)
            self.update_status_bar(
                f"Profile exported successfully: {export_profile_name}"
            )
            logging.info(f"Exported profile: {export_profile_name}")

    def select_midi_channel(self, index):
        selected_channel = self.midi_channel_combobox.itemText(index)
        self.profile_data["channel"] = int(selected_channel)
        self.update_status_bar(f"MIDI channel {selected_channel} selected.")

    def reload_midi_output(self):
        midi_outputs = (
            self.midi_handler.get_output() if self.midi_handler.get_output() else []
        )

        current_items = [
            self.midi_output_combobox.itemText(i)
            for i in range(self.midi_output_combobox.count())
        ]

        for item in current_items:
            if item not in midi_outputs:
                index = self.midi_output_combobox.findText(item)
                if index != -1:
                    self.midi_output_combobox.removeItem(index)

        for output in midi_outputs:
            if output not in current_items:
                self.midi_output_combobox.addItem(output)

        if self.settings["port_name"] != "":
            self.midi_output_combobox.setCurrentText(self.settings["port_name"])

        return midi_outputs

    def show_about_dialog(self):
        about_text = f"""<h2>MyAmpSwitcher v{self.profile_manager.version}</h2>
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

    def select_midi_output(self, index):
        selected_port = self.midi_output_combobox.itemText(index)
        self.settings["port_name"] = selected_port

        try:
            self.midi_handler.set_midi_output(selected_port)
        except Exception as e:
            logging.error(f"Error opening MIDI port: {e}")
            self.update_status_bar("MIDI Output selected cannot be empty")
            self.midi_handler.midi_output = None
