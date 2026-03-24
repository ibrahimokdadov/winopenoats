from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter
from PySide6.QtCore import Qt, QSize


def _make_icon(color: str) -> QIcon:
    """Draw a simple filled circle icon in the given color."""
    px = QPixmap(QSize(22, 22))
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 18, 18)
    painter.end()
    return QIcon(px)


_ICON_IDLE = _make_icon("#b0b8d8")      # grey — not recording
_ICON_REC  = _make_icon("#e11d48")      # red  — recording


class SystemTray(QSystemTrayIcon):
    def __init__(self, main_window, coordinator, parent=None):
        super().__init__(_ICON_IDLE, parent)
        self._win = main_window
        self._coordinator = coordinator
        self.setToolTip("OpenOats")
        self._build_menu()
        self._connect_signals()
        self.activated.connect(self._on_activated)
        self.show()

    def _build_menu(self):
        menu = QMenu()
        self._show_action = menu.addAction("Show OpenOats")
        self._show_action.triggered.connect(self._win.show)
        self._show_action.triggered.connect(self._win.raise_)
        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
        self.setContextMenu(menu)

    def _connect_signals(self):
        self._coordinator.session_started.connect(
            lambda: self.setIcon(_ICON_REC)
        )
        self._coordinator.session_ended.connect(
            lambda _: self.setIcon(_ICON_IDLE)
        )

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self._win.isVisible():
                self._win.hide()
            else:
                self._win.show()
                self._win.raise_()
                self._win.activateWindow()
