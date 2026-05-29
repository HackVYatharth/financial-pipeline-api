"""Unit tests for anomaly detection logic (no DB required)."""

import pandas as pd
import numpy as np
import pytest

from pipeline.extract import extract
from pipeline.transform import transform
from analytics.anomalies import zscore_anomalies, iqr_anomalies


@pytest.fixture(scope="module")
def sample_df():
    raw = extract(num_transactions=2000)
    return transform(raw)


class TestZScoreAnomalies:
    def test_returns_dataframe(self, sample_df):
        result = zscore_anomalies(df=sample_df, threshold=3.0)
        assert isinstance(result, pd.DataFrame)

    def test_flagged_have_high_zscore(self, sample_df):
        result = zscore_anomalies(df=sample_df, threshold=3.0)
        if not result.empty:
            assert (result["z_score"].abs() > 3.0).all()

    def test_lower_threshold_finds_more(self, sample_df):
        strict = zscore_anomalies(df=sample_df, threshold=3.0)
        loose = zscore_anomalies(df=sample_df, threshold=2.0)
        assert len(loose) >= len(strict)

    def test_result_subset_of_input(self, sample_df):
        completed = sample_df[sample_df["status"] == "completed"]
        result = zscore_anomalies(df=sample_df, threshold=3.0)
        assert set(result["transaction_id"]).issubset(set(completed["transaction_id"]))


class TestIQRAnomalies:
    def test_returns_dataframe(self, sample_df):
        result = iqr_anomalies(df=sample_df, multiplier=1.5)
        assert isinstance(result, pd.DataFrame)

    def test_smaller_multiplier_finds_more(self, sample_df):
        strict = iqr_anomalies(df=sample_df, multiplier=3.0)
        loose = iqr_anomalies(df=sample_df, multiplier=1.0)
        assert len(loose) >= len(strict)

    def test_synthetic_anomaly_detected(self):
        """Inject a known extreme value and verify detection."""
        data = pd.DataFrame({
            "transaction_id": [f"t{i}" for i in range(101)],
            "user_id": ["u1"] * 101,
            "merchant_category": ["Groceries"] * 101,
            "amount": [50.0] * 100 + [50000.0],
            "status": ["completed"] * 101,
        })
        result = iqr_anomalies(df=data, multiplier=1.5)
        assert "t100" in result["transaction_id"].values
