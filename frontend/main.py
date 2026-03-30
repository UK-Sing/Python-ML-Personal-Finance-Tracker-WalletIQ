"""
WalletIQ — PyQt6 Desktop App Entry Point.
Material 3-inspired UI with sidebar navigation, stacked views, terminal panel, and AI chat drawer.
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QPushButton, QStatusBar, QLabel,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon

from frontend.api_client import ApiClient
from frontend import theme
from frontend.components.sidebar import Sidebar
from frontend.components.terminal_panel import TerminalPanel
from frontend.components.chat_drawer import ChatDrawer
from frontend.views.login_view import LoginView
from frontend.views.dashboard_view import DashboardView
from frontend.views.transactions_view import TransactionsView
from frontend.views.budgets_view import BudgetsView
from frontend.views.insights_view import InsightsView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WalletIQ — Intelligent Personal Finance Tracker")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 800)

        self._dark = False
        self._api = ApiClient()

        # Central widget
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        self._root_layout = QVBoxLayout(central)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        # Main content area (sidebar + views + chat drawer)
        self._content_area = QHBoxLayout()
        self._content_area.setContentsMargins(0, 0, 0, 0)
        self._content_area.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar(dark=self._dark)
        self._sidebar.nav_clicked.connect(self._on_nav)
        self._sidebar.theme_toggled.connect(self._toggle_theme)
        self._sidebar.logout_clicked.connect(self._logout)
        self._sidebar.setVisible(False)

        # Stacked views
        self._stack = QStackedWidget()

        # Login view (index 0)
        self._login_view = LoginView(self._api, dark=self._dark)
        self._login_view.login_success.connect(self._on_login)
        self._stack.addWidget(self._login_view)

        # Dashboard (index 1)
        self._dashboard = DashboardView(self._api, dark=self._dark)
        self._stack.addWidget(self._dashboard)

        # Transactions (index 2)
        self._transactions = TransactionsView(self._api, dark=self._dark)
        self._stack.addWidget(self._transactions)

        # Budgets (index 3)
        self._budgets = BudgetsView(self._api, dark=self._dark)
        self._stack.addWidget(self._budgets)

        # Insights (index 4)
        self._insights = InsightsView(self._api, dark=self._dark)
        self._stack.addWidget(self._insights)

        # Chat drawer
        self._chat_drawer = ChatDrawer(self._api, dark=self._dark)
        self._chat_drawer.setVisible(False)

        # Layout: sidebar | stack | chat_drawer
        self._content_area.addWidget(self._sidebar)
        self._content_area.addWidget(self._stack, 1)
        self._content_area.addWidget(self._chat_drawer)

        self._root_layout.addLayout(self._content_area, 1)

        # Terminal panel (shared, docked at bottom)
        self._terminal = TerminalPanel()
        self._terminal.setVisible(False)
        self._api.signals.request_made.connect(self._terminal.log_request)
        self._root_layout.addWidget(self._terminal)

        # Floating AI Coach button (bottom-right)
        self._chat_fab = QPushButton("🤖")
        self._chat_fab.setFixedSize(52, 52)
        self._chat_fab.setCursor(Qt.CursorShape.PointingHandCursor)
        self._chat_fab.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.ACCENT2};
                color: white;
                border: none;
                border-radius: 26px;
                font-size: 24px;
            }}
            QPushButton:hover {{
                background-color: #E0944A;
            }}
        """)
        self._chat_fab.setParent(central)
        self._chat_fab.clicked.connect(self._toggle_chat)
        self._chat_fab.setVisible(False)

        # Status bar
        self._statusbar = QStatusBar()
        self._statusbar.setStyleSheet("font-size: 12px; padding: 2px 8px;")
        self.setStatusBar(self._statusbar)
        self._status_label = QLabel("Welcome to WalletIQ")
        self._statusbar.addWidget(self._status_label)

        # Apply initial theme
        self._apply_theme()

        # Start on login
        self._stack.setCurrentIndex(0)

    # ── Auth ───────────────────────────────────────────────────────────────────

    def _on_login(self, user_data: dict):
        username = user_data.get("username", "User")
        self._status_label.setText(f"Logged in as {username}")
        self._sidebar.setVisible(True)
        self._terminal.setVisible(True)
        self._chat_fab.setVisible(True)
        self._stack.setCurrentIndex(1)
        self._sidebar.set_active(0)
        self._dashboard.refresh()

    def _logout(self):
        self._api.logout()
        self._sidebar.setVisible(False)
        self._terminal.setVisible(False)
        self._chat_fab.setVisible(False)
        self._chat_drawer.hide_drawer()
        self._stack.setCurrentIndex(0)
        self._status_label.setText("Logged out")

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _on_nav(self, index: int):
        # Sidebar indices map to stack indices 1-4 (0 is login)
        view_index = index + 1
        self._stack.setCurrentIndex(view_index)

        # Refresh the view we're switching to
        views = [self._dashboard, self._transactions, self._budgets, self._insights]
        if 0 <= index < len(views):
            views[index].refresh()

    # ── Chat Drawer ────────────────────────────────────────────────────────────

    def _toggle_chat(self):
        if self._chat_drawer.isVisible():
            self._chat_drawer.hide_drawer()
        else:
            self._chat_drawer.show_drawer()

    # ── Theme ──────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self._dark = not self._dark
        self._apply_theme()

    def _apply_theme(self):
        qss = theme.dark_qss() if self._dark else theme.light_qss()
        QApplication.instance().setStyleSheet(qss)

        self._sidebar.apply_theme(self._dark)
        self._chat_drawer.apply_theme(self._dark)
        self._dashboard.apply_theme(self._dark)
        self._transactions.apply_theme(self._dark)
        self._budgets.apply_theme(self._dark)
        self._insights.apply_theme(self._dark)

    # ── Resize (reposition FAB) ────────────────────────────────────────────────

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_fab()

    def _reposition_fab(self):
        if self._chat_fab.isVisible():
            margin = 24
            x = self.centralWidget().width() - self._chat_fab.width() - margin
            y = self.centralWidget().height() - self._chat_fab.height() - margin - 120
            self._chat_fab.move(x, y)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(100, self._reposition_fab)


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
