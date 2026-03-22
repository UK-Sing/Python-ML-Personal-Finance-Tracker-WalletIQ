# SpendSense AI — Intelligent Personal Finance Tracker

An AI-powered personal finance management backend built with Django REST Framework, featuring real-time transaction categorization, spending pattern analysis, expense forecasting, anomaly detection, and smart budget recommendations.

## Features

- **ML Transaction Categorizer** — TF-IDF + Logistic Regression auto-categorizes transactions on creation
- **Spending Pattern Analyzer** — K-Means clustering identifies user spending behavior profiles
- **Expense Predictor** — Linear trend forecasting projects spending 3 months ahead per category
- **Anomaly Detector** — Z-score analysis flags unusual transactions per category
- **Smart Recommender** — Rule-based engine generates budget adherence and savings advice
- **Budget Tracker** — Real-time spend tracking with overspend alerts
- **Dual Storage** — SQLite (Django ORM) as primary, MongoDB as optional analytics store
- **Token Authentication** — DRF Token Auth for all protected endpoints

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 6.0 + Django REST Framework 3.17 |
| Database | SQLite (primary) + MongoDB (analytics) |
| ML/AI | scikit-learn, NumPy, pandas |
| Auth | DRF Token Authentication |

## Project Structure

```
WalletIQ/
├── WalletIQ/              # Django project settings & root URLs
├── backend/
│   ├── accounts/          # User model, auth (register/login/profile)
│   ├── transactions/      # Transaction CRUD with auto-categorization
│   ├── budgets/           # Budget CRUD with live spend tracking
│   ├── insights/          # AI-generated insight storage & retrieval
│   ├── ai_engine/         # ML modules & orchestrator
│   │   ├── categorizer.py
│   │   ├── pattern_analyzer.py
│   │   ├── predictor.py
│   │   ├── anomaly_detector.py
│   │   ├── recommender.py
│   │   └── engine.py      # Orchestrator — runs all 5 modules
│   └── db_client.py       # MongoDB connection utility
├── manage.py
└── project-requirements.txt
```

## Setup

### Prerequisites
- Python 3.12+
- MongoDB (optional — app works without it)

### Installation

```bash
# Clone the repo
git clone https://github.com/<your-username>/SpendSense-AI.git
cd SpendSense-AI

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install django djangorestframework pymongo scikit-learn numpy pandas joblib

# Set environment variables (or copy .env.example)
export DJANGO_SECRET_KEY="your-secret-key"
export MONGO_USER="your-mongo-user"
export MONGO_PASSWORD="your-mongo-password"

# Run migrations
python manage.py migrate

# Seed demo data (trains ML model + creates demo user with 60 transactions)
python manage.py seed_data

# Start server
python manage.py runserver
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Create user account |
| POST | `/api/login` | Authenticate & get token |
| GET/PATCH | `/api/profile` | View/update user profile |
| GET/POST | `/api/transactions` | List / create transactions |
| GET/PUT/DELETE | `/api/transactions/<id>` | Transaction detail |
| GET | `/api/transactions/summary` | Spending summary by category |
| GET/POST | `/api/budgets` | List / create budgets |
| GET/PUT/DELETE | `/api/budgets/<id>` | Budget detail (with live spend) |
| GET | `/api/insights` | List all AI insights |
| GET/DELETE | `/api/insights/<id>` | Insight detail |
| POST | `/api/ai/analyze` | Run full AI analysis |
| POST | `/api/ai/retrain` | Retrain categorizer model |

## Quick Demo

```bash
# Login
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo1234"}'

# Use the returned token
TOKEN="<token-from-login>"

# Add a transaction (auto-categorized by ML)
curl -X POST http://localhost:8000/api/transactions \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 450, "description": "Swiggy biryani order", "date": "2026-03-22T12:00:00Z"}'

# Run AI analysis
curl -X POST http://localhost:8000/api/ai/analyze \
  -H "Authorization: Token $TOKEN"

# View insights
curl http://localhost:8000/api/insights \
  -H "Authorization: Token $TOKEN"
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | `change-me-in-production` | Django secret key |
| `MONGO_HOST` | `localhost` | MongoDB host |
| `MONGO_PORT` | `27017` | MongoDB port |
| `MONGO_DB` | `spendsense` | MongoDB database name |
| `MONGO_USER` | _(empty)_ | MongoDB username |
| `MONGO_PASSWORD` | _(empty)_ | MongoDB password |
| `MONGO_AUTH_SOURCE` | `admin` | MongoDB auth database |

## License

This project is for educational purposes.
