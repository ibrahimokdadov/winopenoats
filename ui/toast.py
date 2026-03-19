from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import QTimer, Qt


class Toast(QLabel):
    COLORS = {
        "info": "#2d2d2d",
        "warning": "#7a5c00",
        "error": "#6b1a1a",
    }

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_message(self, message: str, level: str = "info", duration_ms: int = 4000):
        self._timer.stop()
        color = self.COLORS.get(level, self.COLORS["info"])
        self.setStyleSheet(
            f"background-color: {color}; border: 1px solid #555; "
            f"border-radius: 6px; padding: 8px 14px; color: #e0e0e0;"
        )
        self.setText(message)
        self.adjustSize()
        if self.parent():
            parent_rect = self.parent().rect()
            self.setFixedWidth(min(400, parent_rect.width() - 40))
            x = (parent_rect.width() - self.width()) // 2
            y = max(10, parent_rect.height() - self.height() - 20)
            self.move(x, y)
        self.show()
        self.raise_()
        self._timer.start(duration_ms)
