from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFileDialog, QTabWidget, QWidget, QCheckBox
)
import sounddevice as sd
from app.settings import AppSettings
from intelligence.templates import TEMPLATE_NAMES


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
        self._llm_provider.addItems(["openrouter", "ollama", "custom"])
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
        llm_layout.addWidget(QLabel("Custom Endpoint URL  (LM Studio, llama.cpp, LiteLLM…)"))
        self._custom_url = QLineEdit(self.settings.custom_base_url)
        self._custom_url.setPlaceholderText("http://localhost:1234/v1")
        llm_layout.addWidget(self._custom_url)
        llm_layout.addWidget(QLabel("Custom Model Name"))
        self._custom_model = QLineEdit(self.settings.custom_llm_model)
        self._custom_model.setPlaceholderText("local-model")
        llm_layout.addWidget(self._custom_model)
        llm_layout.addWidget(QLabel("Notes Template"))
        self._notes_template = QComboBox()
        self._notes_template.addItems(TEMPLATE_NAMES)
        current_tpl = self.settings.notes_template
        if current_tpl in TEMPLATE_NAMES:
            self._notes_template.setCurrentText(current_tpl)
        llm_layout.addWidget(self._notes_template)
        llm_layout.addStretch()
        tabs.addTab(llm_tab, "LLM")

        # Transcription tab
        trans_tab = QWidget()
        trans_layout = QVBoxLayout(trans_tab)
        trans_layout.addWidget(QLabel("Transcription Model"))
        self._trans_model = QComboBox()
        self._MODELS = [
            ("Parakeet TDT v2  (English, ~600 MB)",      "parakeet-tdt-0.6b-v2"),
            ("Parakeet TDT 1.1B  (Multilingual, ~1.1 GB)", "parakeet-tdt-1.1b"),
            ("Whisper Base  (~142 MB)",                   "base.en"),
            ("Whisper Small  (~244 MB)",                  "small.en"),
            ("Whisper Large v3 Turbo  (~800 MB)",          "large-v3-turbo"),
            ("Whisper Large v3  (~1.5 GB)",                "large-v3"),
        ]
        for label, _ in self._MODELS:
            self._trans_model.addItem(label)
        # select current
        current_ids = [m for _, m in self._MODELS]
        idx = current_ids.index(self.settings.transcription_model) \
            if self.settings.transcription_model in current_ids else 1
        self._trans_model.setCurrentIndex(idx)
        trans_layout.addWidget(self._trans_model)
        note = QLabel(
            "Model is downloaded on first use and cached locally.\n"
            "Parakeet models require: pip install nemo_toolkit[asr]"
        )
        note.setStyleSheet("color: #8b7e72; font-size: 11px;")
        note.setWordWrap(True)
        trans_layout.addWidget(note)

        trans_layout.addWidget(QLabel("Microphone"))
        self._input_device = QComboBox()
        self._input_device_indices: list[int | None] = [None]
        self._input_device.addItem("System Default")
        try:
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if dev["max_input_channels"] > 0:
                    self._input_device.addItem(dev["name"])
                    self._input_device_indices.append(i)
        except Exception:
            pass
        current_device = self.settings.input_device
        if current_device is not None and current_device in self._input_device_indices:
            self._input_device.setCurrentIndex(self._input_device_indices.index(current_device))
        else:
            self._input_device.setCurrentIndex(0)
        trans_layout.addWidget(self._input_device)

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
        self.settings.notes_template = self._notes_template.currentText()
        self.settings.custom_base_url = self._custom_url.text().strip() or "http://localhost:1234/v1"
        self.settings.custom_llm_model = self._custom_model.text().strip() or "local-model"
        self.settings.transcription_model = self._MODELS[self._trans_model.currentIndex()][1]
        self.settings.input_device = self._input_device_indices[self._input_device.currentIndex()]
        self.settings.kb_folder = self._kb_folder.text() or None
        self.settings.hide_from_screen_capture = self._hide_screen.isChecked()
        self.settings.save()
        key = self._openrouter_key.text().strip()
        if key:
            self.settings.set_secret("openrouter_api_key", key)
        self.accept()
