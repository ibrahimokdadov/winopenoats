from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Slot


class NotesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("NOTES")
        title.setObjectName("section_header")
        header.addWidget(title)
        header.addStretch()
        self._generate_btn = QPushButton("Generate Notes")
        header.addWidget(self._generate_btn)
        layout.addLayout(header)

        self._status = QLabel("")
        self._status.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(self._status)

        self._text = QTextEdit()
        self._text.setReadOnly(True)
        self._text.setPlaceholderText("Notes will appear here after you stop recording...")
        layout.addWidget(self._text)

    @Slot(str)
    def append_chunk(self, chunk: str):
        cursor = self._text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(chunk)
        self._text.setTextCursor(cursor)

    def set_generating(self, generating: bool):
        self._generate_btn.setEnabled(not generating)
        self._status.setText("Generating..." if generating else "")

    def connect_generate(self, callback):
        self._generate_btn.clicked.connect(callback)
