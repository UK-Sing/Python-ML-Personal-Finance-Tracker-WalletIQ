"""
WalletIQ — Add/Edit dialogs for transactions and budgets.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QDateTimeEdit, QPushButton, QDoubleSpinBox, QFormLayout,
)
from PyQt6.QtCore import Qt, QDateTime
from frontend import theme

CATEGORIES = [
    "Groceries", "Dining", "Transport", "Utilities",
    "Entertainment", "Healthcare", "Shopping", "Other",
]

PERIODS = ["monthly", "weekly"]


class TransactionDialog(QDialog):
    """Dialog for adding or editing a transaction."""

    def __init__(self, parent=None, data=None, dark=False):
        super().__init__(parent)
        self.setWindowTitle("Edit Transaction" if data else "Add Transaction")
        self.setMinimumWidth(380)
        self.setModal(True)
        self._data = data or {}

        form = QFormLayout()
        form.setSpacing(12)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 9_999_999.99)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("₹ ")
        self.amount_input.setValue(self._data.get("amount", 0.0))

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("e.g. Swiggy biryani order")
        self.desc_input.setText(self._data.get("description", ""))

        self.category_input = QComboBox()
        self.category_input.addItems(CATEGORIES)
        if "category" in self._data:
            idx = self.category_input.findText(self._data["category"])
            if idx >= 0:
                self.category_input.setCurrentIndex(idx)

        self.date_input = QDateTimeEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        if "date" in self._data:
            self.date_input.setDateTime(QDateTime.fromString(self._data["date"][:19], "yyyy-MM-ddTHH:mm:ss"))
        else:
            self.date_input.setDateTime(QDateTime.currentDateTime())

        form.addRow("Amount:", self.amount_input)
        form.addRow("Description:", self.desc_input)
        form.addRow("Category:", self.category_input)
        form.addRow("Date:", self.date_input)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("outlined")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addLayout(form)
        layout.addSpacing(12)
        layout.addLayout(btn_row)

    def get_data(self) -> dict:
        return {
            "amount": self.amount_input.value(),
            "description": self.desc_input.text().strip(),
            "category": self.category_input.currentText(),
            "date": self.date_input.dateTime().toString("yyyy-MM-ddTHH:mm:ssZ"),
        }


class BudgetDialog(QDialog):
    """Dialog for adding or editing a budget."""

    def __init__(self, parent=None, data=None, dark=False):
        super().__init__(parent)
        self.setWindowTitle("Edit Budget" if data else "Add Budget")
        self.setMinimumWidth(340)
        self.setModal(True)
        self._data = data or {}

        form = QFormLayout()
        form.setSpacing(12)

        self.category_input = QComboBox()
        self.category_input.addItems(CATEGORIES)
        if "category" in self._data:
            idx = self.category_input.findText(self._data["category"])
            if idx >= 0:
                self.category_input.setCurrentIndex(idx)

        self.limit_input = QDoubleSpinBox()
        self.limit_input.setRange(1.0, 9_999_999.99)
        self.limit_input.setDecimals(2)
        self.limit_input.setPrefix("₹ ")
        self.limit_input.setValue(self._data.get("limit", 1000.0))

        self.period_input = QComboBox()
        self.period_input.addItems(PERIODS)
        if "period" in self._data:
            idx = self.period_input.findText(self._data["period"])
            if idx >= 0:
                self.period_input.setCurrentIndex(idx)

        form.addRow("Category:", self.category_input)
        form.addRow("Limit:", self.limit_input)
        form.addRow("Period:", self.period_input)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("outlined")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addLayout(form)
        layout.addSpacing(12)
        layout.addLayout(btn_row)

    def get_data(self) -> dict:
        return {
            "category": self.category_input.currentText(),
            "limit": self.limit_input.value(),
            "period": self.period_input.currentText(),
        }
