import random
from datetime import datetime, timedelta, timezone
from django.core.management.base import BaseCommand
from django.utils import timezone as dj_timezone
from rest_framework.authtoken.models import Token
from backend.accounts.models import User
from backend.transactions.models import Transaction
from backend.budgets.models import Budget
from backend.db_client import get_collection
from backend.ai_engine.categorizer import train_and_save


SEED_TRANSACTIONS = [
    ("Reliance Fresh groceries", "Groceries", 850),
    ("D-Mart weekly shopping", "Groceries", 1200),
    ("Fruits and vegetables market", "Groceries", 450),
    ("BigBasket online order", "Groceries", 980),
    ("Milk and dairy weekly", "Groceries", 320),
    ("Zomato dinner order", "Dining", 540),
    ("Swiggy lunch delivery", "Dining", 380),
    ("Starbucks coffee", "Dining", 480),
    ("Restaurant dinner outing", "Dining", 1800),
    ("Pizza Hut order", "Dining", 760),
    ("Barista cafe visit", "Dining", 340),
    ("Uber cab to airport", "Transport", 650),
    ("Metro card recharge", "Transport", 500),
    ("Petrol fuel filling", "Transport", 2200),
    ("Ola ride to office", "Transport", 180),
    ("Parking charges mall", "Transport", 120),
    ("Flight ticket Mumbai", "Transport", 4500),
    ("Electricity bill payment", "Utilities", 1850),
    ("Jio broadband monthly", "Utilities", 999),
    ("Airtel mobile recharge", "Utilities", 599),
    ("Water bill municipal", "Utilities", 420),
    ("Gas cylinder LPG", "Utilities", 950),
    ("Netflix subscription", "Entertainment", 649),
    ("BookMyShow movie tickets", "Entertainment", 600),
    ("Spotify premium plan", "Entertainment", 119),
    ("Amazon Prime annual", "Entertainment", 1499),
    ("Gym membership monthly", "Entertainment", 1200),
    ("Doctor consultation fee", "Healthcare", 800),
    ("Apollo pharmacy medicines", "Healthcare", 650),
    ("Diagnostic blood test lab", "Healthcare", 1200),
    ("Dental checkup dentist", "Healthcare", 1500),
    ("Amazon shopping electronics", "Shopping", 3200),
    ("Myntra clothes order", "Shopping", 1800),
    ("Flipkart gadget purchase", "Shopping", 5500),
    ("Lifestyle clothing store", "Shopping", 2200),
    ("Decathlon sports shoes", "Shopping", 3500),
]


class Command(BaseCommand):
    help = 'Seed demo user and transactions into the database'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Delete existing demo data first')

    def handle(self, *args, **options):
        self.stdout.write('Training categorizer model...')
        train_and_save()
        self.stdout.write(self.style.SUCCESS('Categorizer trained.'))

        if options['flush']:
            User.objects.filter(username='demo').delete()
            self.stdout.write('Flushed existing demo user.')

        user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@spendsense.ai',
                'first_name': 'Demo',
                'last_name': 'User',
            },
        )
        if created:
            user.set_password('demo1234')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created demo user: demo / demo1234'))
        else:
            self.stdout.write('Demo user already exists.')

        token, _ = Token.objects.get_or_create(user=user)
        self.stdout.write(f'Auth token: {token.key}')

        Budget.objects.get_or_create(user=user, category='Groceries', period='monthly', defaults={'limit': 5000})
        Budget.objects.get_or_create(user=user, category='Dining', period='monthly', defaults={'limit': 3000})
        Budget.objects.get_or_create(user=user, category='Transport', period='monthly', defaults={'limit': 4000})
        Budget.objects.get_or_create(user=user, category='Entertainment', period='monthly', defaults={'limit': 2000})
        Budget.objects.get_or_create(user=user, category='Shopping', period='monthly', defaults={'limit': 6000})
        self.stdout.write(self.style.SUCCESS('Budgets created.'))

        tx_col = get_collection('transactions')
        now = dj_timezone.now()
        created_count = 0

        for month_offset in range(3):
            month_base = now - timedelta(days=30 * (2 - month_offset))
            entries = random.sample(SEED_TRANSACTIONS, min(20, len(SEED_TRANSACTIONS)))
            for i, (description, category, base_amount) in enumerate(entries):
                amount = round(base_amount * random.uniform(0.8, 1.3), 2)
                date = month_base - timedelta(days=random.randint(0, 27))
                tx = Transaction.objects.create(
                    user=user,
                    amount=amount,
                    category=category,
                    description=description,
                    date=date,
                    auto_categorized=False,
                )
                try:
                    tx_col.update_one(
                        {'django_id': tx.id},
                        {'$set': {
                            'django_id': tx.id,
                            'user_id': str(user.id),
                            'amount': tx.amount,
                            'category': tx.category,
                            'description': tx.description,
                            'date': tx.date.isoformat(),
                            'auto_categorized': False,
                        }},
                        upsert=True,
                    )
                except Exception:
                    pass
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created {created_count} transactions across 3 months.'
        ))
        self.stdout.write(self.style.SUCCESS(
            '\nSeed complete! Test with:\n'
            f'  POST /api/login  {{"username": "demo", "password": "demo1234"}}\n'
            f'  Token: {token.key}'
        ))
