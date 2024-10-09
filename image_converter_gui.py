import sys
import os
import time
import shutil
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QHBoxLayout, QVBoxLayout, QMessageBox, QProgressBar
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import subprocess

class ConverterThread(QThread):
    conversion_done = pyqtSignal(bool)

    def __init__(self, exe_path, input_files, output_dir):
        super().__init__()
        self.exe_path = exe_path
        self.input_files = input_files  # List of input files for the current batch
        self.output_dir = output_dir

    def run(self):
        try:
            # Create a temporary directory for the batch
            temp_input_dir = tempfile.mkdtemp(prefix="batch_")

            # Copy the batch files into the temporary directory
            for input_file in self.input_files:
                shutil.copy(input_file, temp_input_dir)

            command = [self.exe_path, temp_input_dir, self.output_dir]
            print(f"Running command: {command}")

            is_windows = sys.platform.startswith('win')

            if is_windows:
                # Set up startupinfo to hide the console window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            else:
                startupinfo = None

            # Run the command and wait for it to complete
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                shell=False,
                cwd=os.path.dirname(self.exe_path),
                startupinfo=startupinfo
            )

            stdout, stderr = process.communicate()

            # Clean up the temporary input directory
            shutil.rmtree(temp_input_dir)

            # Check if the process was successful
            if process.returncode != 0:
                # Log errors and emit failure
                with open('conversion_log.txt', 'a', encoding='utf-8') as log_file:
                    log_file.write(f"Error processing batch:\n")
                    if stdout:
                        log_file.write("Standard Output:\n")
                        log_file.write(stdout)
                    if stderr:
                        log_file.write("\nStandard Error:\n")
                        log_file.write(stderr)
                self.conversion_done.emit(False)
                return  # Exit the thread on failure

            # If the batch was processed successfully
            self.conversion_done.emit(True)

        except Exception as e:
            # Clean up the temporary input directory in case of exception
            shutil.rmtree(temp_input_dir, ignore_errors=True)
            with open('conversion_log.txt', 'a', encoding='utf-8') as log_file:
                log_file.write(f"\nAn exception occurred: {e}\n")
            print(f"An exception occurred: {e}")
            self.conversion_done.emit(False)

class ImageConverterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IIQ to JPG Converter")
        self.setFixedSize(600, 280)  # Adjusted height for additional labels

        # Paths
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        # Paths to the external executable and dest folder
        self.exe_path = os.path.join(base_path, 'net6.0', 'imageSDK4023.exe')
        self.dest_path = os.path.join(base_path, 'dest')

        # Batch processing variables
        self.batch_size = 5  # Adjust the batch size as needed
        self.batches = []
        self.current_batch_index = 0
        self.processed_files = 0
        self.total_files = 0
        self.start_time = None

        # UI Elements
        self.input_dir_edit = QLineEdit()
        self.output_dir_edit = QLineEdit()
        self.start_button = QPushButton("Start Conversion")
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)

        # Additional Labels
        self.progress_label = QLabel("Processed 0 out of 0 files")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.status_label = QLabel("Status: Ready")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.init_ui()

    def init_ui(self):
        # Input Directory
        input_label = QLabel("Input Folder:")
        input_browse = QPushButton("Browse")
        input_browse.clicked.connect(self.browse_input_folder)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_dir_edit)
        input_layout.addWidget(input_browse)

        # Output Directory
        output_label = QLabel("Output Folder:")
        output_browse = QPushButton("Browse")
        output_browse.clicked.connect(self.browse_output_folder)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(output_browse)

        # Start Button
        self.start_button.clicked.connect(self.start_conversion)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(input_label)
        layout.addLayout(input_layout)
        layout.addWidget(output_label)
        layout.addLayout(output_layout)
        # If you have a batch size input, include it here
        # layout.addLayout(batch_size_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_label)
        # layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def browse_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_dir_edit.setText(folder)

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_dir_edit.setText(folder)

    def start_conversion(self):
        input_dir = self.input_dir_edit.text()
        output_dir = self.output_dir_edit.text()

        if not os.path.isdir(input_dir):
            QMessageBox.critical(self, "Error", "Invalid input folder.")
            return
        if not os.path.isdir(output_dir):
            QMessageBox.critical(self, "Error", "Invalid output folder.")
            return

        # Get list of input files
        self.input_files = [
            os.path.join(input_dir, f)
            for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ]

        self.total_files = len(self.input_files)

        if self.total_files == 0:
            QMessageBox.warning(self, "Warning", "No files found in the input folder.")
            return

        # Disable UI elements
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)

        # Initialize progress variables
        self.processed_files = 0
        self.progress_label.setText(f"Processed 0 out of {self.total_files} files")
        self.status_label.setText("Status: Starting conversion...")
        self.start_time = time.time()

        # Divide input files into batches
        self.batches = [
            self.input_files[i:i + self.batch_size]
            for i in range(0, self.total_files, self.batch_size)
        ]
        self.current_batch_index = 0

        # Start processing the first batch
        self.process_next_batch()

    def process_next_batch(self):
        if self.current_batch_index < len(self.batches):
            batch = self.batches[self.current_batch_index]
            self.current_batch_index += 1

            # Update status label to indicate a new batch is being created
            self.status_label.setText("Status: Creating new batch")

            # Update status label to indicate the batch is being processed
            self.status_label.setText(f"Status: Processing {len(batch)} files in batch {self.current_batch_index}")

            # Start conversion thread for the current batch
            self.thread = ConverterThread(self.exe_path, batch, self.output_dir_edit.text())
            self.thread.conversion_done.connect(self.batch_conversion_finished)
            self.thread.start()
        else:
            # All batches processed
            self.conversion_finished(True)

    def batch_conversion_finished(self, success):
        if success:
            # Update processed files count
            self.processed_files += len(self.batches[self.current_batch_index - 1])
            # Update progress bar and labels
            self.update_progress()
            # Update status label
            self.status_label.setText("Status: Batch completed")
            # Process the next batch
            self.process_next_batch()
        else:
            # Handle failure
            self.status_label.setText("Status: Batch failed")
            self.conversion_finished(False)

    def update_progress(self):
        if self.total_files == 0:
            progress = 0
        else:
            progress = int((self.processed_files / self.total_files) * 100)

        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Processed {self.processed_files} out of {self.total_files} files")

        if self.processed_files >= self.total_files:
            self.progress_bar.setValue(100)

    def conversion_finished(self, success):
        if success:
            self.status_label.setText("Status: Conversion completed")
            QMessageBox.information(self, "Success", "Conversion completed successfully.")
            self.progress_bar.setValue(100)
            self.progress_label.setText(f"Processed {self.total_files} out of {self.total_files} files")
        else:
            self.status_label.setText("Status: Conversion failed")
            QMessageBox.warning(self, "Failure", "Conversion failed. Check 'conversion_log.txt' for details.")
        self.start_button.setEnabled(True)

# Dark theme stylesheet (unchanged)
dark_stylesheet = """
QWidget {
    background-color: #2b2b2b;
    color: #d3d3d3;
}

QLineEdit {
    background-color: #3c3f41;
    color: #ffffff;
    border: 1px solid #555555;
}

QPushButton {
    background-color: #3c3f41;
    color: #d3d3d3;
    border: 1px solid #555555;
    padding: 5px;
}

QPushButton:hover {
    background-color: #4c4f51;
}

QPushButton:pressed {
    background-color: #2b2b2b;
}

QLabel {
    color: #d3d3d3;
}

QProgressBar {
    text-align: center;
    color: #ffffff;
    border: 1px solid #555555;
    background-color: #3c3f41;
}

QProgressBar::chunk {
    background-color: #d76262;
}

QMessageBox {
    background-color: #2b2b2b;
    color: #d3d3d3;
}

QScrollBar:vertical, QScrollBar:horizontal {
    background-color: #2b2b2b;
    width: 16px;
}

QScrollBar::handle {
    background-color: #3c3f41;
    border: 1px solid #555555;
}

QScrollBar::handle:hover {
    background-color: #4c4f51;
}
"""

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(dark_stylesheet)
    window = ImageConverterGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
