"""
Main application window with professional dark mode UI.
"""

import os
import json
from datetime import datetime

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QFileDialog, QMessageBox, QStatusBar,
    QGroupBox, QSplitter, QProgressBar, QFrame, QApplication,
    QLineEdit, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

from app import __version__, __app_name__
from app.templates import DEVICE_TEMPLATES, get_template
from app.generators.excel_generator import generate_excel_template, parse_excel_file
from app.generators.yaml_generator import generate_yaml, generate_full_config_yaml
from app.utils.validators import validate_device_data, validate_tags_data, validate_bundling_data
from app.utils.logger import setup_logger
from app.widgets.drag_drop import DragDropWidget
from app.widgets.yaml_preview import YamlPreviewWidget


# Application-wide dark theme stylesheet
DARK_STYLESHEET = """
QMainWindow {
    background-color: #121212;
}
QWidget {
    background-color: #121212;
    color: #E0E0E0;
    font-family: "Segoe UI", sans-serif;
}
QGroupBox {
    border: 1px solid #333333;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 20px;
    font-size: 13px;
    font-weight: bold;
    color: #BBBBBB;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}
QComboBox {
    background-color: #1E1E1E;
    border: 1px solid #444444;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #E0E0E0;
    min-height: 20px;
}
QComboBox:hover {
    border-color: #0078D4;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox QAbstractItemView {
    background-color: #2D2D2D;
    border: 1px solid #444444;
    color: #E0E0E0;
    selection-background-color: #0078D4;
}
QLineEdit {
    background-color: #1E1E1E;
    border: 1px solid #444444;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #E0E0E0;
}
QLineEdit:focus {
    border-color: #0078D4;
}
QPushButton {
    background-color: #0078D4;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
    min-width: 140px;
}
QPushButton:hover {
    background-color: #1A8CE0;
}
QPushButton:pressed {
    background-color: #005A9E;
}
QPushButton:disabled {
    background-color: #333333;
    color: #666666;
}
QPushButton#btnSecondary {
    background-color: #2D2D2D;
    border: 1px solid #555555;
    color: #CCCCCC;
}
QPushButton#btnSecondary:hover {
    background-color: #3D3D3D;
    border-color: #0078D4;
}
QPushButton#btnSuccess {
    background-color: #107C10;
}
QPushButton#btnSuccess:hover {
    background-color: #139413;
}
QPushButton#btnWarning {
    background-color: #CA5010;
}
QPushButton#btnWarning:hover {
    background-color: #E05C12;
}
QStatusBar {
    background-color: #1A1A1A;
    color: #888888;
    border-top: 1px solid #333333;
    font-size: 12px;
}
QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #333333;
    text-align: center;
    color: white;
    font-size: 11px;
    max-height: 6px;
}
QProgressBar::chunk {
    background-color: #0078D4;
    border-radius: 4px;
}
QSplitter::handle {
    background-color: #333333;
    width: 2px;
}
QLabel#titleLabel {
    font-size: 22px;
    font-weight: bold;
    color: #FFFFFF;
}
QLabel#subtitleLabel {
    font-size: 12px;
    color: #888888;
}
QTextEdit {
    background-color: #1E1E1E;
    color: #D4D4D4;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 8px;
    font-family: "Consolas", monospace;
    font-size: 11px;
}
"""


