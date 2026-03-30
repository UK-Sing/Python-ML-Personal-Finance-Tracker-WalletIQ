"""
Reusable M3-style card widget — solid background, 1px muted border, sharp drop shadow.
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from frontend import theme


class Card(QFrame):
    def __init__(self, parent=None, dark=False):
        super().__init__(parent)
        self._dark = dark
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(8)
        self.apply_theme(dark)

    def apply_theme(self, dark: bool):
        self._dark = dark
        bg = theme.CARD_BG_DARK if dark else theme.CARD_BG_LIGHT
        border = theme.BORDER_MUTED_DARK if dark else theme.BORDER_MUTED_LIGHT
        self.setStyleSheet(f"""
            Card {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(0)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 51))  # #00000033
        self.setGraphicsEffect(shadow)

    def layout(self):
        return self._layout
