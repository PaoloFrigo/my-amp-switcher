from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSplitter,
    QTextEdit,
    QLabel,
    QVBoxLayout,
    QFileDialog,
)
from PyQt5.QtCore import QTimer
from midi.midi_handler import MidiHandler


class StatusBarUpdater:
    def __init__(self, status_label, duration=1000):
        self.status_label = status_label
        self.duration = duration

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        QTimer.singleShot(self.duration, self.clear_status_bar)

    def set_text(self, message):
        self.status_label.setText(message)

    def clear_status_bar(self):
        self.status_label.clear()


class ProfileRecorderWindow(QDialog):
    def __init__(self):
        super(ProfileRecorderWindow, self).__init__()

        self.midi_message_list = []

        self.setWindowTitle("MIDI Profile Recorder")

        self.ops_button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start", self)
        self.stop_button = QPushButton("Stop and Generate", self)

        self.ops_button_layout.addWidget(self.start_button)
        self.ops_button_layout.addWidget(self.stop_button)

        self.splitter = QSplitter()
        self.left_column = QTextEdit(self)
        self.right_column = QTextEdit(self)

        self.editor_button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save As Profile", self)
        self.clear_button = QPushButton("Clear", self)
        self.editor_button_layout.addWidget(self.clear_button)
        self.editor_button_layout.addWidget(self.save_button)
        self.midi_log = self.left_column

        self.status_label = QLabel()

        self.splitter.addWidget(self.left_column)
        self.splitter.addWidget(self.right_column)

        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.ops_button_layout)
        self.layout.addWidget(self.splitter)
        self.layout.addLayout(self.editor_button_layout)
        self.layout.addWidget(self.status_label)

        self.midi_handler = MidiHandler(self, self.midi_message_list)

        self.left_column.setReadOnly(True)
        self.right_column.setReadOnly(True)

        self.start_button.clicked.connect(self.midi_handler.start_midi_input)
        self.stop_button.clicked.connect(self.stop_midi)
        self.clear_button.clicked.connect(self.clear_midi_log)
        self.save_button.clicked.connect(self.save_config)

    def stop_midi(self):
        self.midi_handler.stop_midi_input()
        self.midi_handler.generate_profile()

    def clear_midi_log(self):
        self.midi_message_list = []
        self.midi_log.clear()
        self.right_column.clear()
        self.update_status_bar("Clear MIDI log and editor")

    def update_status_bar(self, message):
        with StatusBarUpdater(self.status_label) as updater:
            updater.set_text(message)

    def clear_status_bar(self):
        self.status_label.clear()

    def save_config(self):
        profile_data = self.right_column.toPlainText()
        if profile_data != "":
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.AnyFile)
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setNameFilter("JSON files (*.json)")
            file_dialog.setWindowTitle("Save this profile as JSON File")
            file_dialog.setDefaultSuffix("json")  # Set the default extension
            if file_dialog.exec_():
                selected_file = file_dialog.selectedFiles()[0]
                with open(selected_file, "w") as json_file:
                    json_file.writelines(profile_data)
                self.update_status_bar(
                    f"Profile exported successfully: {selected_file}"
                )
        else:
            self.update_status_bar("Nothing to save")
