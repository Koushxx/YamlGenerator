"""
YAML preview widget with syntax highlighting.
"""

from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont
)


class YamlHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for YAML content."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rules = []

        # Key format (before colon)
        key_format = QTextCharFormat()
        key_format.setForeground(QColor("#569CD6"))
        key_format.setFontWeight(QFont.Bold)
        self._rules.append((QRegularExpression(r"^\s*[\w\-\.]+(?=\s*:)"), key_format))

        # String values (quoted)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self._rules.append((QRegularExpression(r'"[^"]*"'), string_format))
        self._rules.append((QRegularExpression(r"'[^']*'"), string_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self._rules.append((QRegularExpression(r"\b\d+\.?\d*\b"), number_format))

        # Booleans
        bool_format = QTextCharFormat()
        bool_format.setForeground(QColor("#569CD6"))
        self._rules.append((QRegularExpression(r"\b(true|false|null)\b"), bool_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self._rules.append((QRegularExpression(r"#.*$"), comment_format))

        # List dash
        dash_format = QTextCharFormat()
        dash_format.setForeground(QColor("#D4D4D4"))
        dash_format.setFontWeight(QFont.Bold)
        self._rules.append((QRegularExpression(r"^\s*-\s"), dash_format))

    def highlightBlock(self, text):
        for pattern, fmt in self._rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)


class YamlPreviewWidget(QPlainTextEdit):
    """Read-only YAML preview with syntax highlighting."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 11))
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 10px;
                selection-background-color: #264F78;
            }
        """)
        self._highlighter = YamlHighlighter(self.document())

    def set_yaml(self, yaml_text: str):
        """Set YAML content and apply highlighting."""
        self.setPlainText(yaml_text)
