"""
WalletIQ — Transactions view.
Searchable/filterable table with add/edit/delete CRUD via dialogs.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QComboBox, QLineEdit, QMenu, QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction
from frontend import theme
from frontend.components.dialogs import TransactionDialog, CATEGORIES


class TransactionsView(QWidget):
    def __init__(self, api_client, parent=None, dark=False):
        super().__init__(parent)
        self._api = api_client
        self._dark = dark
        self._txns = []  # cached list from API

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 12)
        layout.setSpacing(12)

        # Title row
        title_row = QHBoxLayout()
        title = QLabel("Transactions")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("border: none;")
        title_row.addWidget(title)
        title_row.addStretch()

        add_btn = QPushButton("+ Add Transaction")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_transaction)
        title_row.addWidget(add_btn)
        layout.addLayout(title_row)

        # Filter row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Search description...")
        self._search.setFixedHeight(36)
        self._search.textChanged.connect(self._apply_filter)
        filter_row.addWidget(self._search, 1)

        self._cat_filter = QComboBox()
        self._cat_filter.addItem("All Categories")
        self._cat_filter.addItems(CATEGORIES)
        self._cat_filter.setFixedHeight(36)
        self._cat_filter.currentTextChanged.connect(self._apply_filter)
        filter_row.addWidget(self._cat_filter)

        layout.addLayout(filter_row)

        # Table
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["Date", "Description", "Category", "Amount", "Auto-Cat"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._context_menu)
        layout.addWidget(self._table, 1)

    def refresh(self):
        cat = self._cat_filter.currentText()
        cat_param = None if cat == "All Categories" else cat
        code, data = self._api.get_transactions(category=cat_param)
        if code == 200 and isinstance(data, list):
            self._txns = data
            self._populate_table(data)

    def _populate_table(self, txns):
        search = self._search.text().strip().lower()
        filtered = txns
        if search:
            filtered = [t for t in filtered if search in t.get("description", "").lower()]

        self._table.setRowCount(len(filtered))
        for row, tx in enumerate(filtered):
            self._table.setItem(row, 0, QTableWidgetItem(tx.get("date", "")[:10]))
            self._table.setItem(row, 1, QTableWidgetItem(tx.get("description", "")))
            self._table.setItem(row, 2, QTableWidgetItem(tx.get("category", "")))
            amt = QTableWidgetItem(f"₹{tx.get('amount', 0):,.2f}")
            amt.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 3, amt)
            auto = "✅" if tx.get("auto_categorized") else ""
            auto_item = QTableWidgetItem(auto)
            auto_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 4, auto_item)
            # Store id in first column's data
            self._table.item(row, 0).setData(Qt.ItemDataRole.UserRole, tx.get("id"))

    def _apply_filter(self):
        self._populate_table(self._txns)

    def _add_transaction(self):
        dlg = TransactionDialog(self, dark=self._dark)
        if dlg.exec():
            data = dlg.get_data()
            code, resp = self._api.create_transaction(
                amount=data["amount"],
                description=data["description"],
                date=data["date"],
                category=data["category"],
            )
            self.refresh()

    def _context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        item = self._table.item(row, 0)
        if not item:
            return
        tx_id = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu(self)
        edit_action = QAction("✏️ Edit", self)
        delete_action = QAction("🗑️ Delete", self)
        menu.addAction(edit_action)
        menu.addAction(delete_action)

        action = menu.exec(self._table.viewport().mapToGlobal(pos))
        if action == edit_action:
            self._edit_transaction(row, tx_id)
        elif action == delete_action:
            self._delete_transaction(tx_id)

    def _edit_transaction(self, row, tx_id):
        # Find tx data
        tx_data = next((t for t in self._txns if t.get("id") == tx_id), None)
        if not tx_data:
            return
        dlg = TransactionDialog(self, data=tx_data, dark=self._dark)
        if dlg.exec():
            fields = dlg.get_data()
            self._api.update_transaction(tx_id, **fields)
            self.refresh()

    def _delete_transaction(self, tx_id):
        reply = QMessageBox.question(
            self, "Delete Transaction",
            "Are you sure you want to delete this transaction?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._api.delete_transaction(tx_id)
            self.refresh()

    def apply_theme(self, dark: bool):
        self._dark = dark
