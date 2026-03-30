"""
WalletIQ — Material 3 inspired theme with light/dark mode.
Earthy color palette, sharp shadows, 12px card radius, 8px button radius.
"""

# ── Color Tokens ──────────────────────────────────────────────────────────────
PRIMARY = "#BFC6C4"
SECONDARY = "#E8E2D8"
ACCENT1 = "#6F8F72"      # success / positive / primary buttons
ACCENT2 = "#F2A65A"      # warning / overspend / CTA
DARK_BG = "#1E1E1E"
LIGHT_BG = "#F5F3EF"
SHADOW = "#00000033"
BORDER_MUTED_LIGHT = "#D0CBC2"
BORDER_MUTED_DARK = "#3A3A3A"
TEXT_LIGHT = "#2C2C2C"
TEXT_DARK = "#E8E2D8"
CARD_BG_LIGHT = "#FFFFFF"
CARD_BG_DARK = "#2A2A2A"
SIDEBAR_BG_LIGHT = PRIMARY
SIDEBAR_BG_DARK = "#272727"
INPUT_BG_LIGHT = SECONDARY
INPUT_BG_DARK = "#333333"
TERMINAL_BG = "#0D0D0D"
TERMINAL_FG = "#00FF88"


def _common_qss():
    return """
        * { font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; }
        QToolTip { padding: 4px; border: 1px solid; border-radius: 4px; }
    """


def light_qss():
    return _common_qss() + f"""
        QMainWindow, QWidget#central {{
            background-color: {LIGHT_BG};
        }}
        QLabel {{
            color: {TEXT_LIGHT};
        }}
        QLineEdit, QTextEdit, QComboBox, QDateTimeEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {INPUT_BG_LIGHT};
            color: {TEXT_LIGHT};
            border: 1px solid {BORDER_MUTED_LIGHT};
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 2px solid {ACCENT1};
        }}
        QPushButton {{
            background-color: {ACCENT1};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #5E7D60;
        }}
        QPushButton:pressed {{
            background-color: #4D6C4F;
        }}
        QPushButton#outlined {{
            background-color: transparent;
            color: {ACCENT1};
            border: 2px solid {ACCENT1};
        }}
        QPushButton#outlined:hover {{
            background-color: {ACCENT1}22;
        }}
        QPushButton#warning {{
            background-color: {ACCENT2};
        }}
        QPushButton#warning:hover {{
            background-color: #E0944A;
        }}
        QTableWidget {{
            background-color: {CARD_BG_LIGHT};
            alternate-background-color: {SECONDARY};
            color: {TEXT_LIGHT};
            gridline-color: {BORDER_MUTED_LIGHT};
            border: 1px solid {BORDER_MUTED_LIGHT};
            border-radius: 12px;
            font-size: 13px;
        }}
        QTableWidget::item {{
            padding: 8px;
        }}
        QHeaderView::section {{
            background-color: {PRIMARY};
            color: {TEXT_LIGHT};
            font-weight: bold;
            padding: 8px;
            border: none;
        }}
        QScrollBar:vertical {{
            width: 8px;
            background: transparent;
        }}
        QScrollBar::handle:vertical {{
            background: {BORDER_MUTED_LIGHT};
            border-radius: 4px;
        }}
        QProgressBar {{
            background-color: {SECONDARY};
            border: 1px solid {BORDER_MUTED_LIGHT};
            border-radius: 6px;
            text-align: center;
            font-size: 12px;
            color: {TEXT_LIGHT};
        }}
        QProgressBar::chunk {{
            background-color: {ACCENT1};
            border-radius: 5px;
        }}
        QTabWidget::pane {{
            border: 1px solid {BORDER_MUTED_LIGHT};
            border-radius: 8px;
            background: {CARD_BG_LIGHT};
        }}
        QTabBar::tab {{
            background: {SECONDARY};
            color: {TEXT_LIGHT};
            padding: 10px 24px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 600;
        }}
        QTabBar::tab:selected {{
            background: {CARD_BG_LIGHT};
            color: {ACCENT1};
        }}
    """


def dark_qss():
    return _common_qss() + f"""
        QMainWindow, QWidget#central {{
            background-color: {DARK_BG};
        }}
        QLabel {{
            color: {TEXT_DARK};
        }}
        QLineEdit, QTextEdit, QComboBox, QDateTimeEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {INPUT_BG_DARK};
            color: {TEXT_DARK};
            border: 1px solid {BORDER_MUTED_DARK};
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 2px solid {ACCENT1};
        }}
        QPushButton {{
            background-color: {ACCENT1};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #5E7D60;
        }}
        QPushButton:pressed {{
            background-color: #4D6C4F;
        }}
        QPushButton#outlined {{
            background-color: transparent;
            color: {ACCENT1};
            border: 2px solid {ACCENT1};
        }}
        QPushButton#outlined:hover {{
            background-color: {ACCENT1}22;
        }}
        QPushButton#warning {{
            background-color: {ACCENT2};
        }}
        QPushButton#warning:hover {{
            background-color: #E0944A;
        }}
        QTableWidget {{
            background-color: {CARD_BG_DARK};
            alternate-background-color: #333333;
            color: {TEXT_DARK};
            gridline-color: {BORDER_MUTED_DARK};
            border: 1px solid {BORDER_MUTED_DARK};
            border-radius: 12px;
            font-size: 13px;
        }}
        QTableWidget::item {{
            padding: 8px;
        }}
        QHeaderView::section {{
            background-color: {SIDEBAR_BG_DARK};
            color: {TEXT_DARK};
            font-weight: bold;
            padding: 8px;
            border: none;
        }}
        QScrollBar:vertical {{
            width: 8px;
            background: transparent;
        }}
        QScrollBar::handle:vertical {{
            background: {BORDER_MUTED_DARK};
            border-radius: 4px;
        }}
        QProgressBar {{
            background-color: #333333;
            border: 1px solid {BORDER_MUTED_DARK};
            border-radius: 6px;
            text-align: center;
            font-size: 12px;
            color: {TEXT_DARK};
        }}
        QProgressBar::chunk {{
            background-color: {ACCENT1};
            border-radius: 5px;
        }}
        QTabWidget::pane {{
            border: 1px solid {BORDER_MUTED_DARK};
            border-radius: 8px;
            background: {CARD_BG_DARK};
        }}
        QTabBar::tab {{
            background: #333333;
            color: {TEXT_DARK};
            padding: 10px 24px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 600;
        }}
        QTabBar::tab:selected {{
            background: {CARD_BG_DARK};
            color: {ACCENT1};
        }}
    """
