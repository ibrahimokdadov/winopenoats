import asyncio
import ctypes
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QSizePolicy, QFrame, QLineEdit
)
from PySide6.QtCore import Qt, QTimer, Slot
from app.coordinator import AppCoordinator
from ui.suggestions_view import SuggestionsView
from ui.notes_view import NotesView
from ui.settings_dialog import SettingsDialog
from ui.toast import Toast
from models.models import Utterance, SessionIndex

_YOU_COLOR = "#0f766e"   # deep teal — mic speaker
_THEM_COLOR = "#7c3aed"  # violet — system speaker


class MainWindow(QMainWindow):
    def __init__(self, coordinator: AppCoordinator):
        super().__init__()
        self._coordinator = coordinator
        self.setWindowTitle("OpenOats")
        self.setMinimumSize(500, 680)
        self._transcript_rows: list[tuple[QHBoxLayout, str]] = []
        self._build_ui()
        self._connect_signals()
        self._apply_screen_share_setting()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        outer = QVBoxLayout(central)
        outer.setSpacing(0)
        outer.setContentsMargins(0, 0, 0, 0)

        # ── Top accent strip (teal → emerald) ───────────────────
        accent = QFrame()
        accent.setFixedHeight(3)
        accent.setStyleSheet(
            "background-color: qlineargradient("
            "x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #0f766e, stop:0.5 #0d9488, stop:1 #10b981);"
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
            "font-size: 15px; font-weight: 700; color: #1c1a17; letter-spacing: -0.2px;"
        )
        header.addWidget(title)
        header.addStretch()
        self._kb_label = QLabel("")
        self._kb_label.setStyleSheet("color: #c5bdb3; font-size: 11px;")
        header.addWidget(self._kb_label)

        self._settings_btn = QPushButton("⚙")
        self._settings_btn.setObjectName("settings_btn")
        self._settings_btn.setFixedSize(28, 28)
        self._settings_btn.setToolTip("Settings")
        self._settings_btn.clicked.connect(self._open_settings)
        header.addSpacing(8)
        header.addWidget(self._settings_btn)
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
            "color: #92400e; background-color: #fefce8; "
            "border: 1px solid #fde68a; border-radius: 6px; "
            "padding: 6px 12px; font-size: 12px;"
        )
        self._sys_banner.hide()
        root.addWidget(self._sys_banner)

        # Transcript section
        root.addSpacing(4)

        # Search bar
        search_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search transcript…")
        self._search_input.setClearButtonEnabled(True)
        self._search_input.textChanged.connect(self._filter_transcript)
        search_row.addWidget(self._search_input)
        root.addLayout(search_row)
        root.addSpacing(6)

        transcript_header = QLabel("TRANSCRIPT")
        transcript_header.setObjectName("section_header")
        root.addWidget(transcript_header)
        root.addSpacing(8)

        self._scroll = QScrollArea()
        scroll = self._scroll
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
            "color: #c5bdb3; font-size: 13px; padding: 40px 0;"
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

        self._mute_btn = QPushButton("Mute")
        self._mute_btn.setObjectName("mute_btn")
        self._mute_btn.setCheckable(True)
        self._mute_btn.setToolTip("Mute microphone")
        self._mute_btn.clicked.connect(self._toggle_mute)
        controls.addWidget(self._mute_btn)

        self._notes_btn = QPushButton("Notes")
        self._notes_btn.setObjectName("notes_btn")
        self._notes_btn.setToolTip("Open meeting notes")
        self._notes_btn.clicked.connect(self._open_notes)
        controls.addWidget(self._notes_btn)

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

        # Notes window (standalone, not parented to keep it as top-level)
        self._notes_window = NotesView()
        self._notes_window.set_session_dirs(
            self._coordinator.settings.session_dir,
            self._coordinator.settings.notes_dir,
        )

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
        c.session_started.connect(lambda: self._transcript_rows.clear())
        c.session_ended.connect(self._on_session_ended)
        c.suggestion_ready.connect(self._add_suggestion)
        c.notes_chunk_ready.connect(self._notes_window.append_chunk)

    def _add_suggestion(self, suggestion):
        from ui.suggestions_view import SuggestionCard
        self._suggestions_view.add_suggestion(suggestion)
        # Wire the freshly-inserted card's feedback_given signal to the coordinator
        if self._suggestions_view._cards_layout.count() > 0:
            item = self._suggestions_view._cards_layout.itemAt(0)
            if item and item.widget() and isinstance(item.widget(), SuggestionCard):
                card = item.widget()
                card.feedback_given.connect(self._coordinator.record_feedback)

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
            f'<span style="color:{color};font-weight:700;font-size:9px;'
            f'letter-spacing:1.5px">{tag}</span>'
            f'<span style="color:#ddd8d0">&nbsp;&nbsp;·&nbsp;&nbsp;</span>'
            f'<span style="color:#1c1a17;font-family:Consolas,monospace;font-size:12px">{utterance.text}</span>'
        )
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        time_label = QLabel(ts)
        time_label.setStyleSheet("color: #c5bdb3; font-size: 10px; padding-left: 8px; font-family: Consolas, monospace;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        row.addWidget(label)
        row.addWidget(time_label)

        count = self._transcript_layout.count()
        self._transcript_layout.insertLayout(count - 1, row)
        self._transcript_rows.append((row, utterance.text))
        QTimer.singleShot(0, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))

    @Slot(object)
    def _on_session_ended(self, index: SessionIndex):
        self._record_btn.setText("⏺  Record")
        self._record_btn.setChecked(False)
        self._toast.show_message(
            f"Session saved — {index.utterance_count} utterances", "success"
        )

    def _filter_transcript(self, query: str):
        for row_layout, plain_text in self._transcript_rows:
            if query == "" or query.lower() in plain_text.lower():
                visible = True
            else:
                visible = False
            for i in range(row_layout.count()):
                item = row_layout.itemAt(i)
                if item and item.widget():
                    item.widget().setVisible(visible)

    def _toggle_mute(self, checked: bool):
        self._coordinator._mic.muted = checked
        self._mute_btn.setText("Unmute" if checked else "Mute")

    def _open_notes(self):
        self._notes_window.show_and_raise()

    def _update_levels(self):
        def bar(rms, color):
            filled = int(min(rms * 20, 5))
            f = f'<span style="color:{color}">{"█" * filled}</span>'
            e = f'<span style="color:#e2ddd6">{"░" * (5 - filled)}</span>'
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

    def _open_settings(self):
        dlg = SettingsDialog(self._coordinator.settings, parent=self)
        dlg.exec()
        self._apply_screen_share_setting()

    def _apply_screen_share_setting(self):
        hide = self._coordinator.settings.hide_from_screen_capture
        QTimer.singleShot(0, lambda: self._set_screen_affinity(hide))

    def _set_screen_affinity(self, hide: bool):
        try:
            hwnd = int(self.winId())
            affinity = 0x00000011 if hide else 0x00000000
            ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, affinity)
        except Exception:
            pass
