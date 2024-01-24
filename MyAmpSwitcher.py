import json
import mido
import os
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
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

def send_program_change(port, channel, pc_number):
    program_change = mido.Message('program_change', channel=channel, program=pc_number)
    port.send(program_change)

app = QApplication([])

window = QWidget()
window.setWindowTitle(channel_data['name'])
layout = QVBoxLayout(window)

sorted_channels = sorted(channel_data.get('channels', []), key=lambda x: x.get('order', 0))

for channel_info in sorted_channels:
    pc_number = channel_info.get('program_change', 0)
    name = channel_info.get('name', 'Unknown')
    button = QPushButton(name)
    button.setMinimumHeight(40)
    button.clicked.connect(lambda _, ch=pc_number: send_program_change(output_port, channel, ch))
    layout.addWidget(button)

title_width = len(channel_data['name']) * 10 + 50
window.resize(title_width, 200)
window.show()

# Set the application icon
app_icon = QIcon(os.path.join(script_directory, settings["icon"]))
app.setWindowIcon(app_icon)

app.exec_()
