"""
WalletIQ — Login / Register screen.
Two-tab form centered on screen with username, password (+ email for register).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QMessageBox, QSizePolicy, QSpacerItem,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from frontend import theme


class LoginView(QWidget):
    login_success = pyqtSignal(dict)  # emits user data on success

    def __init__(self, api_client, parent=None, dark=False):
        super().__init__(parent)
        self._api = api_client
        self._dark = dark

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QWidget()
        container.setFixedWidth(400)
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.CARD_BG_DARK if dark else theme.CARD_BG_LIGHT};
                border: 1px solid {theme.BORDER_MUTED_DARK if dark else theme.BORDER_MUTED_LIGHT};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Brand
        brand = QLabel("🪙 WalletIQ")
        brand.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setStyleSheet("border: none;")
        layout.addWidget(brand)

        subtitle = QLabel("Intelligent Personal Finance Tracker")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; border: none; opacity: 0.7;")
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        # Tabs
        tabs = QTabWidget()

        # ── Login Tab ──
        login_tab = QWidget()
        login_layout = QVBoxLayout(login_tab)
        login_layout.setSpacing(12)

        self._login_user = QLineEdit()
        self._login_user.setPlaceholderText("Username")
        self._login_pass = QLineEdit()
        self._login_pass.setPlaceholderText("Password")
        self._login_pass.setEchoMode(QLineEdit.EchoMode.Password)

        login_btn = QPushButton("Login")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self._do_login)
        self._login_pass.returnPressed.connect(self._do_login)

        self._login_status = QLabel("")
        self._login_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._login_status.setStyleSheet("color: red; font-size: 12px; border: none;")

        login_layout.addWidget(self._login_user)
        login_layout.addWidget(self._login_pass)
        login_layout.addWidget(login_btn)
        login_layout.addWidget(self._login_status)
        login_layout.addStretch()

        # ── Register Tab ──
        reg_tab = QWidget()
        reg_layout = QVBoxLayout(reg_tab)
        reg_layout.setSpacing(12)

        self._reg_user = QLineEdit()
        self._reg_user.setPlaceholderText("Username")
        self._reg_email = QLineEdit()
        self._reg_email.setPlaceholderText("Email (optional)")
        self._reg_pass = QLineEdit()
        self._reg_pass.setPlaceholderText("Password")
        self._reg_pass.setEchoMode(QLineEdit.EchoMode.Password)

        reg_btn = QPushButton("Register")
        reg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reg_btn.clicked.connect(self._do_register)
        self._reg_pass.returnPressed.connect(self._do_register)

        self._reg_status = QLabel("")
        self._reg_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._reg_status.setStyleSheet("color: red; font-size: 12px; border: none;")

        reg_layout.addWidget(self._reg_user)
        reg_layout.addWidget(self._reg_email)
        reg_layout.addWidget(self._reg_pass)
        reg_layout.addWidget(reg_btn)
        reg_layout.addWidget(self._reg_status)
        reg_layout.addStretch()

        tabs.addTab(login_tab, "Login")
        tabs.addTab(reg_tab, "Register")
        layout.addWidget(tabs)

        outer.addWidget(container)

    def _do_login(self):
        user = self._login_user.text().strip()
        pw = self._login_pass.text().strip()
        if not user or not pw:
            self._login_status.setText("Please enter username and password")
            return
        self._login_status.setText("Logging in...")
        code, data = self._api.login(user, pw)
        if code == 200:
            self._login_status.setText("")
            self.login_success.emit(data.get("user", {}))
        else:
            err = data.get("error", data.get("non_field_errors", ["Login failed"])) if isinstance(data, dict) else str(data)
            if isinstance(err, list):
                err = err[0]
            self._login_status.setText(str(err))

    def _do_register(self):
        user = self._reg_user.text().strip()
        email = self._reg_email.text().strip()
        pw = self._reg_pass.text().strip()
        if not user or not pw:
            self._reg_status.setText("Username and password required")
            return
        self._reg_status.setText("Registering...")
        code, data = self._api.register(user, pw, email)
        if code == 201:
            self._reg_status.setText("")
            self.login_success.emit(data.get("user", {}))
        else:
            if isinstance(data, dict):
                errors = []
                for k, v in data.items():
                    if isinstance(v, list):
                        errors.extend(v)
                    else:
                        errors.append(str(v))
                err = "; ".join(errors) if errors else "Registration failed"
            else:
                err = str(data)
            self._reg_status.setText(err)
