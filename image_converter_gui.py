import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QHBoxLayout, QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
import subprocess

class ConverterThread(QThread):
    conversion_done = pyqtSignal(bool)
    update_status = pyqtSignal(str)
    start_monitoring = pyqtSignal()

    def __init__(self, exe_path, input_dir, output_dir, total_files):
        super().__init__()
        self.exe_path = exe_path
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.total_files = total_files
        self.process = None  # Store the process here

    def run(self):
        try:
            self.update_status.emit("Eating the IIQ and making JPG...")
            command = [self.exe_path, self.input_dir, self.output_dir]
            print(f"Running command: {command}")

            is_windows = sys.platform.startswith('win')

            if is_windows:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            else:
                startupinfo = None

            # Start the process and store it
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                shell=False,
                cwd=os.path.dirname(self.exe_path),
                startupinfo=startupinfo
            )

            self.start_monitoring.emit()

            stdout, stderr = self.process.communicate()

            with open('conversion_log.txt', 'w', encoding='utf-8') as log_file:
                if stdout:
                    log_file.write("Standard Output:\n")
                    log_file.write(stdout)
                if stderr:
                    log_file.write("\nStandard Error:\n")
                    log_file.write(stderr)
                    print(stderr)

            success = self.process.returncode == 0
            self.conversion_done.emit(success)

        except Exception as e:
            with open('conversion_log.txt', 'a', encoding='utf-8') as log_file:
                log_file.write(f"\nAn exception occurred: {e}\n")
            print(f"An exception occurred: {e}")
            self.conversion_done.emit(False)

    def terminate_process(self):
        if self.process and self.process.poll() is None:
            print("Terminating imageSDK process...")
            self.process.terminate()

class ImageConverterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IIQ to JPG Converter")
        self.setFixedSize(600, 240)

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        self.exe_path = os.path.join(base_path, 'net6.0', 'imageSDK4028.exe')
        self.dest_path = os.path.join(base_path, 'dest')
        self.total_files = 0
        self.processed_files = 0
        self.thread = None

        self.input_dir_edit = QLineEdit()
        self.output_dir_edit = QLineEdit()
        self.start_button = QPushButton("Start Conversion")
        self.progress_label = QLabel("Processed 0 out of 0 files")
        self.status_label = QLabel("Status: Ready")

        self.init_ui()

    def init_ui(self):
        input_label = QLabel("Input Folder:")
        input_browse = QPushButton("Browse")
        input_browse.clicked.connect(self.browse_input_folder)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_dir_edit)
        input_layout.addWidget(input_browse)

        output_label = QLabel("Output Folder:")
        output_browse = QPushButton("Browse")
        output_browse.clicked.connect(self.browse_output_folder)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(output_browse)

        self.start_button.clicked.connect(self.start_conversion)

        layout = QVBoxLayout()
        layout.addWidget(input_label)
        layout.addLayout(input_layout)
        layout.addWidget(output_label)
        layout.addLayout(output_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_label)
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

        self.total_files = len([f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))])
        self.processed_files = 0

        if self.total_files == 0:
            QMessageBox.warning(self, "Warning", "No files found in the input folder.")
            return

        self.progress_label.setText(f"Processed {self.processed_files} out of {self.total_files} files")
        self.start_button.setEnabled(False)

        self.thread = ConverterThread(self.exe_path, input_dir, output_dir, self.total_files)
        self.thread.conversion_done.connect(self.conversion_finished)
        self.thread.start_monitoring.connect(self.start_monitoring)
        self.thread.update_status.connect(self.update_status_label)
        self.thread.start()

    def start_monitoring(self):
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_progress)
        self.monitor_timer.start(500)

    def update_progress(self):
        output_dir = self.output_dir_edit.text()
        if not os.path.isdir(output_dir):
            return

        output_files = len([f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))])
        self.processed_files = output_files
        self.progress_label.setText(f"Processed {self.processed_files} out of {self.total_files} files")

        if self.processed_files >= self.total_files:
            self.monitor_timer.stop()

    def update_status_label(self, status):
        self.status_label.setText(f"Status: {status}")

    def conversion_finished(self, success):
        self.monitor_timer.stop()
        if success:
            QMessageBox.information(self, "Success", "Conversion completed successfully.")
            self.progress_label.setText(f"Processed {self.total_files} out of {self.total_files} files")
        else:
            QMessageBox.warning(self, "Failure", "Conversion failed. Check 'conversion_log.txt' for details.")
        self.start_button.setEnabled(True)

    def closeEvent(self, event):
        if self.thread:
            self.thread.terminate_process()  # Terminate the running imageSDK process
        event.accept()

# Dark theme stylesheet
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
"""

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(dark_stylesheet)
    window = ImageConverterGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
