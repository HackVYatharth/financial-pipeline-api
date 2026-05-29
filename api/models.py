"""Pydantic response schemas for the FastAPI layer."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TransactionOut(BaseModel):
    transaction_id: str
    user_id: str
    merchant_name: str
    merchant_category: str
    amount: float
    currency: str
    transaction_date: datetime
    channel: str
    status: str
    city: str
    country: str
    is_flagged: bool
    year: Optional[int] = None
    month: Optional[int] = None
    quarter: Optional[int] = None
    amount_bucket: Optional[str] = None

    class Config:
        from_attributes = True


class MonthlyTrendOut(BaseModel):
    year: int
    month: int
    month_label: str
    merchant_category: str
    transaction_count: int
    total_spend: float
    avg_spend: float
    min_spend: float
    max_spend: float


class OverallMonthlyTrendOut(BaseModel):
    year: int
    month: int
    month_label: str
    transaction_count: int
    total_spend: float
    avg_spend: float


class CategoryBreakdownOut(BaseModel):
    merchant_category: str
    transaction_count: int
    total_spend: float
    avg_spend: float
    spend_share_pct: float


class AnomalyOut(BaseModel):
    transaction_id: str
    user_id: str
    merchant_name: str
    merchant_category: str
    amount: float
    transaction_date: datetime
    flagged_by_zscore: bool
    flagged_by_iqr: bool
    z_score: Optional[float] = None
    category_mean: Optional[float] = None
    category_std: Optional[float] = None


class AnomalySummaryOut(BaseModel):
    total_anomalies: int
    zscore_only: int
    iqr_only: int
    both_methods: int
    total_anomalous_spend: float
    avg_anomalous_amount: float
    top_category: str


class TopMerchantOut(BaseModel):
    merchant_name: str
    merchant_category: str
    transaction_count: int
    total_spend: float
    avg_spend: float


class ETLRunOut(BaseModel):
    status: str
    extracted: int
    transformed: int
    loaded: int
    message: str


class HealthOut(BaseModel):
    status: str
    db_connected: bool
    transaction_count: int = Field(default=0)
