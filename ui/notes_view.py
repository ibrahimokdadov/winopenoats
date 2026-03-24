from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton,
    QSplitter, QListWidget, QListWidgetItem, QTabWidget, QFrame
)
from PySide6.QtCore import Qt, Slot, QSize
from pathlib import Path
from datetime import datetime, timezone
from storage.session_store import SessionStore

_YOU_COLOR = "#0f766e"
_THEM_COLOR = "#7c3aed"


class NotesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Past Sessions")
        self.setMinimumSize(680, 520)
        self.setWindowFlags(Qt.WindowType.Window)

        self._session_dir: Path | None = None
        self._notes_dir: Path | None = None
        self._current_session_id: str | None = None

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Top accent strip ──────────────────────────────────────
        accent = QFrame()
        accent.setFixedHeight(2)
        accent.setStyleSheet(
            "background-color: qlineargradient("
            "x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #0f766e, stop:0.5 #0d9488, stop:1 #10b981);"
        )
        root.addWidget(accent)

        # ── Toolbar ───────────────────────────────────────────────
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(20, 14, 20, 14)
        toolbar.setSpacing(12)

        self._title_label = QLabel("PAST SESSIONS")
        self._title_label.setObjectName("section_header")
        toolbar.addWidget(self._title_label)
        toolbar.addStretch()

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.setFixedHeight(30)
        self._refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self._refresh_btn)

        root.addLayout(toolbar)

        # ── Divider ───────────────────────────────────────────────
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        root.addWidget(div)

        # ── Two-panel splitter ────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background-color: #e0e4f0; }")

        # Left panel — session list
        left_panel = QWidget()
        left_panel.setMinimumWidth(180)
        left_panel.setMaximumWidth(260)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self._session_list = QListWidget()
        self._session_list.setStyleSheet(
            "QListWidget {"
            "  border: none;"
            "  background-color: #f2f0ec;"
            "  outline: none;"
            "}"
            "QListWidget::item {"
            "  border-bottom: 1px solid #e8e3db;"
            "  padding: 10px 14px;"
            "  color: #1c1a17;"
            "}"
            "QListWidget::item:selected {"
            "  background-color: #e6f5f3;"
            "  border-left: 3px solid #0d9488;"
            "  color: #1c1a17;"
            "}"
            "QListWidget::item:hover:!selected {"
            "  background-color: #edeae5;"
            "}"
        )
        self._session_list.currentItemChanged.connect(self._on_session_selected)
        left_layout.addWidget(self._session_list)

        # Right panel — tabs
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)

        # Transcript tab
        self._transcript_edit = QTextEdit()
        self._transcript_edit.setReadOnly(True)
        self._transcript_edit.setPlaceholderText("Select a session to view its transcript…")
        self._transcript_edit.setStyleSheet(
            "QTextEdit { border: none; background-color: #ffffff; padding: 16px; font-family: Consolas, monospace; font-size: 12px; }"
        )
        self._tabs.addTab(self._transcript_edit, "Transcript")

        # Notes tab
        self._notes_edit = QTextEdit()
        self._notes_edit.setReadOnly(True)
        self._notes_edit.setPlaceholderText("No notes for this session yet…")
        self._notes_edit.setStyleSheet(
            "QTextEdit { border: none; background-color: #ffffff; padding: 16px; line-height: 1.6; }"
        )
        self._tabs.addTab(self._notes_edit, "Notes")

        right_layout.addWidget(self._tabs)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([180, 500])

        root.addWidget(splitter)

    # ── Public API ────────────────────────────────────────────────

    def set_session_dirs(self, session_dir: Path, notes_dir: Path) -> None:
        """Called from main_window to pass directory paths."""
        self._session_dir = session_dir
        self._notes_dir = notes_dir

    # Alias kept for back-compat if coordinator calls the old name
    def set_session_dir(self, session_dir: Path, notes_dir: Path) -> None:
        self.set_session_dirs(session_dir, notes_dir)

    @Slot()
    def refresh(self) -> None:
        """Re-scan session_dir and repopulate the session list."""
        self._session_list.blockSignals(True)
        self._session_list.clear()
        self._session_list.blockSignals(False)

        if self._session_dir is None:
            return

        sessions = SessionStore.load_sessions(self._session_dir)
        for meta in sessions:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, meta)
            item.setText(self._format_item_text(meta))
            self._session_list.addItem(item)

        # Re-select the previously selected session if it still exists
        if self._current_session_id:
            for i in range(self._session_list.count()):
                it = self._session_list.item(i)
                if it and it.data(Qt.ItemDataRole.UserRole).get("id") == self._current_session_id:
                    self._session_list.setCurrentItem(it)
                    break

    @Slot(QListWidgetItem, QListWidgetItem)
    def _on_session_selected(self, current: QListWidgetItem, _previous) -> None:
        if current is None:
            return
        meta = current.data(Qt.ItemDataRole.UserRole)
        if not meta:
            return
        session_id = meta.get("id", "")
        self._current_session_id = session_id

        # Load transcript
        self._transcript_edit.clear()
        if self._session_dir:
            records = SessionStore.load_session_transcript(self._session_dir, session_id)
            html_parts = []
            for rec in records:
                speaker = rec.get("speaker", "")
                text = rec.get("text", "")
                if speaker == "you":
                    color = _YOU_COLOR
                    tag = "YOU"
                else:
                    color = _THEM_COLOR
                    tag = "THEM"
                # Escape HTML entities in text
                safe_text = (
                    text.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                )
                html_parts.append(
                    f'<p style="margin:6px 0;">'
                    f'<span style="color:{color};font-weight:700;font-size:9px;'
                    f'letter-spacing:1.5px;">{tag}</span>'
                    f'<span style="color:#ddd8d0;">&nbsp;&nbsp;·&nbsp;&nbsp;</span>'
                    f'<span style="color:#1c1a17;">{safe_text}</span>'
                    f'</p>'
                )
            if html_parts:
                self._transcript_edit.setHtml("<br>".join(html_parts))
            else:
                self._transcript_edit.setPlaceholderText("No transcript records found.")

        # Load notes
        self._notes_edit.clear()
        if self._notes_dir:
            notes_text = SessionStore.load_session_notes(self._notes_dir, session_id)
            if notes_text:
                self._notes_edit.setPlainText(notes_text)

    @Slot(str)
    def append_chunk(self, chunk: str) -> None:
        """Append live-streamed notes text to the Notes tab (used by coordinator)."""
        # Switch to Notes tab so live streaming is visible
        self._tabs.setCurrentIndex(1)
        cursor = self._notes_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(chunk)
        self._notes_edit.setTextCursor(cursor)

    def show_and_raise(self) -> None:
        self.refresh()
        self.show()
        self.raise_()
        self.activateWindow()

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _format_item_text(meta: dict) -> str:
        title = meta.get("title") or "Untitled"
        utt_count = meta.get("utterance_count", 0)
        ts_raw = meta.get("timestamp", "")
        date_str = ""
        try:
            dt = datetime.fromisoformat(ts_raw)
            # Ensure we have a timezone-aware datetime for display
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            date_str = dt.strftime("%b %-d · %H:%M")
        except (ValueError, TypeError):
            date_str = ts_raw[:16] if ts_raw else ""

        utt_label = f"{utt_count} utt" if utt_count == 1 else f"{utt_count} utts"
        return f"{title} · {utt_label}\n{date_str}"
