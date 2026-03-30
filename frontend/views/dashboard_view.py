"""
WalletIQ — Dashboard view.
Top stat cards, category spending chart, recent 5 transactions, quick AI action.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from frontend import theme
from frontend.components.stat_card import StatCard
from frontend.components.charts import CategoryPieChart
from frontend.components.card import Card


class DashboardView(QWidget):
    def __init__(self, api_client, parent=None, dark=False):
        super().__init__(parent)
        self._api = api_client
        self._dark = dark

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 12)
        layout.setSpacing(16)

        # Title
        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("border: none;")
        layout.addWidget(title)

        # Stat cards row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        self._spend_card = StatCard("💰", "₹0", "Total Spend", dark=dark)
        self._txn_card = StatCard("📝", "0", "Transactions", dark=dark)
        self._budget_card = StatCard("🎯", "—", "Budget Health", dark=dark)
        stats_row.addWidget(self._spend_card)
        stats_row.addWidget(self._txn_card)
        stats_row.addWidget(self._budget_card)
        layout.addLayout(stats_row)

        # Middle row: chart + recent transactions
        mid_row = QHBoxLayout()
        mid_row.setSpacing(16)

        # Pie chart
        self._chart = CategoryPieChart(dark=dark)
        chart_card = Card(dark=dark)
        chart_card.layout().addWidget(self._chart)
        mid_row.addWidget(chart_card, 1)

        # Recent transactions
        recent_card = Card(dark=dark)
        self._recent_card = recent_card
        recent_title = QLabel("Recent Transactions")
        recent_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        recent_title.setStyleSheet("border: none;")
        recent_card.layout().addWidget(recent_title)

        self._recent_table = QTableWidget(0, 4)
        self._recent_table.setHorizontalHeaderLabels(["Date", "Description", "Category", "Amount"])
        self._recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._recent_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._recent_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._recent_table.setAlternatingRowColors(True)
        self._recent_table.verticalHeader().setVisible(False)
        recent_card.layout().addWidget(self._recent_table)

        mid_row.addWidget(recent_card, 1)
        layout.addLayout(mid_row, 1)

        # Quick action row
        action_row = QHBoxLayout()
        action_row.addStretch()
        self._ai_btn = QPushButton("🧠  Run AI Analysis")
        self._ai_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._ai_btn.setObjectName("warning")
        self._ai_btn.clicked.connect(self._run_analysis)
        action_row.addWidget(self._ai_btn)
        layout.addLayout(action_row)

    def refresh(self):
        """Fetch summary + recent transactions and update UI."""
        # Summary
        code, summary = self._api.get_transaction_summary()
        if code == 200:
            total = summary.get("total_spend", 0)
            count = summary.get("transaction_count", 0)
            by_cat = summary.get("by_category", [])
            self._spend_card.set_value(f"₹{total:,.2f}")
            self._txn_card.set_value(str(count))
            # Chart
            cats = [c["category"] for c in by_cat]
            amounts = [c["total"] for c in by_cat]
            self._chart.update_data(cats, amounts, self._dark)

        # Budget health
        bcode, budgets = self._api.get_budgets()
        if bcode == 200 and isinstance(budgets, list) and budgets:
            overspent = sum(1 for b in budgets if b.get("overspent"))
            total_b = len(budgets)
            if overspent == 0:
                self._budget_card.set_value("✅ On Track")
            else:
                self._budget_card.set_value(f"⚠ {overspent}/{total_b} Over")
        else:
            self._budget_card.set_value("—")

        # Recent 5 transactions
        tcode, txns = self._api.get_transactions()
        if tcode == 200 and isinstance(txns, list):
            recent = txns[:5]
            self._recent_table.setRowCount(len(recent))
            for row, tx in enumerate(recent):
                date_str = tx.get("date", "")[:10]
                self._recent_table.setItem(row, 0, QTableWidgetItem(date_str))
                self._recent_table.setItem(row, 1, QTableWidgetItem(tx.get("description", "")))
                self._recent_table.setItem(row, 2, QTableWidgetItem(tx.get("category", "")))
                amt_item = QTableWidgetItem(f"₹{tx.get('amount', 0):,.2f}")
                amt_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self._recent_table.setItem(row, 3, amt_item)

    def _run_analysis(self):
        self._ai_btn.setText("⏳ Running...")
        self._ai_btn.setEnabled(False)
        code, data = self._api.run_analysis()
        self._ai_btn.setEnabled(True)
        self._ai_btn.setText("🧠  Run AI Analysis")
        if code == 200:
            self._ai_btn.setText("✅ Analysis Complete!")
        else:
            self._ai_btn.setText("❌ Analysis Failed")

    def apply_theme(self, dark: bool):
        self._dark = dark
        self._spend_card.apply_theme(dark)
        self._txn_card.apply_theme(dark)
        self._budget_card.apply_theme(dark)
        self._recent_card.apply_theme(dark)
        self._chart.update_data([], [], dark)
        self.refresh()
