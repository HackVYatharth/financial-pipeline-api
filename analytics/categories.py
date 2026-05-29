"""Merchant category breakdown analytics."""

import pandas as pd
from sqlalchemy import create_engine, text

from pipeline.config import DATABASE_URL


def _engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def category_breakdown(engine=None) -> pd.DataFrame:
    """Spend share and transaction count per merchant category."""
    if engine is None:
        engine = _engine()
    query = text("""
        SELECT
            merchant_category,
            COUNT(*)                                  AS transaction_count,
            ROUND(SUM(amount)::numeric, 2)            AS total_spend,
            ROUND(AVG(amount)::numeric, 2)            AS avg_spend,
            ROUND(
                100.0 * SUM(amount) / SUM(SUM(amount)) OVER (),
                2
            )                                         AS spend_share_pct
        FROM transactions
        WHERE status = 'completed'
        GROUP BY merchant_category
        ORDER BY total_spend DESC
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def category_monthly_heatmap(engine=None) -> pd.DataFrame:
    """Category x month spend matrix (wide format for heatmap)."""
    if engine is None:
        engine = _engine()
    query = text("""
        SELECT
            merchant_category,
            year,
            month,
            ROUND(SUM(amount)::numeric, 2) AS total_spend
        FROM transactions
        WHERE status = 'completed'
        GROUP BY merchant_category, year, month
        ORDER BY merchant_category, year, month
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    df["period"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
    pivot = df.pivot_table(
        index="merchant_category", columns="period", values="total_spend", fill_value=0
    )
    return pivot.reset_index()


def channel_breakdown(engine=None) -> pd.DataFrame:
    if engine is None:
        engine = _engine()
    query = text("""
        SELECT
            channel,
            COUNT(*)                       AS transaction_count,
            ROUND(SUM(amount)::numeric, 2) AS total_spend,
            ROUND(AVG(amount)::numeric, 2) AS avg_spend
        FROM transactions
        WHERE status = 'completed'
        GROUP BY channel
        ORDER BY total_spend DESC
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)
