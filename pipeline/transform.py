"""Data cleaning and transformation layer."""

import pandas as pd


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["transaction_id"])
    df = df[df["amount"] > 0]
    df = df[df["status"].isin(["completed", "pending", "failed"])]
    df["merchant_name"] = df["merchant_name"].str.strip().str.title()
    df["city"] = df["city"].str.strip().str.title()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    return df


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    df["year"] = df["transaction_date"].dt.year
    df["month"] = df["transaction_date"].dt.month
    df["month_name"] = df["transaction_date"].dt.strftime("%B")
    df["week"] = df["transaction_date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["transaction_date"].dt.day_name()
    df["hour"] = df["transaction_date"].dt.hour
    df["quarter"] = df["transaction_date"].dt.quarter
    df["is_weekend"] = df["transaction_date"].dt.dayofweek >= 5
    df["amount_bucket"] = pd.cut(
        df["amount"],
        bins=[0, 25, 75, 200, 500, float("inf")],
        labels=["micro", "small", "medium", "large", "xlarge"],
    )
    return df


def _flag_failed(df: pd.DataFrame) -> pd.DataFrame:
    df["is_failed"] = df["status"] == "failed"
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Full transform chain: clean → enrich → flag."""
    df = _clean(df)
    df = _enrich(df)
    df = _flag_failed(df)
    return df
