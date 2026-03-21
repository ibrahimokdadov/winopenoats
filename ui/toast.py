from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import QTimer, Qt


class Toast(QLabel):
    _STYLES = {
        "info": (
            "background-color: #111827; border: 1px solid #252d45; "
            "border-left: 3px solid #6366f1; color: #a5b4fc;"
        ),
        "success": (
            "background-color: #052e16; border: 1px solid #14532d; "
            "border-left: 3px solid #22c55e; color: #86efac;"
        ),
        "warning": (
            "background-color: #1c1505; border: 1px solid #292005; "
            "border-left: 3px solid #f59e0b; color: #fcd34d;"
        ),
        "error": (
            "background-color: #1c0606; border: 1px solid #350a0a; "
            "border-left: 3px solid #ef4444; color: #fca5a5;"
        ),
    }

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.setWordWrap(True)
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_message(self, message: str, level: str = "info", duration_ms: int = 4000):
        self._timer.stop()
        style = self._STYLES.get(level, self._STYLES["info"])
        self.setStyleSheet(
            f"{style} border-radius: 6px; padding: 10px 16px; font-size: 13px;"
        )
        self.setText(message)
        self.adjustSize()
        if self.parent():
            parent_rect = self.parent().rect()
            self.setFixedWidth(min(420, parent_rect.width() - 48))
            self.adjustSize()
            x = (parent_rect.width() - self.width()) // 2
            y = parent_rect.height() - self.height() - 24
            self.move(x, y)
        self.show()
        self.raise_()
        self._timer.start(duration_ms)
