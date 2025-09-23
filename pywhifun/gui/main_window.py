import sys
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QFileDialog
)
from .subject_details_dialog import SubjectDetailsDialog
from pywhifun.preprocessing.pipeline import run_preprocessing_pipeline


class PipelineWorker(QObject):
    """
    A worker object for running the preprocessing pipeline in a separate thread.
    """
    finished = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        """Runs the long-running task."""
        try:
            self.progress.emit("--- Starting PyWhiFuN Preprocessing Pipeline (STUBBED) ---")
            # For now, use dummy paths and params from the GUI
            run_preprocessing_pipeline(
                output_folder=self.params.get("output_folder", "/tmp/pywhifun_output"),
                subject_list_csv="Subj_list.csv",
                params=self.params
            )
            self.progress.emit("--- PyWhiFuN Preprocessing Pipeline Finished ---")
        except Exception as e:
            self.progress.emit(f"PIPELINE CRITICAL ERROR: {e}")
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    """
    Main window for the PyWhiFuN application.

    This class sets up the main graphical user interface, including all the
    widgets for user interaction, organized into logical groups.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyWhiFuN - Python White-matter Functional Networks Toolbox")
        self.setGeometry(100, 100, 800, 700)  # x, y, width, height

        self.subject_details = {}  # To store details from the non-BIDS dialog

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self._create_path_setup_group()
        self._create_data_config_group()
        self._create_preprocessing_group()
        self._create_network_construction_group()
        self._create_log_area()

        self.main_layout.addStretch()

        self._connect_signals()

    def _connect_signals(self):
        """Connects widget signals to their corresponding slots (methods)."""
        self.output_path_button.clicked.connect(self._browse_output_folder)
        self.data_path_button.clicked.connect(self._browse_data_folder)
        self.bids_checkbox.toggled.connect(self._on_bids_toggled)
        self.all_subjects_checkbox.toggled.connect(self._on_all_subjects_toggled)
        self.data_check_button.clicked.connect(self._run_data_check)
        self.preprocessing_params_button.clicked.connect(self._open_preprocessing_params)
        self.run_preprocessing_button.clicked.connect(self._run_preprocessing)
        self.exclude_subjects_checkbox.toggled.connect(self._on_exclude_subjects_toggled)
        self.create_wm_fn_button.clicked.connect(self._create_wm_fn)
        self.create_gm_fn_button.clicked.connect(self._create_gm_fn)
        self.display_fn_button.clicked.connect(self._display_fn)

    def _log(self, message):
        """Appends a message to the log text edit."""
        self.log_edit.append(message)
        QApplication.processEvents() # Update the GUI to show the message immediately

    # --- Callback Methods / Slots ---

    def _browse_output_folder(self):
        self._log("ACTION: Browse for output folder...")
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_path:
            self.output_path_edit.setText(folder_path)
            self._log(f"INFO: Output folder set to: {folder_path}")

    def _browse_data_folder(self):
        self._log("ACTION: Browse for subject data folder...")
        folder_path = QFileDialog.getExistingDirectory(self, "Select Subject Data Folder")
        if folder_path:
            self.data_path_edit.setText(folder_path)
            self._log(f"INFO: Subject data folder set to: {folder_path}")

    def _on_bids_toggled(self, checked):
        self._log(f"EVENT: 'BIDS format' checkbox toggled to {checked}.")
        if not checked:
            dialog = SubjectDetailsDialog(self)
            if dialog.exec():
                self.subject_details = dialog.get_details()
                self._log("INFO: Non-BIDS details submitted by user.")
                self._log(str(self.subject_details))
            else:
                self._log("INFO: Non-BIDS details dialog was canceled.")
                # Re-check the box if the user cancels, as non-BIDS path requires these details.
                self.bids_checkbox.setChecked(True)

    def _on_all_subjects_toggled(self, checked):
        self._log(f"EVENT: 'All folders are subjects' checkbox toggled to {checked}.")
        # Placeholder for logic to update subject list

    def _run_data_check(self):
        self._log("ACTION: 'Run Data Check' clicked.")

    def _open_preprocessing_params(self):
        self._log("ACTION: 'Preprocessing Parameters' clicked.")
        # Placeholder for opening a parameters dialog

    def _run_preprocessing(self):
        """
        Gathers parameters and runs the preprocessing pipeline in a separate thread
        to avoid freezing the GUI.
        """
        self._log("ACTION: 'Run Preprocessing' clicked. Preparing to start pipeline...")
        self.run_preprocessing_button.setEnabled(False)

        # For now, create some dummy parameters to pass to the stubbed pipeline
        # In the future, these will be read from dedicated parameter dialogs
        params = {
            'n_vol_dis': 10,
            'Reg_': 1,
            'filter_check': 0,
            'Smooth_': 1
        }
        params['output_folder'] = self.output_path_edit.text()
        if not params['output_folder']:
            self._log("ERROR: Output folder cannot be empty.")
            self.run_preprocessing_button.setEnabled(True)
            return

        # Create a QThread and a worker
        self.thread = QThread()
        self.worker = PipelineWorker(params)
        self.worker.moveToThread(self.thread)

        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self._log) # Log progress from the pipeline to the GUI

        # Re-enable button when the thread is finished
        self.thread.finished.connect(
            lambda: self.run_preprocessing_button.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self._log("Pipeline thread has finished.")
        )

        # Start the thread
        self.thread.start()

    def _on_exclude_subjects_toggled(self, checked):
        self._log(f"EVENT: 'Manually exclude subjects' checkbox toggled to {checked}.")
        # Placeholder for enabling subject exclusion UI

    def _create_wm_fn(self):
        self._log("ACTION: 'Create WM-FN' clicked.")

    def _create_gm_fn(self):
        self._log("ACTION: 'Create GM-FN' clicked.")

    def _display_fn(self):
        self._log("ACTION: 'Display FN' clicked.")

    def _create_path_setup_group(self):
        """Creates the 'Path Setup' group box with widgets for folder selection."""
        group_box = QGroupBox("Path Setup")
        layout = QVBoxLayout()

        # Output folder
        output_layout = QHBoxLayout()
        output_label = QLabel("Outputs folder:")
        self.output_path_edit = QLineEdit()
        self.output_path_button = QPushButton("Browse...")
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(self.output_path_button)
        layout.addLayout(output_layout)

        # Data folder
        data_layout = QHBoxLayout()
        data_label = QLabel("Subject Data Folder:")
        self.data_path_edit = QLineEdit()
        self.data_path_button = QPushButton("Browse...")
        data_layout.addWidget(data_label)
        data_layout.addWidget(self.data_path_edit)
        data_layout.addWidget(self.data_path_button)
        layout.addLayout(data_layout)

        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _create_data_config_group(self):
        """Creates the 'Data Configuration' group box."""
        group_box = QGroupBox("Data Configuration")
        layout = QHBoxLayout()

        self.bids_checkbox = QCheckBox("BIDS format")
        self.bids_checkbox.setChecked(True)

        self.all_subjects_checkbox = QCheckBox("All folders are subjects")
        self.all_subjects_checkbox.setChecked(True)

        layout.addWidget(self.bids_checkbox)
        layout.addWidget(self.all_subjects_checkbox)
        layout.addStretch()

        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _create_preprocessing_group(self):
        """Creates the 'Preprocessing' group box."""
        group_box = QGroupBox("Preprocessing")
        layout = QHBoxLayout()

        self.data_check_button = QPushButton("Run Data Check")
        self.preprocessing_params_button = QPushButton("Preprocessing Parameters")
        self.run_preprocessing_button = QPushButton("Run Preprocessing")

        layout.addWidget(self.data_check_button)
        layout.addWidget(self.preprocessing_params_button)
        layout.addWidget(self.run_preprocessing_button)
        layout.addStretch()

        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _create_network_construction_group(self):
        """Creates the 'Construct FN and FC' group box."""
        group_box = QGroupBox("Construct FN and FC")
        layout = QVBoxLayout()

        # Manual Exclude
        exclude_layout = QHBoxLayout()
        self.exclude_subjects_checkbox = QCheckBox("Manually exclude subjects")
        exclude_layout.addWidget(self.exclude_subjects_checkbox)
        exclude_layout.addStretch()
        layout.addLayout(exclude_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.create_wm_fn_button = QPushButton("Create WM-FN")
        self.create_gm_fn_button = QPushButton("Create GM-FN")
        self.display_fn_button = QPushButton("Display FN")
        button_layout.addWidget(self.create_wm_fn_button)
        button_layout.addWidget(self.create_gm_fn_button)
        button_layout.addWidget(self.display_fn_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _create_log_area(self):
        """Creates the 'Log' text area."""
        group_box = QGroupBox("Log")
        layout = QVBoxLayout()
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        layout.addWidget(self.log_edit)
        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

if __name__ == '__main__':
    # This block allows the GUI to be run directly for testing purposes.
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
