"""
WalletIQ — Matplotlib-in-Qt chart widgets.
"""
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from frontend import theme


CHART_COLORS = [
    "#6F8F72", "#F2A65A", "#BFC6C4", "#E8E2D8",
    "#8CB4A0", "#D4896A", "#A3B1AF", "#C9C1B4",
]


class CategoryPieChart(FigureCanvas):
    """Donut/pie chart showing spending by category."""

    def __init__(self, parent=None, width=5, height=4, dark=False):
        self.fig = Figure(figsize=(width, height), dpi=100)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self._dark = dark
        self._apply_bg()

    def _apply_bg(self):
        bg = theme.DARK_BG if self._dark else theme.LIGHT_BG
        self.fig.patch.set_facecolor(bg)
        self.ax.set_facecolor(bg)

    def update_data(self, categories: list[str], amounts: list[float], dark: bool = False):
        self._dark = dark
        self._apply_bg()
        self.ax.clear()
        if not categories or not amounts:
            text_color = theme.TEXT_DARK if dark else theme.TEXT_LIGHT
            self.ax.text(0.5, 0.5, "No data", ha="center", va="center",
                         fontsize=14, color=text_color, transform=self.ax.transAxes)
            self.draw()
            return

        colors = CHART_COLORS[:len(categories)]
        text_color = theme.TEXT_DARK if dark else theme.TEXT_LIGHT

        wedges, texts, autotexts = self.ax.pie(
            amounts, labels=categories, colors=colors,
            autopct="%1.1f%%", startangle=90, pctdistance=0.75,
            wedgeprops=dict(width=0.4, edgecolor=theme.DARK_BG if dark else theme.LIGHT_BG),
        )
        for t in texts:
            t.set_color(text_color)
            t.set_fontsize(10)
        for t in autotexts:
            t.set_color(text_color)
            t.set_fontsize(9)

        self.ax.set_title("Spending by Category", color=text_color, fontsize=13, fontweight="bold", pad=12)
        self.fig.tight_layout()
        self.draw()
