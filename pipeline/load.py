"""Load transformed data into PostgreSQL."""

import logging

import pandas as pd
from sqlalchemy import create_engine, text

from pipeline.config import DATABASE_URL

logger = logging.getLogger(__name__)


def _get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def create_schema(engine=None) -> None:
    """Create tables if they don't exist."""
    if engine is None:
        engine = _get_engine()
    with open("sql/schema.sql") as f:
        ddl = f.read()
    with engine.begin() as conn:
        conn.execute(text(ddl))
    logger.info("Schema created / verified")


def load(df: pd.DataFrame, engine=None, if_exists: str = "append") -> int:
    """Load DataFrame into the transactions table. Returns rows inserted."""
    if engine is None:
        engine = _get_engine()

    completed = df[df["status"] == "completed"].copy()

    cols = [
        "transaction_id", "user_id", "merchant_name", "merchant_category",
        "amount", "currency", "transaction_date", "channel", "status",
        "city", "country", "is_flagged", "year", "month", "week",
        "day_of_week", "hour", "quarter", "is_weekend", "amount_bucket",
        "is_failed",
    ]
    completed["amount_bucket"] = completed["amount_bucket"].astype(str)

    completed[cols].to_sql(
        "transactions",
        engine,
        if_exists=if_exists,
        index=False,
        method="multi",
        chunksize=1000,
    )
    logger.info("Loaded %d completed transactions", len(completed))
    return len(completed)


def run_etl(num_transactions: int = None) -> dict:
    """Full ETL run: extract → transform → load."""
    from pipeline.extract import extract
    from pipeline.transform import transform
    from pipeline.config import NUM_TRANSACTIONS

    n = num_transactions or NUM_TRANSACTIONS
    logger.info("Starting ETL: generating %d transactions", n)

    raw = extract(n)
    logger.info("Extracted %d raw records", len(raw))

    cleaned = transform(raw)
    logger.info("Transformed to %d records", len(cleaned))

    engine = _get_engine()
    create_schema(engine)
    rows = load(cleaned, engine, if_exists="replace")

    return {"extracted": len(raw), "transformed": len(cleaned), "loaded": rows}
