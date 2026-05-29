import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/finpipeline"
)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "finpipeline")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

NUM_TRANSACTIONS = int(os.getenv("NUM_TRANSACTIONS", "50000"))
ANOMALY_Z_THRESHOLD = float(os.getenv("ANOMALY_Z_THRESHOLD", "3.0"))
ANOMALY_IQR_MULTIPLIER = float(os.getenv("ANOMALY_IQR_MULTIPLIER", "1.5"))

MERCHANT_CATEGORIES = [
    "Groceries", "Restaurants", "Travel", "Entertainment",
    "Healthcare", "Utilities", "Shopping", "Fuel",
    "Subscription", "Transfer", "ATM", "Insurance",
]

TRANSACTION_CHANNELS = ["online", "in-store", "mobile", "ATM"]
