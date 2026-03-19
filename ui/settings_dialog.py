from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFileDialog, QTabWidget, QWidget, QCheckBox
)
from app.settings import AppSettings


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(460)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # LLM tab
        llm_tab = QWidget()
        llm_layout = QVBoxLayout(llm_tab)
        llm_layout.addWidget(QLabel("LLM Provider"))
        self._llm_provider = QComboBox()
        self._llm_provider.addItems(["openrouter", "ollama"])
        self._llm_provider.setCurrentText(self.settings.llm_provider)
        llm_layout.addWidget(self._llm_provider)
        llm_layout.addWidget(QLabel("Model"))
        self._llm_model = QLineEdit(self.settings.llm_model)
        llm_layout.addWidget(self._llm_model)
        llm_layout.addWidget(QLabel("OpenRouter API Key"))
        self._openrouter_key = QLineEdit()
        self._openrouter_key.setEchoMode(QLineEdit.EchoMode.Password)
        self._openrouter_key.setPlaceholderText("sk-or-...")
        key = self.settings.get_secret("openrouter_api_key") or ""
        self._openrouter_key.setText(key)
        llm_layout.addWidget(self._openrouter_key)
        llm_layout.addWidget(QLabel("Ollama Base URL"))
        self._ollama_url = QLineEdit(self.settings.ollama_base_url)
        llm_layout.addWidget(self._ollama_url)
        llm_layout.addStretch()
        tabs.addTab(llm_tab, "LLM")

        # Transcription tab
        trans_tab = QWidget()
        trans_layout = QVBoxLayout(trans_tab)
        trans_layout.addWidget(QLabel("Whisper Model"))
        self._trans_model = QComboBox()
        self._trans_model.addItems(["tiny.en", "small.en", "medium.en", "large-v3"])
        self._trans_model.setCurrentText(self.settings.transcription_model)
        trans_layout.addWidget(self._trans_model)
        trans_layout.addStretch()
        tabs.addTab(trans_tab, "Transcription")

        # Knowledge Base tab
        kb_tab = QWidget()
        kb_layout = QVBoxLayout(kb_tab)
        kb_layout.addWidget(QLabel("Knowledge Base Folder"))
        kb_row = QHBoxLayout()
        self._kb_folder = QLineEdit(self.settings.kb_folder or "")
        self._kb_folder.setPlaceholderText("Select folder...")
        kb_row.addWidget(self._kb_folder)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_kb)
        kb_row.addWidget(browse_btn)
        kb_layout.addLayout(kb_row)
        kb_layout.addStretch()
        tabs.addTab(kb_tab, "Knowledge Base")

        # Privacy tab
        privacy_tab = QWidget()
        privacy_layout = QVBoxLayout(privacy_tab)
        self._hide_screen = QCheckBox("Hide window from screen capture")
        self._hide_screen.setChecked(self.settings.hide_from_screen_capture)
        privacy_layout.addWidget(self._hide_screen)
        privacy_layout.addStretch()
        tabs.addTab(privacy_tab, "Privacy")

        layout.addWidget(tabs)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _browse_kb(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Knowledge Base Folder")
        if folder:
            self._kb_folder.setText(folder)

    def _save(self):
        self.settings.llm_provider = self._llm_provider.currentText()
        self.settings.llm_model = self._llm_model.text()
        self.settings.ollama_base_url = self._ollama_url.text()
        self.settings.transcription_model = self._trans_model.currentText()
        self.settings.kb_folder = self._kb_folder.text() or None
        self.settings.hide_from_screen_capture = self._hide_screen.isChecked()
        self.settings.save()
        key = self._openrouter_key.text().strip()
        if key:
            self.settings.set_secret("openrouter_api_key", key)
        self.accept()
