"""Anomaly detection using Z-score and IQR-based statistical thresholds."""

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from pipeline.config import (
    ANOMALY_IQR_MULTIPLIER,
    ANOMALY_Z_THRESHOLD,
    DATABASE_URL,
)


def _engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)


def _load_transactions(engine) -> pd.DataFrame:
    query = text("SELECT * FROM transactions WHERE status = 'completed'")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)


def zscore_anomalies(
    df: pd.DataFrame | None = None,
    threshold: float = ANOMALY_Z_THRESHOLD,
    engine=None,
) -> pd.DataFrame:
    """Flag transactions whose Z-score (per category) exceeds threshold."""
    if df is None:
        engine = engine or _engine()
        df = _load_transactions(engine)

    result = df.copy()
    result["z_score"] = (
        result.groupby("merchant_category")["amount"]
        .transform(lambda s: (s - s.mean()) / s.std())
    )
    result["zscore_anomaly"] = result["z_score"].abs() > threshold
    return result[result["zscore_anomaly"]].sort_values("z_score", ascending=False)


def iqr_anomalies(
    df: pd.DataFrame | None = None,
    multiplier: float = ANOMALY_IQR_MULTIPLIER,
    engine=None,
) -> pd.DataFrame:
    """Flag transactions outside [Q1 - k*IQR, Q3 + k*IQR] per category."""
    if df is None:
        engine = engine or _engine()
        df = _load_transactions(engine)

    result = df.copy()
    result["iqr_anomaly"] = False

    for category in result["merchant_category"].unique():
        mask = result["merchant_category"] == category
        amounts = result.loc[mask, "amount"]

        q1 = amounts.quantile(0.25)
        q3 = amounts.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr

        anomaly_mask = (amounts < lower) | (amounts > upper)
        result.loc[mask & anomaly_mask, "iqr_anomaly"] = True

    return result[result["iqr_anomaly"]].sort_values("amount", ascending=False)


def combined_anomaly_report(engine=None) -> pd.DataFrame:
    """Return transactions flagged by either Z-score OR IQR method."""
    engine = engine or _engine()
    df = _load_transactions(engine)

    z_ids = set(zscore_anomalies(df)["transaction_id"])
    iqr_ids = set(iqr_anomalies(df)["transaction_id"])
    flagged_ids = z_ids | iqr_ids

    report = df[df["transaction_id"].isin(flagged_ids)].copy()
    report["flagged_by_zscore"] = report["transaction_id"].isin(z_ids)
    report["flagged_by_iqr"] = report["transaction_id"].isin(iqr_ids)

    group = df.groupby("merchant_category")["amount"]
    report["category_mean"] = report["merchant_category"].map(group.mean())
    report["category_std"] = report["merchant_category"].map(group.std())
    report["z_score"] = (report["amount"] - report["category_mean"]) / report["category_std"]

    return report.sort_values("amount", ascending=False)


def anomaly_summary(engine=None) -> dict:
    """High-level anomaly stats for the API summary endpoint."""
    engine = engine or _engine()
    report = combined_anomaly_report(engine)
    return {
        "total_anomalies": len(report),
        "zscore_only": int(report["flagged_by_zscore"].sum()),
        "iqr_only": int(report["flagged_by_iqr"].sum()),
        "both_methods": int((report["flagged_by_zscore"] & report["flagged_by_iqr"]).sum()),
        "total_anomalous_spend": round(float(report["amount"].sum()), 2),
        "avg_anomalous_amount": round(float(report["amount"].mean()), 2),
        "top_category": report.groupby("merchant_category")["amount"].sum().idxmax(),
    }
