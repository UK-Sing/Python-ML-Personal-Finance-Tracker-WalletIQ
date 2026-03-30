"""
WalletIQ — Budgets view.
Grid of budget cards with progress bars, overspend highlighting, add/edit/delete.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QGridLayout, QScrollArea, QMessageBox, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from frontend import theme
from frontend.components.card import Card
from frontend.components.dialogs import BudgetDialog


class BudgetCard(Card):
    """Single budget card with category, limit, progress bar, remaining."""

    def __init__(self, budget_data: dict, parent=None, dark=False):
        super().__init__(parent, dark)
        self._data = budget_data
        self.setMinimumWidth(260)
        self.setMaximumWidth(400)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        cat = budget_data.get("category", "Other")
        limit_val = budget_data.get("limit", 0)
        current = budget_data.get("current_spend", 0)
        remaining = budget_data.get("remaining", 0)
        overspent = budget_data.get("overspent", False)
        period = budget_data.get("period", "monthly").capitalize()

        # Header row
        header = QHBoxLayout()
        cat_label = QLabel(f"📂 {cat}")
        cat_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        cat_label.setStyleSheet("border: none;")
        header.addWidget(cat_label)
        header.addStretch()
        period_label = QLabel(period)
        period_label.setStyleSheet(f"color: {theme.ACCENT1}; font-size: 11px; font-weight: 600; border: none;")
        header.addWidget(period_label)
        self._layout.addLayout(header)

        # Progress bar
        progress = QProgressBar()
        pct = min(int((current / limit_val) * 100), 100) if limit_val > 0 else 0
        progress.setValue(pct)
        progress.setFixedHeight(18)
        progress.setFormat(f"₹{current:,.0f} / ₹{limit_val:,.0f}")
        if overspent:
            progress.setStyleSheet(f"""
                QProgressBar {{
                    background-color: {theme.SECONDARY if not dark else '#333'};
                    border: 1px solid {theme.ACCENT2};
                    border-radius: 6px; text-align: center; font-size: 11px;
                }}
                QProgressBar::chunk {{
                    background-color: {theme.ACCENT2};
                    border-radius: 5px;
                }}
            """)
        self._layout.addWidget(progress)

        # Remaining
        rem_row = QHBoxLayout()
        if overspent:
            rem_label = QLabel(f"⚠ Over by ₹{abs(remaining):,.2f}")
            rem_label.setStyleSheet(f"color: {theme.ACCENT2}; font-weight: bold; font-size: 12px; border: none;")
        else:
            rem_label = QLabel(f"₹{remaining:,.2f} remaining")
            rem_label.setStyleSheet(f"color: {theme.ACCENT1}; font-size: 12px; border: none;")
        rem_row.addWidget(rem_label)
        rem_row.addStretch()
        self._layout.addLayout(rem_row)

        # Overspend border highlight
        if overspent:
            bg = theme.CARD_BG_DARK if dark else theme.CARD_BG_LIGHT
            self.setStyleSheet(f"""
                BudgetCard {{
                    background-color: {bg};
                    border: 2px solid {theme.ACCENT2};
                    border-radius: 12px;
                }}
            """)


class BudgetsView(QWidget):
    def __init__(self, api_client, parent=None, dark=False):
        super().__init__(parent)
        self._api = api_client
        self._dark = dark
        self._budgets = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 12)
        layout.setSpacing(12)

        # Title row
        title_row = QHBoxLayout()
        title = QLabel("Budgets")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("border: none;")
        title_row.addWidget(title)
        title_row.addStretch()

        add_btn = QPushButton("+ Add Budget")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_budget)
        title_row.addWidget(add_btn)
        layout.addLayout(title_row)

        # Scroll area for grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        self._grid_widget = QWidget()
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(16)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self._grid_widget)
        layout.addWidget(scroll, 1)

    def refresh(self):
        code, data = self._api.get_budgets()
        if code == 200 and isinstance(data, list):
            self._budgets = data
            self._rebuild_grid()

    def _rebuild_grid(self):
        # Clear old cards
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cols = 3
        for i, b in enumerate(self._budgets):
            card = BudgetCard(b, dark=self._dark)
            card.setCursor(Qt.CursorShape.PointingHandCursor)
            card.mousePressEvent = lambda e, bdata=b: self._on_card_click(bdata)
            self._grid.addWidget(card, i // cols, i % cols)

        if not self._budgets:
            empty = QLabel("No budgets yet. Click '+ Add Budget' to get started.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("font-size: 14px; padding: 40px; border: none;")
            self._grid.addWidget(empty, 0, 0, 1, cols)

    def _add_budget(self):
        dlg = BudgetDialog(self, dark=self._dark)
        if dlg.exec():
            data = dlg.get_data()
            self._api.create_budget(**data)
            self.refresh()

    def _on_card_click(self, budget_data):
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction, QCursor
        menu = QMenu(self)
        edit_act = QAction("✏️ Edit", self)
        delete_act = QAction("🗑️ Delete", self)
        menu.addAction(edit_act)
        menu.addAction(delete_act)
        action = menu.exec(QCursor.pos())
        if action == edit_act:
            dlg = BudgetDialog(self, data=budget_data, dark=self._dark)
            if dlg.exec():
                fields = dlg.get_data()
                self._api.update_budget(budget_data["id"], **fields)
                self.refresh()
        elif action == delete_act:
            reply = QMessageBox.question(
                self, "Delete Budget", f"Delete {budget_data.get('category')} budget?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._api.delete_budget(budget_data["id"])
                self.refresh()

    def apply_theme(self, dark: bool):
        self._dark = dark
        self._rebuild_grid()
