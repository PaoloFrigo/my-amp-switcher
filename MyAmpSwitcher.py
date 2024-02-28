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

    window = MainWindow(script_directory)

    window.show()

    def cleanup():
        logging.info("Cleaning up resources...")

    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
