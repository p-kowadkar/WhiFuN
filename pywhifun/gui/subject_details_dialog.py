import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QFormLayout, QLineEdit,
    QDialogButtonBox, QVBoxLayout, QLabel
)

class SubjectDetailsDialog(QDialog):
    """
    A dialog for entering subject folder and file name details
    when the data is not in BIDS format.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Non-BIDS Data Details")

        # Create widgets
        self.intermediate_folder_edit = QLineEdit("session_1")
        self.functional_folder_edit = QLineEdit("rest_1")
        self.anatomical_folder_edit = QLineEdit("anat_1")
        self.functional_image_edit = QLineEdit("rest")
        self.anatomical_image_edit = QLineEdit("mprage")

        # Layout
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Enter the folder names and common file names for your data structure."))
        form_layout.addRow("Intermediate Folder(s):", self.intermediate_folder_edit)
        form_layout.addRow("Functional Folder Name:", self.functional_folder_edit)
        form_layout.addRow("Anatomical Folder Name:", self.anatomical_folder_edit)
        form_layout.addRow("Functional Image Name (* for wildcard):", self.functional_image_edit)
        form_layout.addRow("Anatomical Image Name (* for wildcard):", self.anatomical_image_edit)

        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def get_details(self):
        """Returns the entered details as a dictionary."""
        return {
            "intermediate_folder": self.intermediate_folder_edit.text(),
            "functional_folder": self.functional_folder_edit.text(),
            "anatomical_folder": self.anatomical_folder_edit.text(),
            "functional_image": self.functional_image_edit.text(),
            "anatomical_image": self.anatomical_image_edit.text(),
        }

if __name__ == '__main__':
    # A small test block for the dialog
    app = QApplication(sys.argv)
    dialog = SubjectDetailsDialog()
    if dialog.exec():
        print("Dialog accepted")
        print(dialog.get_details())
    else:
        print("Dialog canceled")
    sys.exit()
