import asyncio
import ctypes
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QTimer, Slot
from app.coordinator import AppCoordinator
from ui.suggestions_view import SuggestionsView
from ui.toast import Toast
from models.models import Utterance, SessionIndex

_YOU_COLOR = "#34d399"   # emerald — mic speaker
_THEM_COLOR = "#60a5fa"  # sky blue — system speaker


class MainWindow(QMainWindow):
    def __init__(self, coordinator: AppCoordinator):
        super().__init__()
        self._coordinator = coordinator
        self.setWindowTitle("OpenOats")
        self.setMinimumSize(500, 680)
        self._build_ui()
        self._connect_signals()
        self._apply_screen_share_setting()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setSpacing(0)
        outer.setContentsMargins(0, 0, 0, 0)

        # ── Top accent strip (indigo → violet gradient) ──────────
        accent = QFrame()
        accent.setFixedHeight(2)
        accent.setStyleSheet(
            "background-color: qlineargradient("
            "x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #6366f1, stop:0.55 #8b5cf6, stop:1 #a855f7);"
        )
        outer.addWidget(accent)

        # ── Content area ─────────────────────────────────────────
        content = QWidget()
        root = QVBoxLayout(content)
        root.setSpacing(0)
        root.setContentsMargins(24, 18, 24, 16)
        outer.addWidget(content)

        # Header
        header = QHBoxLayout()
        title = QLabel("OpenOats")
        title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #dde1f0; letter-spacing: -0.3px;"
        )
        header.addWidget(title)
        header.addStretch()
        self._kb_label = QLabel("")
        self._kb_label.setStyleSheet("color: #2e3655; font-size: 11px;")
        header.addWidget(self._kb_label)
        root.addLayout(header)
        root.addSpacing(20)

        # Suggestions section
        suggestions_header = QLabel("SUGGESTIONS")
        suggestions_header.setObjectName("section_header")
        root.addWidget(suggestions_header)
        root.addSpacing(8)

        self._suggestions_view = SuggestionsView()
        root.addWidget(self._suggestions_view)
        root.addSpacing(16)

        # System audio warning banner
        self._sys_banner = QLabel("⚠  System audio unavailable — capturing mic only")
        self._sys_banner.setStyleSheet(
            "color: #b45309; background-color: #1c1505; "
            "border: 1px solid #292005; border-radius: 6px; "
            "padding: 6px 12px; font-size: 12px;"
        )
        self._sys_banner.hide()
        root.addWidget(self._sys_banner)

        # Transcript section
        root.addSpacing(4)
        transcript_header = QLabel("TRANSCRIPT")
        transcript_header.setObjectName("section_header")
        root.addWidget(transcript_header)
        root.addSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent;")
        self._transcript_widget = QWidget()
        self._transcript_widget.setStyleSheet("background-color: transparent;")
        self._transcript_layout = QVBoxLayout(self._transcript_widget)
        self._transcript_layout.setSpacing(2)
        self._transcript_layout.setContentsMargins(0, 0, 0, 0)

        # Empty state
        self._transcript_empty = QLabel("Transcript will appear here once you start recording")
        self._transcript_empty.setStyleSheet(
            "color: #1e2640; font-size: 13px; padding: 32px 0;"
        )
        self._transcript_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._transcript_layout.addWidget(self._transcript_empty)
        self._transcript_layout.addStretch()
        scroll.setWidget(self._transcript_widget)
        root.addWidget(scroll)
        root.addSpacing(12)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(sep)
        root.addSpacing(10)

        # Control bar
        controls = QHBoxLayout()
        controls.setSpacing(12)

        self._record_btn = QPushButton("⏺  Record")
        self._record_btn.setObjectName("record_btn")
        self._record_btn.setCheckable(True)
        self._record_btn.clicked.connect(self._toggle_recording)
        controls.addWidget(self._record_btn)
        controls.addStretch()

        self._you_level = QLabel()
        self._you_level.setTextFormat(Qt.TextFormat.RichText)
        self._you_level.setStyleSheet("font-size: 12px;")
        self._them_level = QLabel()
        self._them_level.setTextFormat(Qt.TextFormat.RichText)
        self._them_level.setStyleSheet("font-size: 12px;")
        self._update_levels()  # set initial text

        controls.addWidget(self._you_level)
        controls.addWidget(self._them_level)
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
        c.session_started.connect(lambda: self._record_btn.setText("⏹  Stop"))
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
        if self._transcript_empty.isVisible():
            self._transcript_empty.hide()

        speaker = utterance.speaker
        color = _YOU_COLOR if speaker == "you" else _THEM_COLOR
        tag = "YOU" if speaker == "you" else "THEM"
        ts = utterance.timestamp.strftime("%H:%M")

        row = QHBoxLayout()
        row.setSpacing(0)
        row.setContentsMargins(0, 4, 0, 4)

        label = QLabel(
            f'<span style="color:{color};font-weight:700;font-size:10px;'
            f'letter-spacing:1px">{tag}</span>'
            f'<span style="color:#2e3655">&nbsp;&nbsp;·&nbsp;&nbsp;</span>'
            f'<span style="color:#b0b8d0">{utterance.text}</span>'
        )
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        time_label = QLabel(ts)
        time_label.setStyleSheet("color: #2e3655; font-size: 11px; padding-left: 8px;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        row.addWidget(label)
        row.addWidget(time_label)

        count = self._transcript_layout.count()
        self._transcript_layout.insertLayout(count - 1, row)

    @Slot(object)
    def _on_session_ended(self, index: SessionIndex):
        self._record_btn.setText("⏺  Record")
        self._record_btn.setChecked(False)
        self._toast.show_message(
            f"Session saved — {index.utterance_count} utterances", "success"
        )

    def _update_levels(self):
        def bar(rms, color):
            filled = int(min(rms * 20, 5))
            f = f'<span style="color:{color}">{"█" * filled}</span>'
            e = f'<span style="color:#1a2035">{"░" * (5 - filled)}</span>'
            return f + e

        mic = self._coordinator._mic.rms if hasattr(self._coordinator, "_mic") else 0
        sys = self._coordinator._sys.rms if hasattr(self._coordinator, "_sys") else 0

        self._you_level.setText(
            f'<span style="color:{_YOU_COLOR};font-size:10px;font-weight:700'
            f';letter-spacing:1px">YOU</span>'
            f'<span style="font-family:monospace"> {bar(mic, _YOU_COLOR)}</span>'
        )
        self._them_level.setText(
            f'<span style="color:{_THEM_COLOR};font-size:10px;font-weight:700'
            f';letter-spacing:1px">THEM</span>'
            f'<span style="font-family:monospace"> {bar(sys, _THEM_COLOR)}</span>'
        )

    def _apply_screen_share_setting(self):
        if self._coordinator.settings.hide_from_screen_capture:
            QTimer.singleShot(0, self._set_screen_affinity)

    def _set_screen_affinity(self):
        try:
            hwnd = int(self.winId())
            ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x00000011)
        except Exception:
            pass
