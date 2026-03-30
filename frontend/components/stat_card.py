"""
Metric display card — icon + value + label, built on Card.
"""
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from frontend.components.card import Card
from frontend import theme


class StatCard(Card):
    def __init__(self, icon_text: str, value: str, label: str, parent=None, dark=False):
        super().__init__(parent, dark)

        row = QHBoxLayout()
        row.setSpacing(12)

        icon_label = QLabel(icon_text)
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            background-color: {theme.ACCENT1}22;
            border-radius: 8px;
            font-size: 20px;
        """)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        self._value_label = QLabel(value)
        self._value_label.setStyleSheet("font-size: 22px; font-weight: bold; border: none;")

        self._desc_label = QLabel(label)
        self._desc_label.setStyleSheet("font-size: 12px; opacity: 0.7; border: none;")

        text_col.addWidget(self._value_label)
        text_col.addWidget(self._desc_label)

        row.addWidget(icon_label)
        row.addLayout(text_col)
        row.addStretch()

        self._layout.addLayout(row)

    def set_value(self, value: str):
        self._value_label.setText(value)

    def set_label(self, label: str):
        self._desc_label.setText(label)
