import json
import mido
import os
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QComboBox, QLabel, QHBoxLayout
from PyQt5.QtGui import QIcon

# SETTINGS
script_directory = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(script_directory, "settings.json")) as settings_file:
    settings = json.load(settings_file)

port_name = settings["port_name"]
channel = settings["channel"]
output_port = None
json_file_path = os.path.join(script_directory, 'profiles', settings["profile"])

with open(json_file_path) as json_file:
    channel_data = json.load(json_file)

for port in mido.get_output_names():
    if port_name in port:
        output_port = mido.open_output(port)
        break
if not output_port:
    print(f"Error: MIDI port '{port_name}' not found.")


def send_program_change(pc_number):
    program_change = mido.Message('program_change', channel=channel, program=pc_number)
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


app = QApplication([])

window = QWidget()
window.setWindowTitle(channel_data['name'])
layout = QVBoxLayout(window)

sorted_channels = sorted(channel_data.get('channels', []), key=lambda x: x.get('order', 0))

# Create a horizontal layout for channel buttons
channel_buttons_layout = QHBoxLayout()

for channel_info in sorted_channels:
    pc_number = channel_info.get('program_change', 0)
    name = channel_info.get('name', 'Unknown')
    button = QPushButton(name)
    button.setMinimumHeight(40)
    button.clicked.connect(lambda _, ch=pc_number: send_program_change(ch))
    channel_buttons_layout.addWidget(button)

layout.addLayout(channel_buttons_layout)

# MIDI Output ComboBox
midi_output_label = QLabel("MIDI Output:")
midi_output_combobox = QComboBox()
midi_output_combobox.addItems(mido.get_output_names())
midi_output_combobox.setCurrentText(port_name)
midi_output_combobox.currentIndexChanged.connect(select_midi_output)

# MIDI Channel ComboBox
midi_channel_label = QLabel("Channel:")
midi_channel_combobox = QComboBox()
midi_channel_combobox.addItems(map(str, range(128)))  # Adding values 0 to 127
midi_channel_combobox.setCurrentText(str(channel))
midi_channel_combobox.currentIndexChanged.connect(select_midi_channel)

# Save Button
save_button = QPushButton("Save")
save_button.clicked.connect(save_settings)

# Create a horizontal layout for MIDI output, channel, and save button
midi_layout = QHBoxLayout()
midi_layout.addWidget(midi_output_label)
midi_layout.addWidget(midi_output_combobox)
midi_layout.addWidget(midi_channel_label)
midi_layout.addWidget(midi_channel_combobox)
midi_layout.addWidget(save_button)

layout.addLayout(midi_layout)

title_width = len(channel_data['name']) * 10 + 50
window.resize(title_width, 100)
window.show()

# Set the application icon
app_icon = QIcon(os.path.join(script_directory, settings["icon"]))
app.setWindowIcon(app_icon)

app.exec_()
