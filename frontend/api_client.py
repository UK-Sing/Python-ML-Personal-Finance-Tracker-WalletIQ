"""
WalletIQ — HTTP client wrapping all Django REST API endpoints.
Emits Qt signals on every request/response for the terminal panel.
"""
import time
import json
import requests
from PyQt6.QtCore import QObject, pyqtSignal


class ApiSignals(QObject):
    request_made = pyqtSignal(dict)  # {method, url, headers, body, response, status_code, duration_ms}


class ApiClient:
    BASE_URL = "http://localhost:8000/api"

    def __init__(self):
        self.token = None
        self.signals = ApiSignals()

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Token {self.token}"
        return h

    def _request(self, method: str, path: str, body=None, params=None):
        url = f"{self.BASE_URL}{path}"
        headers = self._headers()
        start = time.perf_counter()
        try:
            resp = requests.request(
                method, url, headers=headers,
                json=body, params=params, timeout=15,
            )
            duration = round((time.perf_counter() - start) * 1000, 1)
            try:
                resp_body = resp.json()
            except Exception:
                resp_body = resp.text
            self.signals.request_made.emit({
                "method": method,
                "url": url,
                "headers": headers,
                "body": body,
                "response": resp_body,
                "status_code": resp.status_code,
                "duration_ms": duration,
            })
            return resp.status_code, resp_body
        except requests.ConnectionError:
            self.signals.request_made.emit({
                "method": method,
                "url": url,
                "headers": headers,
                "body": body,
                "response": "Connection refused – is the Django server running?",
                "status_code": 0,
                "duration_ms": 0,
            })
            return 0, {"error": "Connection refused – is the Django server running?"}
        except Exception as exc:
            return 0, {"error": str(exc)}

    # ── Auth ───────────────────────────────────────────────────────────────────

    def login(self, username: str, password: str):
        code, data = self._request("POST", "/login", {"username": username, "password": password})
        if code == 200 and "token" in data:
            self.token = data["token"]
        return code, data

    def register(self, username: str, password: str, email: str = ""):
        body = {"username": username, "password": password}
        if email:
            body["email"] = email
        code, data = self._request("POST", "/register", body)
        if code == 201 and "token" in data:
            self.token = data["token"]
        return code, data

    def logout(self):
        self.token = None

    # ── Profile ────────────────────────────────────────────────────────────────

    def get_profile(self):
        return self._request("GET", "/profile")

    # ── Transactions ───────────────────────────────────────────────────────────

    def get_transactions(self, category=None):
        params = {}
        if category:
            params["category"] = category
        return self._request("GET", "/transactions", params=params)

    def create_transaction(self, amount, description, date, category="Other"):
        return self._request("POST", "/transactions", {
            "amount": amount,
            "description": description,
            "date": date,
            "category": category,
        })

    def update_transaction(self, pk, **fields):
        return self._request("PUT", f"/transactions/{pk}", fields)

    def delete_transaction(self, pk):
        return self._request("DELETE", f"/transactions/{pk}")

    def get_transaction_summary(self):
        return self._request("GET", "/transactions/summary")

    # ── Budgets ────────────────────────────────────────────────────────────────

    def get_budgets(self):
        return self._request("GET", "/budgets")

    def create_budget(self, category, limit, period="monthly"):
        return self._request("POST", "/budgets", {
            "category": category,
            "limit": limit,
            "period": period,
        })

    def update_budget(self, pk, **fields):
        return self._request("PUT", f"/budgets/{pk}", fields)

    def delete_budget(self, pk):
        return self._request("DELETE", f"/budgets/{pk}")

    # ── Insights ───────────────────────────────────────────────────────────────

    def get_insights(self, insight_type=None):
        params = {}
        if insight_type:
            params["type"] = insight_type
        return self._request("GET", "/insights", params=params)

    def delete_insight(self, pk):
        return self._request("DELETE", f"/insights/{pk}")

    # ── AI ─────────────────────────────────────────────────────────────────────

    def run_analysis(self):
        return self._request("POST", "/ai/analyze")

    def retrain_model(self):
        return self._request("POST", "/ai/retrain")

    def chat(self, message: str):
        return self._request("POST", "/ai/chat", {"message": message})
