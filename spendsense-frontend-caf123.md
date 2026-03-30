
# WalletIQ — PyQt6 Frontend Plan

Build a Material 3-inspired PyQt6 desktop app with solid colors, sharp shadows, light/dark theme toggle, and an earthy color palette connecting to the existing Django REST API.

## Color Palette

| Role | Hex | Usage |
|------|-----|-------|
| Primary | `#BFC6C4` | Surface tints, nav bar, headers |
| Secondary | `#E8E2D8` | Card backgrounds, input fields (light mode) |
| Accent 1 | `#6F8F72` | Success states, positive amounts, buttons |
| Accent 2 | `#F2A65A` | Warnings, overspend alerts, CTAs |
| Dark BG | `#1E1E1E` | Dark mode background |
| Light BG | `#F5F3EF` | Light mode background |

## Architecture

```
frontend/
├── main.py                 # App entry point, QApplication setup
├── api_client.py           # HTTP client wrapping all REST endpoints
├── theme.py                # M3 color tokens, QSS stylesheets, theme toggle
├── components/
│   ├── sidebar.py          # Navigation sidebar with icons
│   ├── card.py             # Reusable M3 card widget (sharp shadow)
│   ├── stat_card.py        # Metric display card (icon + value + label)
│   ├── dialogs.py          # Add/edit transaction & budget dialogs
│   ├── charts.py           # Matplotlib-in-Qt chart widgets
│   ├── terminal_panel.py   # Read-only terminal showing API activity
│   └── chat_drawer.py      # Overlay chat drawer (right side, accessible from any view)
├── views/
│   ├── login_view.py       # Login / register screen
│   ├── dashboard_view.py   # Overview: stats, category chart, recent txns
│   ├── transactions_view.py# Searchable transaction table + add button
│   ├── budgets_view.py     # Budget cards with progress bars
│   └── insights_view.py    # AI insights display + "Run Analysis" button
└── resources/
    └── icons/              # SVG icons for sidebar & cards
```

## Screens (5 views + chat drawer)

### 1. Login / Register
- Two-tab form (Login | Register) centered on screen
- Fields: username, password (+ email for register)
- Calls `POST /api/login` or `POST /api/register`, stores token

### 2. Dashboard
- Top stat cards: total spend, transaction count, budget health
- Category spending donut/pie chart (matplotlib)
- Recent 5 transactions mini-table
- "Run AI Analysis" quick-action button

### 3. Transactions
- Filterable table (QTableWidget) with columns: date, description, category, amount
- Category filter dropdown + search bar
- Add Transaction dialog (auto-categorization happens server-side)
- Edit/delete context menu
- Calls `GET/POST/PUT/DELETE /api/transactions`

### 4. Budgets
- Grid of budget cards, each showing: category, limit, progress bar (current_spend / limit), remaining
- Overspend cards highlighted with `#F2A65A` border
- Add/edit budget dialog
- Calls `GET/POST/PUT/DELETE /api/budgets`

### 5. AI Insights
- "Run Analysis" button → `POST /api/ai/analyze`
- Cards for each insight type: spending_pattern, expense_prediction, anomaly_detection, recommendations
- Expand card to see full content
- Calls `GET /api/insights`

### Chat Drawer (Overlay — accessible from any view)
- Floating "AI Coach" button fixed to bottom-right corner of the main window
- Click opens a right-side overlay drawer (~350px wide) that slides over content with semi-transparent backdrop
- Chat bubble UI: user messages right-aligned, bot messages left-aligned
- Input field at bottom with send button
- Close button / click backdrop to dismiss
- Persists chat history while the app is open (resets on close)
- Calls `POST /api/ai/chat` with `{"message": "..."}` and displays response
- Rule-based bot understands queries like:
  - "How much did I spend on Groceries?" → queries transaction summary
  - "Am I over budget?" → checks budget status
  - "What are my top spending categories?" → category breakdown
  - "Any anomalies?" → runs anomaly detector
  - "Give me advice" / "recommendations" → runs recommender
  - "Predict next month" → runs predictor
  - Fallback: "I can help with: spending, budgets, anomalies, predictions, recommendations"

## Terminal Panel (Demo Mode)

Every view page includes a collapsible read-only terminal panel docked at the bottom. It logs every API call in real-time with three sections per request:

1. **Curl command** — the equivalent `curl` command so the audience sees the exact request
2. **Response JSON** — formatted response body with status code
3. **Timing** — round-trip duration in milliseconds

Example output:
```
─── 14:23:05 ─────────────────────────────────────
$ curl -X GET http://localhost:8000/api/transactions \
  -H "Authorization: Token 090db0..." \
  -H "Content-Type: application/json"

← 200 OK (47ms)
[
  {"id": 1, "amount": 850.0, "category": "Groceries", ...},
  ...
]
───────────────────────────────────────────────────
```

**Implementation:**
- `api_client.py` emits a Qt signal on every request/response
- `terminal_panel.py` is a `QTextEdit(readOnly=True)` with monospace font, styled like a terminal (dark bg regardless of theme)
- Panel has a collapse/expand toggle and a clear button
- Each view embeds the same shared terminal panel instance via the main window

## Design Rules (Material 3 + Sharp)

- **Elevation**: No blur — use solid `#00000033` offset shadows (2px right, 2px down)
- **Corners**: 12px border-radius on cards, 8px on buttons/inputs
- **Typography**: System sans-serif, weight hierarchy (bold headings, regular body)
- **Cards**: Solid background fill, 1px border in muted tone, sharp drop shadow
- **Buttons**: Filled (accent bg + white text) or outlined (border only)
- **Sidebar**: Fixed left, icon + label, highlight active with accent bar
- **Theme toggle**: Icon button in sidebar footer, switches all QSS at runtime

## Implementation Phases

### Phase 1 — Foundation
- `main.py`, `api_client.py`, `theme.py` (light + dark QSS)
- Login view with token storage
- Main window shell with sidebar navigation + stacked widget

### Phase 2 — Dashboard & Transactions
- Dashboard view with stat cards and matplotlib chart
- Transactions view with table, filter, CRUD dialogs

### Phase 3 — Budgets & Insights
- Budgets view with progress-bar cards
- Insights view with AI analysis trigger and result cards

### Phase 4 — Polish
- Theme toggle wired up
- Error handling toasts / status bar messages
- Loading spinners for API calls
