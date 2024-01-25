import json
import mido
import os
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QComboBox, QLabel, \
    QHBoxLayout, QFileDialog
from PyQt5.QtGui import QIcon

# Global variables
script_directory = os.path.dirname(os.path.realpath(__file__))
settings = None
profile_data = None
output_port = None
window = None
midi_channel_combobox = None  # Declare the combobox globally

def load_settings():
    with open(os.path.join(script_directory, "settings.json")) as settings_file:
        return json.load(settings_file)

def load_profile_data(profile_name):
    json_file_path = os.path.join(script_directory, 'profiles', profile_name)
    with open(json_file_path) as json_file:
        return json.load(json_file)

def create_window(profile_data):
    global window
    window = QWidget()
    window.setWindowTitle(profile_data['name'])
    layout = QVBoxLayout(window)

    sorted_buttons = sorted(profile_data.get('buttons', []), key=lambda x: x.get('order', 0))

    # Create a horizontal layout for channel buttons
    channel_buttons_layout = QHBoxLayout()

    for button_info in sorted_buttons:
        pc_number = button_info.get('program_change', 0)
        name = button_info.get('name', 'Unknown')
        button = QPushButton(name)
        button.setMinimumHeight(40)
        button.clicked.connect(lambda _, ch=pc_number: send_program_change(ch))
        channel_buttons_layout.addWidget(button)

    layout.addLayout(channel_buttons_layout)

    # MIDI Output ComboBox
    midi_output_label = QLabel("MIDI Output:")
    midi_output_combobox = QComboBox()
    midi_output_combobox.addItems(mido.get_output_names())
    midi_output_combobox.setCurrentText(settings["port_name"])
    midi_output_combobox.currentIndexChanged.connect(select_midi_output)

    # MIDI Channel ComboBox
    global midi_channel_combobox  # Make the combobox global
    midi_channel_label = QLabel("Channel:")
    midi_channel_combobox = QComboBox()
    midi_channel_combobox.addItems(map(str, range(128)))  # Adding values 0 to 127
    midi_channel_combobox.setCurrentText(str(profile_data["channel"]))
    midi_channel_combobox.currentIndexChanged.connect(select_midi_channel)

    # Save Button
    save_button = QPushButton("Save")
    save_button.clicked.connect(save_settings)

    # Profile Change Button
    profile_change_button = QPushButton("Change Profile")
    profile_change_button.clicked.connect(change_profile)

    # Create a horizontal layout for MIDI output, channel, save, and profile change buttons
    midi_layout = QHBoxLayout()
    midi_layout.addWidget(midi_output_label)
    midi_layout.addWidget(midi_output_combobox)
    midi_layout.addWidget(midi_channel_label)
    midi_layout.addWidget(midi_channel_combobox)
    midi_layout.addWidget(save_button)
    midi_layout.addWidget(profile_change_button)

    layout.addLayout(midi_layout)

    title_width = len(profile_data['name']) * 10 + 50
    window.resize(title_width, 100)
    window.show()

    # Set the application icon
    app_icon = QIcon(os.path.join(script_directory, settings["icon"]))
    app.setWindowIcon(app_icon)

    return window

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
    print(f"Error: MIDI port '{port_name}' not found.")


def send_program_change(pc_number):
    program_change = mido.Message('program_change', channel=settings["channel"], program=pc_number)
    try:
        output_port.send(program_change)
    except Exception as e:
        print(f"Unexpected error: {e}")


def select_midi_output(index):
    selected_port = midi_output_combobox.itemText(index)
    settings["port_name"] = selected_port
    global output_port
    output_port.close()  # Close the previous output port
    output_port = mido.open_output(selected_port)


def select_midi_channel(index):
    selected_channel = midi_channel_combobox.itemText(index)
    settings["channel"] = int(selected_channel)


def save_settings():
    with open(os.path.join(script_directory, "settings.json"), 'w') as settings_file:
        json.dump(settings, settings_file, indent=4)
    
    # Save the channel information to the profile as well
    new_profile_data = profile_data.copy()  # Make a copy to avoid modifying the original
    new_profile_data["channel"] = int(midi_channel_combobox.currentText())
    
    with open(os.path.join(script_directory, "profiles", settings["profile"]), 'w') as profile_file:
        json.dump(new_profile_data, profile_file, indent=4)



def change_profile():
    global window, profile_data
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFile)
    file_dialog.setNameFilter("JSON files (*.json)")
    file_dialog.setDirectory(os.path.join(script_directory, 'profiles'))
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
        window = create_window(profile_data)

app = QApplication([])

window = create_window(profile_data)

app.exec_()
