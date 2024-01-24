import mido
import time
from mido import MidiFile, MidiTrack, Message

def send_program_change(port, channel, pc_number):
    program_change = Message('program_change', channel=channel, program=pc_number)
    port.send(program_change)

def send_control_change(port, channel, cc_number, cc_value):
    control_change = Message('control_change', channel=channel, control=cc_number, value=cc_value)
    port.send(control_change)

def list_midi_output():
    print(mido.get_output_names())

def main():
    # Replace 'Your MIDI Port Name' with the actual MIDI port name
    port_name = 'USB MIDI CABLE'

    output_port = None
    for port in mido.get_output_names():
        if port_name in port:
            output_port = mido.open_output(port)
            break

    if not output_port:
        print(f"Error: MIDI port '{port_name}' not found.")
        return

    channel = 0

    channel_names = {1:"boost", 2:"clean", 3:"xlead"}
    for pc_number in [1,2,3]:
        send_program_change(output_port, channel, pc_number)
        print(f"{pc_number} - {channel_names[pc_number]}")
        time.sleep(2)


if __name__ == "__main__":
    main()
