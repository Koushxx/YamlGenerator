"""
Drag and drop widget for Excel file upload.
"""

from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent


class DragDropWidget(QWidget):
    """Custom drag-and-drop area for uploading Excel files."""

    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("Drag & Drop Excel File Here\nor click 'Upload Excel' button")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #555555;
                border-radius: 12px;
                padding: 30px;
                color: #AAAAAA;
                font-size: 14px;
                background-color: #1E1E1E;
            }
        """)
        layout.addWidget(self.label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().endswith(('.xlsx', '.xls')):
                event.acceptProposedAction()
                self.label.setStyleSheet("""
                    QLabel {
                        border: 2px dashed #00AAFF;
                        border-radius: 12px;
                        padding: 30px;
                        color: #00AAFF;
                        font-size: 14px;
                        background-color: #1A2A3A;
                    }
                """)

    def dragLeaveEvent(self, event):
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #555555;
                border-radius: 12px;
                padding: 30px;
                color: #AAAAAA;
                font-size: 14px;
                background-color: #1E1E1E;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith(('.xlsx', '.xls')):
                self.file_dropped.emit(file_path)
                self.label.setText(f"✓ Loaded: {file_path.split('/')[-1].split(chr(92))[-1]}")
                self.label.setStyleSheet("""
                    QLabel {
                        border: 2px solid #00CC66;
                        border-radius: 12px;
                        padding: 30px;
                        color: #00CC66;
                        font-size: 14px;
                        background-color: #1A2E1A;
                    }
                """)

    def reset(self):
        """Reset widget to initial state."""
        self.label.setText("Drag & Drop Excel File Here\nor click 'Upload Excel' button")
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #555555;
                border-radius: 12px;
                padding: 30px;
                color: #AAAAAA;
                font-size: 14px;
                background-color: #1E1E1E;
            }
        """)