class ProcessingThread(QThread):
    """Background thread for Excel parsing and YAML generation."""
    finished = pyqtSignal(str, str)  # yaml_output, full_config_output
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, template, file_path):
        super().__init__()
        self.template = template
        self.file_path = file_path

    def run(self):
        try:
            self.progress.emit(20)
            device_data, tags_data, bundling_data = parse_excel_file(self.file_path)

            self.progress.emit(40)
            # Validate
            valid, errors = validate_device_data(self.template, device_data)
            if not valid:
                self.error.emit("Validation Errors:\n" + "\n".join(errors))
                return

            self.progress.emit(50)
            valid, errors = validate_tags_data(self.template, tags_data)
            if not valid:
                self.error.emit("Validation Errors:\n" + "\n".join(errors))
                return

            self.progress.emit(60)
            available_tags = [str(t.get("Tag Name", "")).strip() for t in tags_data if t.get("Tag Name")]
            valid, errors = validate_bundling_data(bundling_data, available_tags)
            if not valid:
                self.error.emit("Validation Warnings:\n" + "\n".join(errors))
                # Continue with warnings for bundling

            self.progress.emit(80)
            yaml_output = generate_yaml(self.template, device_data, tags_data, bundling_data)
            full_config = generate_full_config_yaml(self.template, device_data, tags_data, bundling_data)

            self.progress.emit(100)
            self.finished.emit(yaml_output, full_config)

        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.logger = setup_logger()
        self.logger.info("Application started")
        self.current_yaml = ""
        self.current_full_config = ""
        self.uploaded_file_path = ""
        self._setup_ui()
        self._connect_signals()
        self._load_recent()

    def _setup_ui(self):
        self.setWindowTitle(f"{__app_name__} v{__version__}")
        self.setMinimumSize(1100, 750)
        self.resize(1300, 850)
        self.setStyleSheet(DARK_STYLESHEET)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 20, 24, 16)

        # Title section
        title_layout = QHBoxLayout()
        title_label = QLabel(__app_name__)
        title_label.setObjectName("titleLabel")
        subtitle_label = QLabel(f"v{__version__} | Generate device YAML configurations from Excel templates")
        subtitle_label.setObjectName("subtitleLabel")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(subtitle_label)
        main_layout.addLayout(title_layout)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #333333; max-height: 1px;")
        main_layout.addWidget(sep)

        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Configuration
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(0, 0, 8, 0)

        # Device Selection Group
        device_group = QGroupBox("Device Selection")
        device_layout = QVBoxLayout(device_group)

        # Search/filter
        self.device_search = QLineEdit()
        self.device_search.setPlaceholderText("Search device types...")
        device_layout.addWidget(self.device_search)

        # Combo box
        self.device_combo = QComboBox()
        self.device_combo.addItem("-- Select Device Type --")
        for name in sorted(DEVICE_TEMPLATES.keys()):
            self.device_combo.addItem(name)
        device_layout.addWidget(self.device_combo)

        left_layout.addWidget(device_group)

        # Actions Group
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(10)

        self.btn_download_template = QPushButton("⬇  Download Excel Template")
        self.btn_download_template.setEnabled(False)
        actions_layout.addWidget(self.btn_download_template)

        # Separator
        actions_layout.addWidget(self._make_separator())

        # Upload section
        self.drag_drop = DragDropWidget()
        actions_layout.addWidget(self.drag_drop)

        self.btn_upload_excel = QPushButton("📂  Upload Filled Excel")
        self.btn_upload_excel.setObjectName("btnSecondary")
        self.btn_upload_excel.setEnabled(False)
        actions_layout.addWidget(self.btn_upload_excel)

        # Separator
        actions_layout.addWidget(self._make_separator())

        self.btn_generate = QPushButton("⚡  Generate YAML")
        self.btn_generate.setObjectName("btnSuccess")
        self.btn_generate.setEnabled(False)
        actions_layout.addWidget(self.btn_generate)

        left_layout.addWidget(actions_group)

        # Output options
        output_group = QGroupBox("Output Options")
        output_layout = QVBoxLayout(output_group)

        self.btn_download_yaml = QPushButton("💾  Download YAML")
        self.btn_download_yaml.setObjectName("btnSuccess")
        self.btn_download_yaml.setEnabled(False)
        output_layout.addWidget(self.btn_download_yaml)

        self.btn_download_full = QPushButton("📦  Download Full Config (values.yaml)")
        self.btn_download_full.setObjectName("btnSecondary")
        self.btn_download_full.setEnabled(False)
        output_layout.addWidget(self.btn_download_full)

        self.btn_copy_yaml = QPushButton("📋  Copy YAML to Clipboard")
        self.btn_copy_yaml.setObjectName("btnSecondary")
        self.btn_copy_yaml.setEnabled(False)
        output_layout.addWidget(self.btn_copy_yaml)

        left_layout.addWidget(output_group)
        left_layout.addStretch()

        # Right panel - YAML Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(8)
        right_layout.setContentsMargins(8, 0, 0, 0)

        preview_label = QLabel("YAML Preview")
        preview_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #BBBBBB;")
        right_layout.addWidget(preview_label)

        self.yaml_preview = YamlPreviewWidget()
        self.yaml_preview.setPlaceholderText(
            "Generated YAML will appear here...\n\n"
            "Steps:\n"
            "1. Select a device type\n"
            "2. Download the Excel template\n"
            "3. Fill in the template with your device configuration\n"
            "4. Upload the filled Excel file\n"
            "5. Click 'Generate YAML'"
        )
        right_layout.addWidget(self.yaml_preview)

        # Validation log area
        log_label = QLabel("Validation Log")
        log_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #888888;")
        right_layout.addWidget(log_label)

        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(120)
        self.log_area.setReadOnly(True)
        self.log_area.setPlaceholderText("Validation messages will appear here...")
        right_layout.addWidget(self.log_area)

        # Add to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready | Select a device type to begin")

    def _make_separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #2A2A2A; max-height: 1px;")
        return sep

    def _connect_signals(self):
        self.device_combo.currentIndexChanged.connect(self._on_device_selected)
        self.device_search.textChanged.connect(self._filter_devices)
        self.btn_download_template.clicked.connect(self._download_template)
        self.btn_upload_excel.clicked.connect(self._upload_excel)
        self.btn_generate.clicked.connect(self._generate_yaml)
        self.btn_download_yaml.clicked.connect(self._download_yaml)
        self.btn_download_full.clicked.connect(self._download_full_config)
        self.btn_copy_yaml.clicked.connect(self._copy_to_clipboard)
        self.drag_drop.file_dropped.connect(self._on_file_dropped)

    def _filter_devices(self, text: str):
        """Filter device types based on search text."""
        self.device_combo.clear()
        self.device_combo.addItem("-- Select Device Type --")
        search = text.strip().lower()
        for name in sorted(DEVICE_TEMPLATES.keys()):
            if not search or search in name.lower():
                self.device_combo.addItem(name)

    def _on_device_selected(self, index: int):
        """Handle device type selection."""
        enabled = index > 0
        self.btn_download_template.setEnabled(enabled)
        self.btn_upload_excel.setEnabled(enabled)
        self.drag_drop.reset()
        self.uploaded_file_path = ""
        self.btn_generate.setEnabled(False)
        self.btn_download_yaml.setEnabled(False)
        self.btn_download_full.setEnabled(False)
        self.btn_copy_yaml.setEnabled(False)
        self.yaml_preview.clear()
        self.log_area.clear()

        if enabled:
            device_name = self.device_combo.currentText()
            self.status_bar.showMessage(f"Selected: {device_name} | Download template or upload filled Excel")
            self.logger.info(f"Device type selected: {device_name}")

    def _download_template(self):
        """Generate and save Excel template for selected device."""
        device_name = self.device_combo.currentText()
        if device_name == "-- Select Device Type --":
            return

        try:
            template = get_template(device_name)
            safe_name = device_name.replace(" ", "_").replace("(", "").replace(")", "")
            default_filename = f"{safe_name}_template.xlsx"

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Excel Template", default_filename,
                "Excel Files (*.xlsx)"
            )

            if file_path:
                generate_excel_template(template, file_path)
                self.status_bar.showMessage(f"✓ Template saved: {file_path}")
                self.logger.info(f"Template generated: {file_path}")
                self._show_notification("Template Downloaded",
                                        f"Excel template saved to:\n{file_path}", "success")

        except Exception as e:
            self.logger.error(f"Template generation failed: {e}")
            self._show_notification("Error", f"Failed to generate template:\n{e}", "error")

    def _upload_excel(self):
        """Open file dialog to upload filled Excel."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Upload Filled Excel", "",
            "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self._on_file_dropped(file_path)

    def _on_file_dropped(self, file_path: str):
        """Handle file drop or upload."""
        self.uploaded_file_path = file_path
        self.btn_generate.setEnabled(True)
        filename = os.path.basename(file_path)
        self.status_bar.showMessage(f"✓ File loaded: {filename} | Click 'Generate YAML'")
        self.logger.info(f"File uploaded: {file_path}")
        self.log_area.clear()
        self.log_area.append(f"[INFO] File loaded: {filename}")

    def _generate_yaml(self):
        """Parse Excel and generate YAML configuration."""
        device_name = self.device_combo.currentText()
        if device_name == "-- Select Device Type --" or not self.uploaded_file_path:
            return

        template = get_template(device_name)

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_generate.setEnabled(False)
        self.status_bar.showMessage("Processing...")

        # Run in background thread
        self._thread = ProcessingThread(template, self.uploaded_file_path)
        self._thread.progress.connect(self._on_progress)
        self._thread.finished.connect(self._on_generation_complete)
        self._thread.error.connect(self._on_generation_error)
        self._thread.start()

    def _on_progress(self, value: int):
        self.progress_bar.setValue(value)

    def _on_generation_complete(self, yaml_output: str, full_config: str):
        """Handle successful YAML generation."""
        self.current_yaml = yaml_output
        self.current_full_config = full_config

        self.yaml_preview.set_yaml(yaml_output)
        self.btn_download_yaml.setEnabled(True)
        self.btn_download_full.setEnabled(True)
        self.btn_copy_yaml.setEnabled(True)
        self.btn_generate.setEnabled(True)

        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("✓ YAML generated successfully!")
        self.log_area.append(f"[SUCCESS] YAML generated at {datetime.now().strftime('%H:%M:%S')}")
        self.logger.info("YAML generation completed successfully")

        self._save_recent()

    def _on_generation_error(self, error_msg: str):
        """Handle YAML generation errors."""
        self.progress_bar.setVisible(False)
        self.btn_generate.setEnabled(True)
        self.status_bar.showMessage("✗ Generation failed - see validation log")
        self.log_area.append(f"[ERROR] {error_msg}")
        self.logger.error(f"Generation failed: {error_msg}")
        self._show_notification("Generation Failed", error_msg, "error")

    def _download_yaml(self):
        """Save generated YAML to file."""
        if not self.current_yaml:
            return

        device_name = self.device_combo.currentText()
        safe_name = device_name.replace(" ", "_").replace("(", "").replace(")", "").lower()
        default_filename = f"{safe_name}_config.yaml"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save YAML Configuration", default_filename,
            "YAML Files (*.yaml *.yml)"
        )

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.current_yaml)
            self.status_bar.showMessage(f"✓ YAML saved: {file_path}")
            self.logger.info(f"YAML saved: {file_path}")
            self._show_notification("YAML Saved", f"Configuration saved to:\n{file_path}", "success")

    def _download_full_config(self):
        """Save full configdevices YAML (values.yaml format)."""
        if not self.current_full_config:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Full Configuration", "values.yaml",
            "YAML Files (*.yaml *.yml)"
        )

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.current_full_config)
            self.status_bar.showMessage(f"✓ Full config saved: {file_path}")
            self.logger.info(f"Full config saved: {file_path}")

    def _copy_to_clipboard(self):
        """Copy YAML to system clipboard."""
        if self.current_yaml:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_yaml)
            self.status_bar.showMessage("✓ YAML copied to clipboard")

    def _show_notification(self, title: str, message: str, msg_type: str = "info"):
        """Show a message box notification."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        if msg_type == "error":
            msg_box.setIcon(QMessageBox.Critical)
        elif msg_type == "success":
            msg_box.setIcon(QMessageBox.Information)
        else:
            msg_box.setIcon(QMessageBox.Information)

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QMessageBox QLabel {
                color: #E0E0E0;
                font-size: 13px;
            }
            QPushButton {
                min-width: 80px;
            }
        """)
        msg_box.exec_()

    def _save_recent(self):
        """Save recent project information."""
        recent_dir = os.path.join(os.path.expanduser("~"), ".device_yaml_generator")
        os.makedirs(recent_dir, exist_ok=True)
        recent_file = os.path.join(recent_dir, "recent.json")

        recent_data = {
            "last_device": self.device_combo.currentText(),
            "last_file": self.uploaded_file_path,
            "timestamp": datetime.now().isoformat(),
        }

        with open(recent_file, "w") as f:
            json.dump(recent_data, f, indent=2)

    def _load_recent(self):
        """Load recent project information."""
        recent_file = os.path.join(os.path.expanduser("~"), ".device_yaml_generator", "recent.json")
        if os.path.exists(recent_file):
            try:
                with open(recent_file, "r") as f:
                    data = json.load(f)
                last_device = data.get("last_device", "")
                idx = self.device_combo.findText(last_device)
                if idx >= 0:
                    self.device_combo.setCurrentIndex(idx)
            except (json.JSONDecodeError, IOError):
                pass
