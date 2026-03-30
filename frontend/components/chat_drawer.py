"""
WalletIQ — AI Coach chat drawer overlay.
Slides in from the right side, accessible from any view via floating button.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QFont
from frontend import theme


class ChatBubble(QLabel):
    def __init__(self, text: str, is_user: bool, dark: bool = False, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.setMaximumWidth(260)
        if is_user:
            bg = theme.ACCENT1
            fg = "white"
            align = "right"
            radius = "12px 12px 2px 12px"
        else:
            bg = theme.CARD_BG_DARK if dark else theme.SECONDARY
            fg = theme.TEXT_DARK if dark else theme.TEXT_LIGHT
            align = "left"
            radius = "12px 12px 12px 2px"
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg}; color: {fg};
                padding: 10px 14px; border-radius: {radius};
                font-size: 13px; border: none;
            }}
        """)


class ChatDrawer(QWidget):
    """Right-side overlay chat drawer."""
    closed = pyqtSignal()

    def __init__(self, api_client, parent=None, dark=False):
        super().__init__(parent)
        self._api = api_client
        self._dark = dark
        self._messages = []  # list of (text, is_user)
        self.setFixedWidth(360)
        self.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QHBoxLayout()
        header.setContentsMargins(16, 12, 16, 12)
        title = QLabel("🤖 AI Coach")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("border: none;")
        header.addWidget(title)
        header.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {theme.TEXT_DARK if dark else theme.TEXT_LIGHT};
                font-size: 16px; border: none; border-radius: 16px;
            }}
            QPushButton:hover {{ background: #ff000033; }}
        """)
        close_btn.clicked.connect(self.hide_drawer)
        header.addWidget(close_btn)
        header_w = QWidget()
        header_w.setLayout(header)
        layout.addWidget(header_w)

        # Scroll area for messages
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { border: none; }")

        self._msg_container = QWidget()
        self._msg_layout = QVBoxLayout(self._msg_container)
        self._msg_layout.setContentsMargins(12, 8, 12, 8)
        self._msg_layout.setSpacing(8)
        self._msg_layout.addStretch()
        self._scroll.setWidget(self._msg_container)
        layout.addWidget(self._scroll, 1)

        # Input bar
        input_bar = QHBoxLayout()
        input_bar.setContentsMargins(12, 8, 12, 12)
        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask WalletIQ anything...")
        self._input.setFixedHeight(40)
        self._input.returnPressed.connect(self._send)
        input_bar.addWidget(self._input, 1)

        send_btn = QPushButton("➤")
        send_btn.setFixedSize(40, 40)
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        send_btn.clicked.connect(self._send)
        input_bar.addWidget(send_btn)

        input_w = QWidget()
        input_w.setLayout(input_bar)
        layout.addWidget(input_w)

        self.apply_theme(dark)

    def apply_theme(self, dark: bool):
        self._dark = dark
        bg = theme.CARD_BG_DARK if dark else theme.CARD_BG_LIGHT
        border = theme.BORDER_MUTED_DARK if dark else theme.BORDER_MUTED_LIGHT
        self.setStyleSheet(f"""
            ChatDrawer {{
                background-color: {bg};
                border-left: 1px solid {border};
            }}
        """)

    def show_drawer(self):
        self.setVisible(True)
        self.raise_()

    def hide_drawer(self):
        self.setVisible(False)
        self.closed.emit()

    def _add_bubble(self, text: str, is_user: bool):
        self._messages.append((text, is_user))
        bubble = ChatBubble(text, is_user, self._dark)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        if is_user:
            row.addStretch()
            row.addWidget(bubble)
        else:
            row.addWidget(bubble)
            row.addStretch()
        wrapper = QWidget()
        wrapper.setLayout(row)
        # Insert before the stretch
        count = self._msg_layout.count()
        self._msg_layout.insertWidget(count - 1, wrapper)
        # Scroll to bottom
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))

    def _send(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._add_bubble(text, is_user=True)

        code, data = self._api.chat(text)
        if code == 200:
            reply = data.get("reply", data.get("response", str(data)))
            self._add_bubble(str(reply), is_user=False)
        else:
            err = data.get("error", "Something went wrong") if isinstance(data, dict) else str(data)
            self._add_bubble(f"⚠ {err}", is_user=False)
