import asyncio
import ctypes
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Slot
from app.coordinator import AppCoordinator
from ui.suggestions_view import SuggestionsView
from ui.toast import Toast
from models.models import Utterance, SessionIndex


class MainWindow(QMainWindow):
    def __init__(self, coordinator: AppCoordinator):
        super().__init__()
        self._coordinator = coordinator
        self.setWindowTitle("OpenOats")
        self.setMinimumSize(480, 640)
        self._build_ui()
        self._connect_signals()
        self._apply_screen_share_setting()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(0)
        root.setContentsMargins(16, 12, 16, 12)

        # Header
        header = QHBoxLayout()
        title = QLabel("OpenOats")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        self._kb_label = QLabel("")
        self._kb_label.setStyleSheet("color: #666; font-size: 11px;")
        header.addWidget(self._kb_label)
        root.addLayout(header)

        # Suggestions
        self._suggestions_view = SuggestionsView()
        root.addWidget(self._suggestions_view)

        # System audio banner
        self._sys_banner = QLabel("⚠ System audio capture unavailable — mic only")
        self._sys_banner.setStyleSheet("color: #f39c12; font-size: 11px; padding: 4px;")
        self._sys_banner.hide()
        root.addWidget(self._sys_banner)

        # Transcript
        transcript_header = QLabel("TRANSCRIPT")
        transcript_header.setObjectName("section_header")
        root.addWidget(transcript_header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._transcript_widget = QWidget()
        self._transcript_layout = QVBoxLayout(self._transcript_widget)
        self._transcript_layout.addStretch()
        scroll.setWidget(self._transcript_widget)
        root.addWidget(scroll)

        # Control bar
        controls = QHBoxLayout()
        self._record_btn = QPushButton("⏺ Record")
        self._record_btn.setObjectName("record_btn")
        self._record_btn.setCheckable(True)
        self._record_btn.clicked.connect(self._toggle_recording)
        controls.addWidget(self._record_btn)

        self._you_level = QLabel("You ░░░░░")
        self._them_level = QLabel("Them ░░░░░")
        controls.addWidget(self._you_level)
        controls.addWidget(self._them_level)
        controls.addStretch()
        root.addLayout(controls)

        # Toast overlay
        self._toast = Toast(central)

        # Audio level timer
        self._level_timer = QTimer(self)
        self._level_timer.setInterval(100)
        self._level_timer.timeout.connect(self._update_levels)

    def _connect_signals(self):
        c = self._coordinator
        c.toast_requested.connect(self._toast.show_message)
        c.system_audio_unavailable.connect(lambda: self._sys_banner.show())
        c.transcript_store.utterance_added.connect(self._add_utterance_row)
        c.session_started.connect(lambda: self._record_btn.setText("⏹ Stop"))
        c.session_ended.connect(self._on_session_ended)

    def _toggle_recording(self, checked: bool):
        if checked:
            asyncio.ensure_future(self._coordinator.start_session())
            self._level_timer.start()
        else:
            asyncio.ensure_future(self._coordinator.end_session())
            self._level_timer.stop()

    @Slot(object)
    def _add_utterance_row(self, utterance: Utterance):
        speaker = "You" if utterance.speaker == "you" else "Them"
        ts = utterance.timestamp.strftime("%H:%M")
        row = QHBoxLayout()
        label = QLabel(f'<b>{speaker}:</b> {utterance.text}')
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        time_label = QLabel(ts)
        time_label.setStyleSheet("color: #555; font-size: 11px;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        row.addWidget(label)
        row.addWidget(time_label)
        count = self._transcript_layout.count()
        self._transcript_layout.insertLayout(count - 1, row)

    @Slot(object)
    def _on_session_ended(self, index: SessionIndex):
        self._record_btn.setText("⏺ Record")
        self._record_btn.setChecked(False)
        self._toast.show_message(f"Session saved: {index.utterance_count} utterances", "info")

    def _update_levels(self):
        def bar(rms):
            filled = int(min(rms * 20, 5))
            return "█" * filled + "░" * (5 - filled)
        mic_rms = self._coordinator._mic.rms if hasattr(self._coordinator, '_mic') else 0
        sys_rms = self._coordinator._sys.rms if hasattr(self._coordinator, '_sys') else 0
        self._you_level.setText(f"You {bar(mic_rms)}")
        self._them_level.setText(f"Them {bar(sys_rms)}")

    def _apply_screen_share_setting(self):
        if self._coordinator.settings.hide_from_screen_capture:
            QTimer.singleShot(0, self._set_screen_affinity)

    def _set_screen_affinity(self):
        try:
            hwnd = int(self.winId())
            ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x00000011)
        except Exception:
            pass
