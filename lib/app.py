import time
import logging
import os
import sys
from typing import cast
from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core import init_logging, CoffeeChatCore

logger: logging.Logger = logging.getLogger(__name__)


class CoffeeChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.sit_mode = "out"
        self.maybe_solo_participant = None

    def initUI(self):
        # create the window
        self.setGeometry(100, 100, 800, 500)
        self.setWindowTitle("Coffee Chat Pairings Generator")

        self.inputFilesGroupBox = self.createInputsBox()
        self.startButtonBox = self.createStartButtonBox()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.inputFilesGroupBox)
        main_layout.addWidget(self.startButtonBox)
        main_layout.addWidget(self.message)

        self.setLayout(main_layout)

    def createStartButtonBox(self):
        startButtonBox = QGroupBox()
        startButtonLayout = QVBoxLayout()

        self.message = QLabel()
        self.message.setStyleSheet("color: red")
        startButtonLayout.addWidget(self.message)

        startButton = QPushButton("Generate this month's coffee chat pairings!")
        startButton.clicked.connect(self.onButtonClicked)
        startButtonLayout.addWidget(startButton)

        startButtonBox.setLayout(startButtonLayout)
        return startButtonBox

    def onButtonClicked(self):
        participants_file_path = self.file_path_label.text()
        res_filename = self.text_box.text()

        if res_filename.lower() == "constraints" or res_filename.lower() == "constraints.csv":
            self.message.setText(
                "The filename 'CONSTRAINTS.csv' is reserved for the constraints file. Please choose a different filename."
            )
            self.message.show()
        elif participants_file_path == "No file selected" or res_filename == "":
            self.message.setText(
                "Please specify the file for this month's participants, and a filename for storing this month's generated pairings."
            )
            self.message.show()
        else:
            self.message.setText("")
            if not res_filename.endswith(".csv"):
                res_filename += ".csv"

            core = CoffeeChatCore(participants_file_path, res_filename)
            loaded_data = core.load_data()

            participant_names = loaded_data.participant_names
            constraints_names = loaded_data.constraints_names

            if len(participant_names) % 2 == 1:
                if "Eliette Seo" in participant_names and "Michael Youn" in participant_names:
                    self.sit_mode = "out"
                    ret = self.createOddOneOutBox().exec()
                    if ret == 0:
                        participant_names.remove("Eliette Seo")
                    elif ret == 1:
                        participant_names.remove("Michael Youn")
                elif "Eliette Seo" in participant_names:
                    self.maybe_solo_participant = "Eliette"
                    self.createNotifyRemoveOneBox().exec()
                    participant_names.remove("Eliette Seo")
                elif "Michael Youn" in participant_names:
                    self.maybe_solo_participant = "Michael"
                    self.createNotifyRemoveOneBox().exec()
                    participant_names.remove("Michael Youn")
                else:
                    self.sit_mode = "in"
                    ret = self.createOddOneOutBox().exec()
                    if ret == 0:
                        participant_names.append("Eliette Seo")
                    elif ret == 1:
                        participant_names.append("Michael Youn")

            # generate pairing
            pair_names = core.run_matchmaking(participant_names, constraints_names)
            core.sanity_check_matches(
                pair_names,
                participant_names,
            )
            core.finalize_matches(pair_names)
            self.message.setStyleSheet("color: green")
            self.message.setText(f"Pairings generated! Check {core.results_filename}")

    def createInputsBox(self) -> QGroupBox:
        inputFilesGroupBox = QGroupBox("Select participants")
        group_box_layout = QVBoxLayout()

        # select file
        button = QPushButton("Select participants file")
        button.clicked.connect(self.select_file)
        group_box_layout.addWidget(button)
        self.file_path_label = QLabel()
        self.file_path_label.setText("No file selected")
        group_box_layout.addWidget(self.file_path_label)

        group_box_layout.addStretch(1)

        # specify results filename
        filename_label = QLabel(
            "Specify results filename (.csv will automatically be appended)"
        )
        self.text_box = QLineEdit()
        group_box_layout.addWidget(filename_label)
        group_box_layout.addWidget(self.text_box)

        inputFilesGroupBox.setLayout(group_box_layout)

        return inputFilesGroupBox

    def createOddOneOutBox(self) -> QMessageBox:
        michael_button = QPushButton("Michael")
        eliette_button = QPushButton("Eliette")

        box = QMessageBox(self)
        box.setWindowTitle("Odd number of participants this time!")
        box.setText(f"Who's volunteering to sit {self.sit_mode}?")
        box.addButton(eliette_button, QMessageBox.ButtonRole.NoRole)  # returns 0
        box.addButton(michael_button, QMessageBox.ButtonRole.YesRole)  # returns 1

        return box

    def createNotifyRemoveOneBox(self) -> QMessageBox:
        box = QMessageBox(self)
        box.setWindowTitle("Odd number of participants this time!")
        box.setText(f"Only {self.maybe_solo_participant} is participating this time. Removing them from this month's participants.")
        box.setStandardButtons(QMessageBox.StandardButton.Ok)

        return box

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", ".", "CSV Files (*.csv)"
        )
        if file_path:
            self.file_path_label.setText(file_path)

    def center(self):
        qrect = self.frameGeometry()
        cp = cast(QScreen, self.screen()).availableGeometry().center()
        qrect.moveCenter(cp)
        self.move(qrect.topLeft())


def main():
    app = QApplication(sys.argv)
    ex = CoffeeChatWidget()
    ex.center()
    ex.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        if "CoffeeChatPairing.app/Contents/MacOS/CoffeeChatPairing" in sys.executable:
            # we're running in windowed mode, go to app location and go up a few
            os.chdir(os.path.dirname(sys.executable))
            os.chdir("../../..")
        else:
            os.chdir(os.path.dirname(sys.executable))

        init_logging(verbose=True)
        main()
    except Exception as e:
        logger.error(f"Error: {e}")
