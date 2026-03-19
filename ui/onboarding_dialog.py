from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QHBoxLayout, QFileDialog, QCheckBox, QComboBox
)
from app.settings import AppSettings


class OnboardingDialog(QDialog):
    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Welcome to OpenOats")
        self.setMinimumWidth(440)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Welcome to OpenOats")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Let's get you set up. This takes about 2 minutes.")
        subtitle.setStyleSheet("color: #aaa;")
        layout.addWidget(subtitle)

        # Consent
        consent_label = QLabel("🎙 Recording Consent")
        consent_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(consent_label)
        self._consent = QCheckBox(
            "I acknowledge that this app will record microphone and system audio during sessions."
        )
        layout.addWidget(self._consent)

        # LLM
        llm_label = QLabel("🤖 LLM Provider")
        llm_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(llm_label)
        self._provider = QComboBox()
        self._provider.addItems(["openrouter", "ollama"])
        layout.addWidget(self._provider)
        self._api_key = QLineEdit()
        self._api_key.setPlaceholderText("OpenRouter API key (sk-or-...)")
        self._api_key.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._api_key)

        # KB folder
        kb_label = QLabel("📁 Knowledge Base (optional)")
        kb_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(kb_label)
        kb_row = QHBoxLayout()
        self._kb_folder = QLineEdit()
        self._kb_folder.setPlaceholderText("Skip for now...")
        kb_row.addWidget(self._kb_folder)
        browse = QPushButton("Browse")
        browse.clicked.connect(self._browse)
        kb_row.addWidget(browse)
        layout.addLayout(kb_row)

        # Whisper model
        model_label = QLabel("🗣 Transcription Model")
        model_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(model_label)
        self._model = QComboBox()
        self._model.addItems([
            "tiny.en (fast, ~75MB)",
            "small.en (balanced, ~244MB)",
            "medium.en (accurate, ~769MB)",
        ])
        self._model.setCurrentIndex(1)
        layout.addWidget(self._model)

        layout.addStretch()

        btn = QPushButton("Get Started")
        btn.clicked.connect(self._finish)
        layout.addWidget(btn)

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select KB Folder")
        if folder:
            self._kb_folder.setText(folder)

    def _finish(self):
        if not self._consent.isChecked():
            return
        self.settings.recording_consent_acknowledged = True
        self.settings.llm_provider = self._provider.currentText()
        kb = self._kb_folder.text().strip()
        if kb:
            self.settings.kb_folder = kb
        model_map = {0: "tiny.en", 1: "small.en", 2: "medium.en"}
        self.settings.transcription_model = model_map[self._model.currentIndex()]
        key = self._api_key.text().strip()
        if key:
            self.settings.set_secret("openrouter_api_key", key)
        self.settings.save()
        self.accept()
