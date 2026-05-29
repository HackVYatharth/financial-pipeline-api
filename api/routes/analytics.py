from typing import List

from fastapi import APIRouter

from api.database import engine
from api.models import (
    CategoryBreakdownOut,
    MonthlyTrendOut,
    OverallMonthlyTrendOut,
)
from analytics.categories import category_breakdown, channel_breakdown
from analytics.trends import monthly_spend_trends, overall_monthly_trends, weekly_spend

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/monthly-trends", response_model=List[MonthlyTrendOut])
def get_monthly_trends():
    df = monthly_spend_trends(engine=engine)
    return df.to_dict(orient="records")


@router.get("/monthly-overview", response_model=List[OverallMonthlyTrendOut])
def get_monthly_overview():
    df = overall_monthly_trends(engine=engine)
    return df.to_dict(orient="records")


@router.get("/weekly-spend")
def get_weekly_spend():
    df = weekly_spend(engine=engine)
    return df.to_dict(orient="records")


@router.get("/category-breakdown", response_model=List[CategoryBreakdownOut])
def get_category_breakdown():
    df = category_breakdown(engine=engine)
    return df.to_dict(orient="records")


@router.get("/channel-breakdown")
def get_channel_breakdown():
    df = channel_breakdown(engine=engine)
    return df.to_dict(orient="records")
