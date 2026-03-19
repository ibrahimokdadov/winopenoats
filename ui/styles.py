DARK_THEME = """
QWidget {
    background-color: #1a1a1a;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #444;
    border-radius: 6px;
    padding: 6px 14px;
    color: #e0e0e0;
}
QPushButton:hover { background-color: #3a3a3a; }
QPushButton:pressed { background-color: #222; }
QPushButton#record_btn {
    background-color: #c0392b;
    color: white;
    font-weight: bold;
}
QPushButton#record_btn:checked { background-color: #e74c3c; }
QLabel { color: #e0e0e0; }
QLabel#section_header {
    color: #888;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
}
QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
}
QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #e0e0e0;
    selection-background-color: #3a3a3a;
}
QScrollArea { border: none; }
QTextEdit {
    background-color: #1e1e1e;
    border: 1px solid #333;
    border-radius: 4px;
    color: #e0e0e0;
}
QLineEdit {
    background-color: #2d2d2d;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
}
QTabWidget::pane { border: 1px solid #333; }
QTabBar::tab {
    background-color: #2d2d2d;
    color: #aaa;
    padding: 6px 14px;
    border: 1px solid #333;
}
QTabBar::tab:selected { background-color: #1a1a1a; color: #e0e0e0; }
QCheckBox { color: #e0e0e0; }
QFrame#suggestion_card {
    background-color: #242424;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 10px;
}
"""
