"""
WalletIQ — AI Insights view.
"Run Analysis" button triggers POST /api/ai/analyze, then displays insight cards.
"""
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QSizePolicy, QTextEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from frontend import theme
from frontend.components.card import Card


INSIGHT_ICONS = {
    "spending_pattern": "📊",
    "expense_prediction": "📈",
    "anomaly_detection": "🔍",
    "recommendations": "💡",
}

INSIGHT_LABELS = {
    "spending_pattern": "Spending Pattern",
    "expense_prediction": "Expense Prediction",
    "anomaly_detection": "Anomaly Detection",
    "recommendations": "Recommendations",
}


class InsightCard(Card):
    """Expandable card for a single insight."""

    def __init__(self, insight: dict, parent=None, dark=False):
        super().__init__(parent, dark)
        self._expanded = False
        self.setMinimumWidth(300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        itype = insight.get("type", "")
        icon = INSIGHT_ICONS.get(itype, "📋")
        label = INSIGHT_LABELS.get(itype, itype.replace("_", " ").title())
        content = insight.get("content", {})
        created = insight.get("created_at", "")[:16].replace("T", " ")

        # Header
        header = QHBoxLayout()
        title = QLabel(f"{icon}  {label}")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("border: none;")
        header.addWidget(title)
        header.addStretch()
        date_label = QLabel(created)
        date_label.setStyleSheet(f"font-size: 11px; color: {'#999' if dark else '#888'}; border: none;")
        header.addWidget(date_label)
        self._layout.addLayout(header)

        # Summary preview (first 2 lines of content)
        preview = self._format_preview(content)
        self._preview_label = QLabel(preview)
        self._preview_label.setWordWrap(True)
        self._preview_label.setStyleSheet("font-size: 13px; border: none; padding: 4px 0;")
        self._layout.addWidget(self._preview_label)

        # Full content (hidden by default)
        self._detail = QTextEdit()
        self._detail.setReadOnly(True)
        self._detail.setVisible(False)
        self._detail.setMaximumHeight(300)
        self._detail.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme.DARK_BG if dark else theme.SECONDARY};
                border: 1px solid {theme.BORDER_MUTED_DARK if dark else theme.BORDER_MUTED_LIGHT};
                border-radius: 8px; padding: 8px; font-size: 12px;
                font-family: 'Cascadia Code', 'Consolas', monospace;
            }}
        """)
        full_text = json.dumps(content, indent=2) if isinstance(content, (dict, list)) else str(content)
        self._detail.setPlainText(full_text)
        self._layout.addWidget(self._detail)

        # Expand button
        self._expand_btn = QPushButton("▶ Show Details")
        self._expand_btn.setObjectName("outlined")
        self._expand_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._expand_btn.setFixedHeight(30)
        self._expand_btn.clicked.connect(self._toggle_expand)
        self._layout.addWidget(self._expand_btn)

    def _format_preview(self, content) -> str:
        if isinstance(content, dict):
            lines = []
            for k, v in list(content.items())[:3]:
                val_str = str(v)
                if len(val_str) > 80:
                    val_str = val_str[:80] + "..."
                lines.append(f"• {k.replace('_', ' ').title()}: {val_str}")
            return "\n".join(lines) if lines else "No data"
        return str(content)[:200]

    def _toggle_expand(self):
        self._expanded = not self._expanded
        self._detail.setVisible(self._expanded)
        self._expand_btn.setText("▼ Hide Details" if self._expanded else "▶ Show Details")


class InsightsView(QWidget):
    def __init__(self, api_client, parent=None, dark=False):
        super().__init__(parent)
        self._api = api_client
        self._dark = dark

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 12)
        layout.setSpacing(12)

        # Title row
        title_row = QHBoxLayout()
        title = QLabel("AI Insights")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("border: none;")
        title_row.addWidget(title)
        title_row.addStretch()

        self._analyze_btn = QPushButton("🧠  Run Analysis")
        self._analyze_btn.setObjectName("warning")
        self._analyze_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._analyze_btn.clicked.connect(self._run_analysis)
        title_row.addWidget(self._analyze_btn)
        layout.addLayout(title_row)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        self._container = QWidget()
        self._vbox = QVBoxLayout(self._container)
        self._vbox.setSpacing(16)
        self._vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self._container)
        layout.addWidget(scroll, 1)

    def refresh(self):
        code, data = self._api.get_insights()
        if code == 200 and isinstance(data, list):
            self._rebuild(data)

    def _rebuild(self, insights: list):
        while self._vbox.count():
            item = self._vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not insights:
            empty = QLabel("No insights yet. Click 'Run Analysis' to generate AI insights.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("font-size: 14px; padding: 40px; border: none;")
            self._vbox.addWidget(empty)
            return

        for insight in insights:
            card = InsightCard(insight, dark=self._dark)
            self._vbox.addWidget(card)

    def _run_analysis(self):
        self._analyze_btn.setText("⏳ Analyzing...")
        self._analyze_btn.setEnabled(False)
        code, data = self._api.run_analysis()
        self._analyze_btn.setEnabled(True)
        if code == 200:
            self._analyze_btn.setText("✅ Done! Refreshing...")
            self.refresh()
            self._analyze_btn.setText("🧠  Run Analysis")
        else:
            self._analyze_btn.setText("❌ Failed — Retry")

    def apply_theme(self, dark: bool):
        self._dark = dark
        self.refresh()
