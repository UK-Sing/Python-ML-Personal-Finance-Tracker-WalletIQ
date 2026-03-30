"""
WalletIQ — Read-only terminal panel showing API activity in real-time.
Logs curl command, response JSON, and timing for every API call.
"""
import json
import time
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from frontend import theme


class TerminalPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._collapsed = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        header = QHBoxLayout()
        header.setContentsMargins(8, 4, 8, 4)

        title = QLabel("⬛ API Terminal")
        title.setStyleSheet(f"color: {theme.TERMINAL_FG}; font-weight: bold; font-size: 12px; border: none; background: {theme.TERMINAL_BG};")
        header.addWidget(title)
        header.addStretch()

        self._toggle_btn = QPushButton("▼ Collapse")
        self._toggle_btn.setFixedHeight(24)
        self._toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {theme.TERMINAL_FG};
                border: 1px solid {theme.TERMINAL_FG}44; border-radius: 4px;
                font-size: 11px; padding: 2px 8px;
            }}
            QPushButton:hover {{ background: {theme.TERMINAL_FG}22; }}
        """)
        self._toggle_btn.clicked.connect(self._toggle)
        header.addWidget(self._toggle_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedHeight(24)
        clear_btn.setStyleSheet(self._toggle_btn.styleSheet())
        clear_btn.clicked.connect(self._clear)
        header.addWidget(clear_btn)

        header_widget = QWidget()
        header_widget.setLayout(header)
        header_widget.setStyleSheet(f"background: {theme.TERMINAL_BG}; border-bottom: 1px solid #333;")
        layout.addWidget(header_widget)

        # Terminal output
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setFont(QFont("Cascadia Code", 11) if QFont("Cascadia Code").exactMatch() else QFont("Consolas", 11))
        self._output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme.TERMINAL_BG};
                color: {theme.TERMINAL_FG};
                border: none;
                padding: 8px;
            }}
        """)
        self._output.setMinimumHeight(120)
        self._output.setMaximumHeight(250)
        layout.addWidget(self._output)

    def _toggle(self):
        self._collapsed = not self._collapsed
        self._output.setVisible(not self._collapsed)
        self._toggle_btn.setText("▲ Expand" if self._collapsed else "▼ Collapse")

    def _clear(self):
        self._output.clear()

    def log_request(self, data: dict):
        """Log an API request/response entry from api_client signal."""
        method = data.get("method", "GET")
        url = data.get("url", "")
        headers = data.get("headers", {})
        body = data.get("body")
        response = data.get("response")
        status_code = data.get("status_code", 0)
        duration = data.get("duration_ms", 0)
        now = datetime.now().strftime("%H:%M:%S")

        lines = [f"─── {now} ───────────────────────────────────"]
        curl = f"$ curl -X {method} {url}"
        for k, v in headers.items():
            if k.lower() == "content-type":
                curl += f' \\\n  -H "{k}: {v}"'
            elif k.lower() == "authorization":
                token_preview = v[:16] + "..." if len(v) > 16 else v
                curl += f' \\\n  -H "Authorization: {token_preview}"'
        if body:
            curl += f" \\\n  -d '{json.dumps(body)}'"
        lines.append(curl)
        lines.append("")

        status_text = "OK" if 200 <= status_code < 300 else "ERROR"
        lines.append(f"← {status_code} {status_text} ({duration}ms)")

        if isinstance(response, (dict, list)):
            resp_str = json.dumps(response, indent=2)
            if len(resp_str) > 600:
                resp_str = resp_str[:600] + "\n  ..."
            lines.append(resp_str)
        elif response:
            lines.append(str(response)[:600])

        lines.append("─" * 50)
        lines.append("")

        self._output.append("\n".join(lines))
        # Auto-scroll to bottom
        cursor = self._output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._output.setTextCursor(cursor)
