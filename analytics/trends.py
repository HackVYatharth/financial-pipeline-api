"""Monthly and weekly spend trend analytics."""

import pandas as pd
from sqlalchemy import create_engine, text

from pipeline.config import DATABASE_URL


def _engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def monthly_spend_trends(engine=None) -> pd.DataFrame:
    """Aggregate spend by year-month, broken down by category."""
    if engine is None:
        engine = _engine()
    query = text("""
        SELECT
            year,
            month,
            TO_CHAR(transaction_date, 'Mon YYYY') AS month_label,
            merchant_category,
            COUNT(*)                             AS transaction_count,
            ROUND(SUM(amount)::numeric, 2)       AS total_spend,
            ROUND(AVG(amount)::numeric, 2)       AS avg_spend,
            ROUND(MIN(amount)::numeric, 2)       AS min_spend,
            ROUND(MAX(amount)::numeric, 2)       AS max_spend
        FROM transactions
        WHERE status = 'completed'
        GROUP BY year, month, month_label, merchant_category
        ORDER BY year, month, merchant_category
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def overall_monthly_trends(engine=None) -> pd.DataFrame:
    """Total spend and transaction count per month (all categories)."""
    if engine is None:
        engine = _engine()
    query = text("""
        SELECT
            year,
            month,
            TO_CHAR(transaction_date, 'Mon YYYY') AS month_label,
            COUNT(*)                              AS transaction_count,
            ROUND(SUM(amount)::numeric, 2)        AS total_spend,
            ROUND(AVG(amount)::numeric, 2)        AS avg_spend
        FROM transactions
        WHERE status = 'completed'
        GROUP BY year, month, month_label
        ORDER BY year, month
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def weekly_spend(engine=None) -> pd.DataFrame:
    if engine is None:
        engine = _engine()
    query = text("""
        SELECT
            year,
            week,
            COUNT(*)                        AS transaction_count,
            ROUND(SUM(amount)::numeric, 2)  AS total_spend
        FROM transactions
        WHERE status = 'completed'
        GROUP BY year, week
        ORDER BY year, week
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def top_merchants(engine=None, limit: int = 20) -> pd.DataFrame:
    if engine is None:
        engine = _engine()
    query = text(f"""
        SELECT
            merchant_name,
            merchant_category,
            COUNT(*)                        AS transaction_count,
            ROUND(SUM(amount)::numeric, 2)  AS total_spend,
            ROUND(AVG(amount)::numeric, 2)  AS avg_spend
        FROM transactions
        WHERE status = 'completed'
        GROUP BY merchant_name, merchant_category
        ORDER BY total_spend DESC
        LIMIT {limit}
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)
