import logging
import os
import sys
from typing import cast
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QFileDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from core import init_logging, CoffeeChatCore

logger: logging.Logger = logging.getLogger(__name__)


class CoffeeChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # create the window
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("Coffee Chat Pairings Generator")

        self.inputFilesGroupBox = self.createInputsBox()
        self.startButtonBox = self.createStartButtonBox()
        self.oddOneOutBox = self.createOddOneOutBox()

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
        file_path = self.file_path_label.text()
        folder_path = self.folder_path_label.text()
        filename = self.text_box.text()

        if (
            file_path == "No file selected"
            or folder_path == "No folder selected"
            or filename == ""
        ):
            self.message.setText(
                "Please specify a participants file, results destination, and a results filename."
            )
            self.message.show()
        else:
            self.message.setText("")
            if not filename.endswith(".csv"):
                filename += ".csv"
            core = CoffeeChatCore(file_path, os.path.join(folder_path, filename))
            loaded_data = core.load_data()

            participant_names = loaded_data.participant_names
            constraints_names = loaded_data.constraints_names

            if len(participant_names) % 2 == 1:
                ret = self.oddOneOutBox.exec()
                if ret == 0:
                    participant_names.remove("Eliette Seo")
                elif ret == 1:
                    participant_names.remove("Michael Youn")

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

        # select folder
        button = QPushButton("Select pairing results destination folder")
        button.clicked.connect(self.select_folder)
        group_box_layout.addWidget(button)
        self.folder_path_label = QLabel()
        self.folder_path_label.setText("No folder selected")
        group_box_layout.addWidget(self.folder_path_label)

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
        box.setText("Who's volunteering to sit out?")
        box.addButton(eliette_button, QMessageBox.NoRole)  # returns 0
        box.addButton(michael_button, QMessageBox.YesRole)  # returns 1

        return box

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "~", "CSV Files (*.csv)"
        )
        if file_path:
            self.file_path_label.setText(file_path)

        print(self.file_path_label.text())

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_path_label.setText(folder_path)

        # this is None if unselected
        print(self.folder_path_label.text())

    def center(self):
        qrect = self.frameGeometry()
        desktop = cast(QDesktopWidget, QApplication.desktop())
        cp = desktop.availableGeometry().center()
        qrect.moveCenter(cp)
        self.move(qrect.topLeft())


def main():
    app = QApplication(sys.argv)
    ex = CoffeeChatWidget()
    ex.center()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        init_logging(verbose=True)
        main()
    except Exception as e:
        logger.error(f"Error: {e}")
