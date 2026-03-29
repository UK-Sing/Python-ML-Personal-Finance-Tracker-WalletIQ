import os
import joblib
import numpy as np
import kagglehub
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'categorizer.pkl')

CATEGORIES = [
    'Groceries', 'Dining', 'Transport', 'Utilities',
    'Entertainment', 'Healthcare', 'Shopping', 'Other'
]

KAGGLE_CATEGORY_MAP = {
    'Groceries': 'Groceries',
    'Food': 'Dining',
    'Friend Activities': 'Dining',
    'Transportation': 'Transport',
    'Travel': 'Transport',
    'Housing and Utilities': 'Utilities',
    'Subscriptions': 'Entertainment',
    'Hobbies': 'Entertainment',
    'Fitness': 'Entertainment',
    'Medical/Dental': 'Healthcare',
    'Personal Hygiene': 'Healthcare',
    'Shopping': 'Shopping',
    'Gifts': 'Other',
}

KAGGLE_DATASET = 'ahmedmohamed2003/spending-habits'

TRAINING_DATA = [
    ("supermarket grocery store vegetables fruit bread milk eggs", "Groceries"),
    ("walmart costco target food items fresh produce", "Groceries"),
    ("grocery big bazaar reliance fresh d-mart", "Groceries"),
    ("fruits vegetables rice wheat dal pulses", "Groceries"),
    ("meat chicken fish seafood butcher", "Groceries"),
    ("restaurant dinner lunch brunch cafe bistro", "Dining"),
    ("pizza burger fries mcdonalds kfc subway dominos", "Dining"),
    ("coffee starbucks barista tea chai latte", "Dining"),
    ("zomato swiggy food delivery order", "Dining"),
    ("hotel bar lounge drinks cocktails", "Dining"),
    ("sushi noodles chinese thai italian food", "Dining"),
    ("uber ola cab taxi ride booking", "Transport"),
    ("bus train metro rail ticket pass", "Transport"),
    ("petrol diesel fuel filling station pump", "Transport"),
    ("parking toll highway expressway", "Transport"),
    ("flight airline airfare ticket booking travel", "Transport"),
    ("rapido bike ride auto rickshaw", "Transport"),
    ("electricity bill power grid current charges", "Utilities"),
    ("water bill municipal supply tap", "Utilities"),
    ("gas cylinder lpg pipeline cooking", "Utilities"),
    ("internet broadband wifi jio airtel bsnl", "Utilities"),
    ("mobile phone recharge prepaid postpaid", "Utilities"),
    ("rent lease apartment flat house monthly", "Utilities"),
    ("movie theatre cinema ticket show", "Entertainment"),
    ("netflix amazon prime hotstar subscription ott", "Entertainment"),
    ("spotify music streaming podcast", "Entertainment"),
    ("gaming ps5 xbox steam online game purchase", "Entertainment"),
    ("concert event festival ticket amusement park", "Entertainment"),
    ("gym fitness membership sports club", "Entertainment"),
    ("book reading kindle kindle-unlimited", "Entertainment"),
    ("doctor hospital clinic consultation fee", "Healthcare"),
    ("medicine pharmacy chemist tablet capsule", "Healthcare"),
    ("diagnostic test lab blood report", "Healthcare"),
    ("dental dentist eye optician glasses", "Healthcare"),
    ("insurance health premium policy", "Healthcare"),
    ("surgery operation procedure medical", "Healthcare"),
    ("amazon flipkart online shopping order", "Shopping"),
    ("clothes shirt pants dress shoes footwear", "Shopping"),
    ("electronics mobile laptop gadget phone charger", "Shopping"),
    ("furniture home decor sofa bed mattress", "Shopping"),
    ("jewellery gold silver accessories watch", "Shopping"),
    ("cosmetics beauty salon haircut spa", "Shopping"),
    ("stationery office supplies pen notebook", "Shopping"),
    ("transfer payment fee charge misc", "Other"),
    ("salary income credit deposit", "Other"),
    ("bank charges atm withdrawal cash", "Other"),
    ("investment mutual fund sip stock", "Other"),
    ("loan emi repayment instalment", "Other"),
    ("donation charity gift contribution", "Other"),
    ("tax government fine penalty challan", "Other"),
    ("grocery store weekly shopping essentials", "Groceries"),
    ("fast food takeaway drive-through", "Dining"),
    ("auto fuel service station refuel", "Transport"),
    ("broadband bill monthly subscription", "Utilities"),
    ("online streaming video music plan", "Entertainment"),
    ("netflix hulu disney plus streaming subscription", "Entertainment"),
    ("spotify apple music youtube premium subscription", "Entertainment"),
    ("amazon prime video subscription monthly annual", "Entertainment"),
    ("hbo max paramount peacock streaming service", "Entertainment"),
    ("gaming subscription xbox game pass playstation plus", "Entertainment"),
    ("magazine newspaper digital subscription", "Entertainment"),
    ("medical checkup annual physical health", "Healthcare"),
    ("retail purchase clothing accessory", "Shopping"),
    ("miscellaneous expense sundry charge", "Other"),
]


def _load_kaggle_data() -> list[tuple[str, str]]:
    """Download the Kaggle spending-habits dataset and return (text, label) pairs
    with categories mapped to the app's category set."""
    path = kagglehub.dataset_download(KAGGLE_DATASET)
    csv_path = os.path.join(path, 'spending_patterns_detailed.csv')
    df = pd.read_csv(csv_path)
    pairs: list[tuple[str, str]] = []
    for _, row in df.iterrows():
        kaggle_cat = row['Category']
        mapped = KAGGLE_CATEGORY_MAP.get(kaggle_cat)
        if mapped is None:
            continue
        item = str(row['Item']).strip()
        if not item:
            continue
        pairs.append((item.lower(), mapped))
    return pairs


def _build_pipeline() -> Pipeline:
    return Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)),
        ('clf', LogisticRegression(
            max_iter=2000, C=5.0, solver='lbfgs',
            class_weight='balanced',
        )),
    ])


def train_and_save():
    os.makedirs(MODEL_DIR, exist_ok=True)
    # Combine hand-crafted examples with Kaggle dataset
    all_data = list(TRAINING_DATA)
    try:
        kaggle_pairs = _load_kaggle_data()
        all_data.extend(kaggle_pairs)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning('Kaggle data unavailable, using built-in data only: %s', e)
    texts = [t for t, _ in all_data]
    labels = [l for _, l in all_data]
    pipe = _build_pipeline()
    pipe.fit(texts, labels)
    joblib.dump(pipe, MODEL_PATH)
    return pipe


def _load_model() -> Pipeline:
    if not os.path.exists(MODEL_PATH):
        return train_and_save()
    return joblib.load(MODEL_PATH)


_model = None


def predict_category(description: str) -> str:
    global _model
    if _model is None:
        _model = _load_model()
    prediction = _model.predict([description.lower()])
    return prediction[0]


def predict_category_with_confidence(description: str) -> dict:
    global _model
    if _model is None:
        _model = _load_model()
    text = description.lower()
    proba = _model.predict_proba([text])[0]
    classes = _model.classes_
    top_idx = int(np.argmax(proba))
    return {
        'category': classes[top_idx],
        'confidence': round(float(proba[top_idx]), 3),
        'all_scores': {c: round(float(p), 3) for c, p in zip(classes, proba)},
    }
