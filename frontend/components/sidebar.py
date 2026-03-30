"""
Navigation sidebar — fixed left, icon + label, accent bar on active item, theme toggle at bottom.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont
from frontend import theme


NAV_ITEMS = [
    ("📊", "Dashboard"),
    ("💳", "Transactions"),
    ("🎯", "Budgets"),
    ("🧠", "Insights"),
]


class SidebarButton(QPushButton):
    def __init__(self, icon_text, label, parent=None):
        super().__init__(f"  {icon_text}  {label}", parent)
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._active = False

    def set_active(self, active: bool, dark: bool = False):
        self._active = active
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme.ACCENT1};
                    color: white;
                    text-align: left;
                    padding-left: 16px;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 600;
                }}
            """)
        else:
            text_color = theme.TEXT_DARK if dark else theme.TEXT_LIGHT
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color};
                    text-align: left;
                    padding-left: 16px;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {theme.ACCENT1}22;
                }}
            """)


class Sidebar(QWidget):
    nav_clicked = pyqtSignal(int)  # index of nav item
    theme_toggled = pyqtSignal()
    logout_clicked = pyqtSignal()

    def __init__(self, parent=None, dark=False):
        super().__init__(parent)
        self._dark = dark
        self.setFixedWidth(200)
        self._buttons: list[SidebarButton] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        # Logo / brand
        brand = QLabel("🪙 WalletIQ")
        brand.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet("border: none; margin-bottom: 12px;")
        layout.addWidget(brand)

        # Nav items
        for idx, (icon, label) in enumerate(NAV_ITEMS):
            btn = SidebarButton(icon, label, self)
            btn.clicked.connect(lambda checked, i=idx: self._on_click(i))
            self._buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Theme toggle
        self._theme_btn = QPushButton("🌙  Dark Mode")
        self._theme_btn.setFixedHeight(38)
        self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.clicked.connect(self.theme_toggled.emit)
        layout.addWidget(self._theme_btn)

        # Logout button
        self._logout_btn = QPushButton("🚪  Logout")
        self._logout_btn.setObjectName("warning")
        self._logout_btn.setFixedHeight(38)
        self._logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._logout_btn.clicked.connect(self.logout_clicked.emit)
        layout.addWidget(self._logout_btn)

        self.set_active(0)
        self.apply_theme(dark)

    def _on_click(self, index: int):
        self.set_active(index)
        self.nav_clicked.emit(index)

    def set_active(self, index: int):
        for i, btn in enumerate(self._buttons):
            btn.set_active(i == index, self._dark)

    def apply_theme(self, dark: bool):
        self._dark = dark
        bg = theme.SIDEBAR_BG_DARK if dark else theme.SIDEBAR_BG_LIGHT
        self.setStyleSheet(f"Sidebar {{ background-color: {bg}; border-right: 1px solid {theme.BORDER_MUTED_DARK if dark else theme.BORDER_MUTED_LIGHT}; }}")
        self._theme_btn.setText("☀️  Light Mode" if dark else "🌙  Dark Mode")
        theme_btn_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.TEXT_DARK if dark else theme.TEXT_LIGHT};
                border: 1px solid {theme.BORDER_MUTED_DARK if dark else theme.BORDER_MUTED_LIGHT};
                border-radius: 8px;
                font-size: 13px;
                padding: 6px;
            }}
            QPushButton:hover {{ background-color: {theme.ACCENT1}22; }}
        """
        self._theme_btn.setStyleSheet(theme_btn_style)
        for i, btn in enumerate(self._buttons):
            btn.set_active(btn._active, dark)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(0)
        shadow.setOffset(2, 0)
        shadow.setColor(QColor(0, 0, 0, 51))
        self.setGraphicsEffect(shadow)
