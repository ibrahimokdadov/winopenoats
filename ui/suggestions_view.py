from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QLabel, QPushButton, QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import Signal
from models.models import Suggestion


class SuggestionCard(QFrame):
    feedback_given = Signal(str, str)  # (suggestion_id, "positive"|"negative")

    def __init__(self, suggestion: Suggestion, parent=None):
        super().__init__(parent)
        self.setObjectName("suggestion_card")
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        headline = QLabel(f"💡 {suggestion.headline}")
        headline.setWordWrap(True)
        headline.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(headline)

        if suggestion.coaching:
            coaching = QLabel(suggestion.coaching)
            coaching.setWordWrap(True)
            coaching.setStyleSheet("color: #aaa; font-size: 12px;")
            layout.addWidget(coaching)

        bottom = QHBoxLayout()
        if suggestion.evidence:
            src = QLabel(f"📄 {suggestion.evidence[0].source_file}")
            src.setStyleSheet("color: #666; font-size: 11px;")
            bottom.addWidget(src)
        bottom.addStretch()

        thumbs_up = QPushButton("👍")
        thumbs_up.setFixedSize(28, 28)
        thumbs_up.clicked.connect(lambda: self.feedback_given.emit(str(suggestion.id), "positive"))
        thumbs_down = QPushButton("👎")
        thumbs_down.setFixedSize(28, 28)
        thumbs_down.clicked.connect(lambda: self.feedback_given.emit(str(suggestion.id), "negative"))
        bottom.addWidget(thumbs_up)
        bottom.addWidget(thumbs_down)
        layout.addLayout(bottom)


class SuggestionsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("SUGGESTIONS")
        header.setObjectName("section_header")
        layout.addWidget(header)

        self._cards_layout = QVBoxLayout()
        self._cards_layout.setSpacing(6)
        layout.addLayout(self._cards_layout)

    def add_suggestion(self, suggestion: Suggestion):
        card = SuggestionCard(suggestion)
        self._cards_layout.insertWidget(0, card)
        # Keep max 3 suggestions visible
        while self._cards_layout.count() > 3:
            item = self._cards_layout.takeAt(self._cards_layout.count() - 1)
            if item.widget():
                item.widget().deleteLater()

    def clear(self):
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
