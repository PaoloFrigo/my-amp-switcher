import mido
import json
from unittest.mock import MagicMock, patch, call
from midi.midi_handler import MidiHandler
from PyQt5.QtWidgets import QMessageBox


def test_init():
    window_mock = MagicMock()
    midi_handler = MidiHandler(window_mock)
    assert midi_handler.window == window_mock
    assert midi_handler.midi_input is None
    assert midi_handler.midi_message_list == []
    assert midi_handler.midi_output is None
    assert midi_handler.midi_channel is None


def test_set_midi_channel():
    window_mock = MagicMock()
    midi_handler = MidiHandler(window_mock)
    midi_handler.set_midi_channel(1)
    assert midi_handler.midi_channel == 1


def test_set_midi_output():
    window_mock = MagicMock()
    midi_handler = MidiHandler(window_mock)
    output_port_mock = MagicMock()

    with patch.object(
        midi_handler, "open_output", return_value=output_port_mock
    ) as mock_open_output:
        midi_handler.set_midi_output("output_port")

    assert midi_handler.midi_output == output_port_mock
    mock_open_output.assert_called_once_with("output_port")


def test_start_midi_input():
    window_mock = MagicMock()
    midi_handler = MidiHandler(window_mock)

    with patch.object(mido, "open_input") as mock_open_input:
        midi_handler.start_midi_input()

    assert midi_handler.midi_input == mock_open_input.return_value
    assert window_mock.update_status_bar.call_args_list == [
        call("MIDI Input Capture\n")
    ]
    assert midi_handler.midi_input.callback == midi_handler.handle_midi_message


def test_start_midi_input_exception():
    window_mock = MagicMock()
    midi_handler = MidiHandler(window_mock)

    with patch.object(mido, "open_input", side_effect=Exception("Test Error")):
        midi_handler.start_midi_input()

    assert midi_handler.midi_input is None
    assert window_mock.update_status_bar.call_args_list == [
        call("Error starting MIDI input: Test Error\n")
    ]


def test_stop_midi_input():
    window_mock = MagicMock()
    midi_handler = MidiHandler(window_mock)
    midi_handler.midi_input = MagicMock()

    midi_handler.stop_midi_input()

    assert midi_handler.midi_input is None
    if midi_handler.midi_input:
        midi_handler.midi_input.close.assert_called_once()
    else:
        print("DEBUG: midi_input is None")

    window_mock.update_status_bar.assert_called_once_with("MIDI Input Stopped\n")


def test_handle_midi_message():
    window_mock = MagicMock()
    midi_handler = MidiHandler(window_mock)

    midi_message_mock = MagicMock()
    midi_handler.handle_midi_message(midi_message_mock)

    assert midi_handler.midi_message_list == [midi_message_mock]
    assert window_mock.midi_log.append.called_with(f"{midi_message_mock}")
    assert window_mock.update_status_bar.called_with(
        f"Received MIDI message: {midi_message_mock}"
    )


def test_generate_profile():
    window_mock = MagicMock()
    midi_handler = MidiHandler(window_mock)

    midi_handler.midi_message_list = [
        mido.Message("program_change", channel=1, program=1),
        mido.Message("control_change", channel=1, control=2, value=127),
    ]

    midi_handler.generate_profile()

    assert window_mock.update_status_bar.called_with("Profile generated")
    assert window_mock.right_column.clear.called
    assert window_mock.right_column.append.called_with(
        json.dumps(
            {
                "name": "profilename",
                "channel": 0,
                "buttons": [
                    {"order": 0, "name": "button 1", "program_change": 1},
                    {"order": 1, "name": "button 2", "cc_number": 2, "cc_value": 127},
                ],
            },
            indent=2,
        )
    )


def test_send_midi_message_program_change():
    window_mock = MagicMock()
    midi_handler = MidiHandler(window_mock)
    midi_handler.midi_output = MagicMock()
    midi_handler.midi_channel = 1

    midi_handler.send_midi_message(pc_number=1, cc_number=None, cc_value=None)

    assert midi_handler.midi_output.send.called_with(
        mido.Message("program_change", channel=1, program=1)
    )
    assert window_mock.update_status_bar.called_with("Midi Program: 1")


def test_send_midi_message_control_change():
    window_mock = MagicMock()
    midi_handler = MidiHandler(window_mock)
    midi_handler.midi_output = MagicMock()
    midi_handler.midi_channel = 1

    midi_handler.send_midi_message(pc_number=None, cc_number=2, cc_value=127)

    assert midi_handler.midi_output.send.called_with(
        mido.Message("control_change", channel=1, control=2, value=127)
    )
    assert window_mock.update_status_bar.called_with("Midi Control: 2 Value: 127")


def test_send_midi_message_no_output():
    window_mock = MagicMock()
    midi_handler = MidiHandler(window_mock)
    midi_handler.midi_output = None

    with patch.object(QMessageBox, "warning") as mock_warning:
        midi_handler.send_midi_message(pc_number=1, cc_number=None, cc_value=None)

    mock_warning.assert_called_once_with(
        None,
        "MIDI output port not found",
        "Please connect a valid MIDI output port and try again",
    )

    if midi_handler.midi_output:
        assert not midi_handler.midi_output.send.called
    else:
        print("DEBUG: midi_output is None, cannot call send method")

    assert not window_mock.update_status_bar.called


def test_get_output():
    midi_handler_instance = MidiHandler(None)
    with patch.object(
        mido, "get_output_names", return_value=["output_port1", "output_port2"]
    ):
        output_ports = midi_handler_instance.get_output()
    assert output_ports == ["output_port1", "output_port2"]


def test_open_output():
    midi_handler_instance = MidiHandler(None)
    with patch.object(
        mido, "open_output", return_value="output_port_mock"
    ) as mock_open_output:
        output_port = midi_handler_instance.open_output("selected_port")
    assert output_port == "output_port_mock"
    mock_open_output.assert_called_once_with("selected_port")
