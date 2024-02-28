import mido
import json
import logging
from PyQt5.QtWidgets import QMessageBox


class MidiHandler:
    def __init__(self, window, midi_message_list=[]):
        self.window = window
        self.midi_input = None
        self.midi_message_list = midi_message_list
        self.midi_output = None
        self.midi_channel = None

    def set_midi_channel(self, midi_channel):
        self.midi_channel = midi_channel

    def set_midi_output(self, output_port):
        self.midi_output = self.open_output(output_port)

    def start_midi_input(self):
        try:
            self.midi_input = mido.open_input()
            self.window.update_status_bar("MIDI Input Capture\n")
            self.midi_input.callback = self.handle_midi_message
        except Exception as e:
            self.window.update_status_bar(f"Error starting MIDI input: {e}\n")

    def stop_midi_input(self):
        if self.midi_input:
            self.midi_input.close()
            self.window.update_status_bar("MIDI Input Stopped\n")
            self.midi_input = None

    def handle_midi_message(self, message):
        self.midi_message_list.append(message)
        self.window.midi_log.append(f"{message}")
        self.window.update_status_bar(f"Received MIDI message: {message}")

    def generate_profile(self):
        profile_name = "profilename"
        channel = 0
        buttons = []

        for counter, rec in enumerate(self.midi_message_list):
            button = {}
            if hasattr(rec, "program") or hasattr(rec, "control"):
                button = {"order": counter, "name": f"button {counter + 1}"}
            if hasattr(rec, "program"):
                button["program_change"] = rec.program
            if hasattr(rec, "control"):
                button["cc_number"] = rec.control
                button["cc_value"] = rec.value
            if button:
                buttons.append(button)

        config_data = {"name": profile_name, "channel": channel, "buttons": buttons}
        self.window.update_status_bar("Profile generated")
        self.window.right_column.clear()
        self.window.right_column.append(json.dumps(config_data, indent=2))

    def send_midi_message(self, pc_number, cc_number, cc_value):

        if self.midi_output is None:
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
                    "program_change", channel=self.midi_channel, program=pc_number
                )
                self.midi_output.send(program_change)
                status_message += f"Program: {pc_number}"

            if cc_number is not None and cc_value is not None:
                cc_message = mido.Message(
                    "control_change",
                    channel=self.midi_channel,
                    control=cc_number,
                    value=cc_value,
                )
                self.midi_output.send(cc_message)
                status_message += f"Control: {cc_number} Value: {cc_value}"
            self.window.update_status_bar(status_message)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

    def get_output(self):
        return mido.get_output_names()

    def open_output(self, selected_port):
        return mido.open_output(selected_port)
