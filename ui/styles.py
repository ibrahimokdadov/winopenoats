DARK_THEME = """
/* ── Base ─────────────────────────────────────────────────────── */
QWidget {
    background-color: #0d1117;
    color: #dde1f0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

/* ── Buttons ───────────────────────────────────────────────────── */
QPushButton {
    background-color: #161c2d;
    border: 1px solid #252d45;
    border-radius: 6px;
    padding: 7px 16px;
    color: #7880a0;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #1e2640;
    border-color: #374060;
    color: #dde1f0;
}
QPushButton:pressed { background-color: #111827; }

/* Record — primary pill button */
QPushButton#record_btn {
    background-color: #111827;
    border: 1px solid #252d45;
    border-radius: 18px;
    padding: 10px 28px;
    color: #7880a0;
    font-size: 13px;
    font-weight: 600;
    min-width: 130px;
}
QPushButton#record_btn:hover {
    background-color: #1e2640;
    border-color: #374060;
    color: #dde1f0;
}
QPushButton#record_btn:checked {
    background-color: #450a0a;
    border: 1px solid #dc2626;
    color: #fca5a5;
}
QPushButton#record_btn:checked:hover { background-color: #5c0e0e; }

/* ── Labels ────────────────────────────────────────────────────── */
QLabel {
    color: #dde1f0;
    background-color: transparent;
}
QLabel#section_header {
    color: #2e3655;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    background-color: transparent;
}

/* ── Inputs ────────────────────────────────────────────────────── */
QLineEdit {
    background-color: #111827;
    border: 1px solid #1e2a40;
    border-radius: 6px;
    padding: 8px 12px;
    color: #dde1f0;
    selection-background-color: #3730a3;
}
QLineEdit:focus { border-color: #4f46e5; }

QTextEdit {
    background-color: #0a0e19;
    border: 1px solid #1e2a40;
    border-radius: 6px;
    color: #dde1f0;
    padding: 8px;
}

QComboBox {
    background-color: #111827;
    border: 1px solid #1e2a40;
    border-radius: 6px;
    padding: 7px 12px;
    color: #dde1f0;
}
QComboBox:hover { border-color: #374060; }
QComboBox QAbstractItemView {
    background-color: #161c2d;
    color: #dde1f0;
    border: 1px solid #252d45;
    selection-background-color: #312e81;
    outline: none;
}

/* ── Scroll ────────────────────────────────────────────────────── */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    background-color: transparent;
    width: 5px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #1e2a40;
    border-radius: 2px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background-color: #374060; }
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical { background: transparent; }

/* ── Tabs ──────────────────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #1e2438;
    background-color: #0d1117;
    top: -1px;
}
QTabBar::tab {
    background-color: transparent;
    color: #3d4468;
    padding: 9px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 12px;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: #dde1f0;
    border-bottom: 2px solid #6366f1;
}
QTabBar::tab:hover:!selected { color: #7880a0; }

/* ── Checkbox ──────────────────────────────────────────────────── */
QCheckBox { color: #8890a8; spacing: 8px; }
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border: 1px solid #252d45;
    border-radius: 4px;
    background-color: #111827;
}
QCheckBox::indicator:checked {
    background-color: #4f46e5;
    border-color: #4f46e5;
}

/* ── Suggestion cards ──────────────────────────────────────────── */
QFrame#suggestion_card {
    background-color: #0f1520;
    border-top: 1px solid #1e2a40;
    border-right: 1px solid #1e2a40;
    border-bottom: 1px solid #1e2a40;
    border-left: 3px solid #6366f1;
    border-radius: 6px;
}

/* ── Separator ─────────────────────────────────────────────────── */
QFrame[frameShape="4"] {
    color: #141c2e;
    background-color: #141c2e;
    border: none;
    max-height: 1px;
}

/* ── Dialogs ───────────────────────────────────────────────────── */
QDialog { background-color: #0d1117; }
"""
