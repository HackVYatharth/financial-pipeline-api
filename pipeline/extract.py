"""Synthetic financial transaction data generator using Faker."""

import random
import uuid
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

from pipeline.config import (
    MERCHANT_CATEGORIES,
    NUM_TRANSACTIONS,
    TRANSACTION_CHANNELS,
)

fake = Faker()
Faker.seed(42)
random.seed(42)

MERCHANTS = {
    "Groceries": ["Whole Foods", "Trader Joe's", "Kroger", "Safeway", "Costco"],
    "Restaurants": ["McDonald's", "Chipotle", "Subway", "Starbucks", "Olive Garden"],
    "Travel": ["Delta Airlines", "Marriott", "Airbnb", "Uber", "Lyft"],
    "Entertainment": ["Netflix", "Spotify", "AMC Theatres", "Steam", "Disney+"],
    "Healthcare": ["CVS Pharmacy", "Walgreens", "Mayo Clinic", "Quest Diagnostics"],
    "Utilities": ["AT&T", "Comcast", "PG&E", "National Grid", "Water Corp"],
    "Shopping": ["Amazon", "Target", "Walmart", "Best Buy", "Macy's"],
    "Fuel": ["Shell", "Chevron", "BP", "ExxonMobil", "Sunoco"],
    "Subscription": ["Adobe Creative", "Microsoft 365", "Hulu", "Audible"],
    "Transfer": ["Venmo", "Zelle", "PayPal", "Cash App"],
    "ATM": ["Chase ATM", "Wells Fargo ATM", "Bank of America ATM"],
    "Insurance": ["State Farm", "Geico", "Allstate", "Progressive"],
}

AMOUNT_RANGES = {
    "Groceries": (15, 250),
    "Restaurants": (8, 120),
    "Travel": (50, 1500),
    "Entertainment": (5, 80),
    "Healthcare": (10, 500),
    "Utilities": (30, 300),
    "Shopping": (10, 800),
    "Fuel": (20, 120),
    "Subscription": (5, 60),
    "Transfer": (10, 2000),
    "ATM": (20, 500),
    "Insurance": (50, 400),
}


def _generate_transaction(transaction_date: datetime, user_id: str) -> dict:
    category = random.choice(MERCHANT_CATEGORIES)
    merchant = random.choice(MERCHANTS[category])
    low, high = AMOUNT_RANGES[category]

    # Inject synthetic anomalies (~1% of transactions)
    is_anomaly = random.random() < 0.01
    if is_anomaly:
        amount = round(random.uniform(high * 3, high * 10), 2)
    else:
        amount = round(random.uniform(low, high), 2)

    return {
        "transaction_id": str(uuid.uuid4()),
        "user_id": user_id,
        "merchant_name": merchant,
        "merchant_category": category,
        "amount": amount,
        "currency": "USD",
        "transaction_date": transaction_date,
        "channel": random.choice(TRANSACTION_CHANNELS),
        "status": random.choices(
            ["completed", "pending", "failed"],
            weights=[90, 7, 3],
        )[0],
        "city": fake.city(),
        "country": "US",
        "is_flagged": is_anomaly,
    }


def extract(num_transactions: int = NUM_TRANSACTIONS) -> pd.DataFrame:
    """Generate synthetic financial transactions spanning the last 12 months."""
    user_ids = [str(uuid.uuid4()) for _ in range(500)]
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    records = []
    for _ in range(num_transactions):
        days_offset = random.randint(0, 365)
        txn_date = start_date + timedelta(days=days_offset, seconds=random.randint(0, 86400))
        user_id = random.choice(user_ids)
        records.append(_generate_transaction(txn_date, user_id))

    df = pd.DataFrame(records)
    df = df.sort_values("transaction_date").reset_index(drop=True)
    return df
