from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import QTimer, Qt


class Toast(QLabel):
    _STYLES = {
        "info": (
            "background-color: #f0fdfa; border: 1px solid #99f6e4; "
            "border-left: 3px solid #0d9488; color: #0f766e;"
        ),
        "success": (
            "background-color: #f0fdf4; border: 1px solid #bbf7d0; "
            "border-left: 3px solid #10b981; color: #065f46;"
        ),
        "warning": (
            "background-color: #fefce8; border: 1px solid #fde68a; "
            "border-left: 3px solid #f59e0b; color: #78350f;"
        ),
        "error": (
            "background-color: #fff5f5; border: 1px solid #fecaca; "
            "border-left: 3px solid #ef4444; color: #991b1b;"
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
