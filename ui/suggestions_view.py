from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QLabel, QPushButton, QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from models.models import Suggestion


class SuggestionCard(QFrame):
    feedback_given = Signal(str, str)  # (suggestion_id, "positive"|"negative")

    def __init__(self, suggestion: Suggestion, parent=None):
        super().__init__(parent)
        self.setObjectName("suggestion_card")
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(14, 12, 12, 10)

        headline = QLabel(suggestion.headline)
        headline.setWordWrap(True)
        headline.setStyleSheet("font-weight: 600; font-size: 13px; color: #dde1f0;")
        layout.addWidget(headline)

        if suggestion.coaching:
            coaching = QLabel(suggestion.coaching)
            coaching.setWordWrap(True)
            coaching.setStyleSheet("color: #6370a0; font-size: 12px; line-height: 1.4;")
            layout.addWidget(coaching)

        bottom = QHBoxLayout()
        bottom.setSpacing(4)

        if suggestion.evidence:
            src = QLabel(f"📄 {suggestion.evidence[0].source_file}")
            src.setStyleSheet("color: #2e3655; font-size: 11px;")
            bottom.addWidget(src)
        bottom.addStretch()

        for emoji, polarity in [("↑", "positive"), ("↓", "negative")]:
            btn = QPushButton(emoji)
            btn.setFixedSize(24, 24)
            btn.setStyleSheet(
                "QPushButton { background-color: transparent; border: 1px solid #1e2a40; "
                "border-radius: 4px; color: #3d4468; font-size: 12px; padding: 0; }"
                "QPushButton:hover { background-color: #1e2640; color: #7880a0; }"
            )
            btn.clicked.connect(
                lambda _, sid=str(suggestion.id), p=polarity:
                    self.feedback_given.emit(sid, p)
            )
            bottom.addWidget(btn)

        layout.addLayout(bottom)


class SuggestionsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(0, 0, 0, 0)

        self._cards_layout = QVBoxLayout()
        self._cards_layout.setSpacing(6)
        layout.addLayout(self._cards_layout)

        # Placeholder shown when no suggestions yet
        self._empty = QLabel("Suggestions from your knowledge base will appear here")
        self._empty.setStyleSheet("color: #1e2640; font-size: 12px; padding: 8px 0;")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._empty)

    def add_suggestion(self, suggestion: Suggestion):
        self._empty.hide()
        card = SuggestionCard(suggestion)
        self._cards_layout.insertWidget(0, card)
        while self._cards_layout.count() > 3:
            item = self._cards_layout.takeAt(self._cards_layout.count() - 1)
            if item.widget():
                item.widget().deleteLater()

    def clear(self):
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._empty.show()
