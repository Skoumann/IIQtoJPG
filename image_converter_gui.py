import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QHBoxLayout, QVBoxLayout, QMessageBox, QFrame, QTextEdit, QScrollArea
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
        self.process = None

    def run(self):
        try:
            self.update_status.emit("Starting conversion...")
            command = [self.exe_path, self.input_dir, self.output_dir]

            # Suppress terminal on Windows
            startupinfo = None
            if os.name == 'nt':  # Only apply on Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                shell=False,  # Ensure shell is disabled
                cwd=os.path.dirname(self.exe_path),  # Set the correct working directory
                startupinfo=startupinfo  # Use startupinfo to suppress terminal
            )

            self.start_monitoring.emit()

            # Capture and emit process output line-by-line
            for line in self.process.stdout:
                self.update_status.emit(line.strip())

            # Wait for the process to complete and capture errors
            stdout, stderr = self.process.communicate()

            # Emit final status based on process return code
            success = self.process.returncode == 0
            if not success:
                self.update_status.emit(f"Process failed with return code {self.process.returncode}")
                if stderr:
                    self.update_status.emit(stderr.strip())
            self.conversion_done.emit(success)

        except Exception as e:
            self.update_status.emit(f"Error: {e}")
            self.conversion_done.emit(False)

    def terminate_process(self):
        """Terminate the external process and stop the thread."""
        if self.process and self.process.poll() is None:  # Check if the process is running
            self.process.terminate()  # Terminate the external process
            self.update_status.emit("Conversion process terminated.")
        self.quit()  # Stop the QThread
        self.wait()  # Wait for the thread to finish

class ImageConverterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IIQ to JPG Converter")
        self.setMinimumSize(600, 240)

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        self.exe_path = os.path.join(base_path, 'net6.0', 'imagesdk32105.exe')
        self.dest_path = os.path.join(base_path, 'dest')
        self.total_files = 0
        self.processed_files = 0
        self.thread = None
        self.monitor_timer = None  # Ensure monitor_timer is initialized

        self.input_dir_edit = QLineEdit()
        self.output_dir_edit = QLineEdit()
        self.start_button = QPushButton("Start Conversion")
        self.progress_label = QLabel("Processed 0 out of 0 files")
        self.status_label = QLabel("Status: Ready")

        self.console_frame = QFrame()
        self.console_frame.setFrameShape(QFrame.StyledPanel)
        self.console_frame.setVisible(False)

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)

        self.load_stylesheet()

        self.init_ui()

    def load_stylesheet(self):
        stylesheet_path = os.path.join(os.path.dirname(__file__), 'style.qss')
        if os.path.exists(stylesheet_path):
            with open(stylesheet_path, 'r') as f:
                stylesheet = f.read()
                QApplication.instance().setStyleSheet(stylesheet)

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

        self.start_button.clicked.connect(self.toggle_conversion)

        toggle_console_button = QPushButton("Toggle Console Output")
        toggle_console_button.clicked.connect(self.toggle_console_output)

        console_layout = QVBoxLayout()
        console_layout.addWidget(self.console_output)
        self.console_frame.setLayout(console_layout)

        layout = QVBoxLayout()
        layout.addWidget(input_label)
        layout.addLayout(input_layout)
        layout.addWidget(output_label)
        layout.addLayout(output_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(toggle_console_button)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.console_frame)

        self.setLayout(layout)
        self.center_window()

    def center_window(self):
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.primaryScreen().geometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def browse_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_dir_edit.setText(folder)

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_dir_edit.setText(folder)

    def toggle_conversion(self):
        if self.start_button.text() == "Start Conversion":
            self.start_conversion()
        else:
            self.cancel_conversion()

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
        self.start_button.setText("Cancel")

        self.thread = ConverterThread(self.exe_path, input_dir, output_dir, self.total_files)
        self.thread.conversion_done.connect(self.conversion_finished)
        self.thread.start_monitoring.connect(self.start_monitoring)
        self.thread.update_status.connect(self.update_status_label)
        self.thread.update_status.connect(self.append_console_output)
        self.thread.start()

    def cancel_conversion(self):
        if self.thread:
            self.thread.terminate_process()
            self.thread = None
        self.start_button.setText("Start Conversion")
        self.status_label.setText("Status: Canceled")

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
            if self.monitor_timer:
                self.monitor_timer.stop()

    def update_status_label(self, status):
        self.status_label.setText(f"Status: {status}")

    def append_console_output(self, text):
        self.console_output.append(text)

    def toggle_console_output(self):
        self.console_frame.setVisible(not self.console_frame.isVisible())
        if self.console_frame.isVisible():
            self.resize(self.width(), self.height() + 200)
        else:
            self.resize(self.width(), self.height() - 200)

    def conversion_finished(self, success):
        if self.monitor_timer:
            self.monitor_timer.stop()
        if success:
            QMessageBox.information(self, "Success", "Conversion completed successfully.")
            self.progress_label.setText(f"Processed {self.total_files} out of {self.total_files} files")
        else:
            QMessageBox.warning(self, "Stopped", "The Convertion have stopped.")
        self.start_button.setText("Start Conversion")

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.thread.terminate_process()  # Ensure the process is terminated
            self.thread.wait()              # Wait for the thread to finish
        if self.monitor_timer:
            self.monitor_timer.stop()
        event.accept()

def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = ImageConverterGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
