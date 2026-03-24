DARK_THEME = """
/* ── Base ─────────────────────────────────────────────────────── */
QWidget {
    background-color: #f7f6f3;
    color: #1c1a17;
    font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
    font-size: 13px;
}

/* ── Buttons ───────────────────────────────────────────────────── */
QPushButton {
    background-color: #ffffff;
    border: 1px solid #e2ddd6;
    border-radius: 6px;
    padding: 7px 16px;
    color: #6b6059;
    font-size: 12px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #f2f0ec;
    border-color: #cec8c0;
    color: #1c1a17;
}
QPushButton:pressed { background-color: #e8e4de; }

/* Settings — compact icon button */
QPushButton#settings_btn {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 0;
    color: #c5bdb3;
    font-size: 15px;
}
QPushButton#settings_btn:hover {
    background-color: #edeae5;
    border-color: #ddd8d0;
    color: #6b6059;
}
QPushButton#settings_btn:pressed { background-color: #e2ddd6; }

/* Notes — secondary ghost button */
QPushButton#notes_btn {
    background-color: transparent;
    border: 1px solid #e2ddd6;
    border-radius: 6px;
    padding: 7px 14px;
    color: #8b7e72;
    font-size: 12px;
    font-weight: 400;
}
QPushButton#notes_btn:hover {
    background-color: #f2f0ec;
    border-color: #cec8c0;
    color: #1c1a17;
}
QPushButton#notes_btn:pressed { background-color: #e8e4de; }

/* Record — primary pill */
QPushButton#record_btn {
    background-color: #ffffff;
    border: 1.5px solid #e2ddd6;
    border-radius: 20px;
    padding: 10px 28px;
    color: #6b6059;
    font-size: 13px;
    font-weight: 600;
    min-width: 136px;
}
QPushButton#record_btn:hover {
    background-color: #f2f0ec;
    border-color: #cec8c0;
    color: #1c1a17;
}
QPushButton#record_btn:checked {
    background-color: #fff5f5;
    border: 1.5px solid #fca5a5;
    color: #dc2626;
}
QPushButton#record_btn:checked:hover { background-color: #fee2e2; }

/* ── Labels ────────────────────────────────────────────────────── */
QLabel {
    color: #1c1a17;
    background-color: transparent;
}
QLabel#section_header {
    color: #c5bdb3;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2.5px;
    background-color: transparent;
}

/* ── Inputs ────────────────────────────────────────────────────── */
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #e2ddd6;
    border-radius: 8px;
    padding: 7px 12px;
    color: #1c1a17;
    selection-background-color: #a7f3e8;
}
QLineEdit:focus { border-color: #0d9488; }
QLineEdit:focus { outline: none; }

QTextEdit {
    background-color: #ffffff;
    border: 1px solid #e2ddd6;
    border-radius: 8px;
    color: #1c1a17;
    padding: 10px;
    selection-background-color: #a7f3e8;
}
QTextEdit:focus { border-color: #0d9488; }

QComboBox {
    background-color: #ffffff;
    border: 1px solid #e2ddd6;
    border-radius: 6px;
    padding: 7px 12px;
    color: #1c1a17;
}
QComboBox:hover { border-color: #cec8c0; }
QComboBox:focus { border-color: #0d9488; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1c1a17;
    border: 1px solid #e2ddd6;
    selection-background-color: #e6f5f3;
    outline: none;
}

/* ── Scroll ────────────────────────────────────────────────────── */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    background-color: transparent;
    width: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #e2ddd6;
    border-radius: 2px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background-color: #cec8c0; }
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical { background: transparent; }

/* ── Tabs ──────────────────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #e2ddd6;
    background-color: #ffffff;
    top: -1px;
}
QTabBar::tab {
    background-color: transparent;
    color: #c5bdb3;
    padding: 9px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 12px;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: #1c1a17;
    border-bottom: 2px solid #0d9488;
}
QTabBar::tab:hover:!selected { color: #8b7e72; }

/* ── Checkbox ──────────────────────────────────────────────────── */
QCheckBox { color: #6b6059; spacing: 8px; }
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border: 1.5px solid #e2ddd6;
    border-radius: 4px;
    background-color: #ffffff;
}
QCheckBox::indicator:checked {
    background-color: #0d9488;
    border-color: #0d9488;
}
QCheckBox::indicator:hover { border-color: #0d9488; }

/* ── Suggestion cards ──────────────────────────────────────────── */
QFrame#suggestion_card {
    background-color: #ffffff;
    border-top: 1px solid #ede8e1;
    border-right: 1px solid #ede8e1;
    border-bottom: 1px solid #ede8e1;
    border-left: 3px solid #0d9488;
    border-radius: 8px;
}

/* ── Separator ─────────────────────────────────────────────────── */
QFrame[frameShape="4"] {
    color: #ede8e1;
    background-color: #ede8e1;
    border: none;
    max-height: 1px;
}

/* ── Dialogs ───────────────────────────────────────────────────── */
QDialog { background-color: #f7f6f3; }

/* ── List Widget ───────────────────────────────────────────────── */
QListWidget {
    border: none;
    background-color: #f2f0ec;
    outline: none;
}
QListWidget::item {
    padding: 10px 14px;
    border-bottom: 1px solid #e8e3db;
    color: #1c1a17;
}
QListWidget::item:selected {
    background-color: #e6f5f3;
    border-left: 3px solid #0d9488;
    color: #1c1a17;
}
QListWidget::item:hover:!selected {
    background-color: #edeae5;
}

/* ── Splitter ──────────────────────────────────────────────────── */
QSplitter::handle { background-color: #e2ddd6; }
"""
