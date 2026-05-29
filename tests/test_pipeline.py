"""Unit tests for extract and transform pipeline stages."""

import pandas as pd
import pytest

from pipeline.extract import extract
from pipeline.transform import transform


@pytest.fixture(scope="module")
def raw_df():
    return extract(num_transactions=500)


@pytest.fixture(scope="module")
def transformed_df(raw_df):
    return transform(raw_df)


class TestExtract:
    def test_returns_dataframe(self, raw_df):
        assert isinstance(raw_df, pd.DataFrame)

    def test_row_count(self, raw_df):
        assert len(raw_df) == 500

    def test_required_columns(self, raw_df):
        required = {
            "transaction_id", "user_id", "merchant_name", "merchant_category",
            "amount", "currency", "transaction_date", "channel", "status",
        }
        assert required.issubset(raw_df.columns)

    def test_no_negative_amounts(self, raw_df):
        assert (raw_df["amount"] > 0).all()

    def test_valid_statuses(self, raw_df):
        assert raw_df["status"].isin(["completed", "pending", "failed"]).all()

    def test_unique_transaction_ids(self, raw_df):
        assert raw_df["transaction_id"].is_unique

    def test_currency_is_usd(self, raw_df):
        assert (raw_df["currency"] == "USD").all()


class TestTransform:
    def test_returns_dataframe(self, transformed_df):
        assert isinstance(transformed_df, pd.DataFrame)

    def test_enriched_columns_present(self, transformed_df):
        for col in ["year", "month", "week", "day_of_week", "hour", "quarter",
                    "is_weekend", "amount_bucket", "is_failed"]:
            assert col in transformed_df.columns, f"Missing column: {col}"

    def test_transaction_date_is_datetime(self, transformed_df):
        assert pd.api.types.is_datetime64_any_dtype(transformed_df["transaction_date"])

    def test_no_duplicates(self, transformed_df):
        assert not transformed_df.duplicated(subset=["transaction_id"]).any()

    def test_is_failed_matches_status(self, transformed_df):
        failed_mask = transformed_df["status"] == "failed"
        assert (transformed_df.loc[failed_mask, "is_failed"]).all()
        assert not (transformed_df.loc[~failed_mask, "is_failed"]).any()

    def test_month_range(self, transformed_df):
        assert transformed_df["month"].between(1, 12).all()

    def test_quarter_range(self, transformed_df):
        assert transformed_df["quarter"].between(1, 4).all()

    def test_amount_bucket_categories(self, transformed_df):
        valid = {"micro", "small", "medium", "large", "xlarge", "nan"}
        actual = set(transformed_df["amount_bucket"].astype(str).unique())
        assert actual.issubset(valid)
