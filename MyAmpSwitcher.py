import logging
import os

import sys
from PyQt5.QtWidgets import QApplication

# Custom Modules
from gui.main_window import MainWindow


def configure_logging(script_directory):
    log_file_path = os.path.join(script_directory, "MyAmpSwitcher.log")
    logging.basicConfig(
        filename=log_file_path,
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def main():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    configure_logging(script_directory)
    logging.info("Application started")

    app = QApplication([])

    # port_name = settings["port_name"]
    # output_port = None

    # for port in midi_handler.get_output():
    #     if port_name in port:
    #         output_port = midi_handler.open_output(port)
    #         break
    # if not output_port:
    #     logging.error(f"Error: MIDI port '{port_name}' not found.")

    window = MainWindow(script_directory)
    # profile_manager.reload_window(window)
    # profile_manager.reload_profile_data(profile_data)
    # if len(midi_handler.get_output()) == 0:
    #     window.update_status_bar("No MIDI output found.")

    window.show()

    def cleanup():
        logging.info("Cleaning up resources...")

    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
