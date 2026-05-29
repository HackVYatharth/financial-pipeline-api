from typing import List

from fastapi import APIRouter, Query

from api.database import engine
from api.models import AnomalyOut, AnomalySummaryOut
from analytics.anomalies import (
    anomaly_summary,
    combined_anomaly_report,
    iqr_anomalies,
    zscore_anomalies,
)

router = APIRouter(prefix="/anomalies", tags=["Anomaly Detection"])


@router.get("/summary", response_model=AnomalySummaryOut)
def get_anomaly_summary():
    return anomaly_summary(engine=engine)


@router.get("/combined", response_model=List[AnomalyOut])
def get_combined_anomalies(
    limit: int = Query(100, ge=1, le=500),
):
    df = combined_anomaly_report(engine=engine).head(limit)
    return df.to_dict(orient="records")


@router.get("/zscore", response_model=List[AnomalyOut])
def get_zscore_anomalies(
    threshold: float = Query(3.0, ge=1.0, le=10.0),
    limit: int = Query(100, ge=1, le=500),
):
    df = zscore_anomalies(threshold=threshold, engine=engine).head(limit)
    df["flagged_by_zscore"] = True
    df["flagged_by_iqr"] = False
    return df.to_dict(orient="records")


@router.get("/iqr", response_model=List[AnomalyOut])
def get_iqr_anomalies(
    multiplier: float = Query(1.5, ge=0.5, le=5.0),
    limit: int = Query(100, ge=1, le=500),
):
    df = iqr_anomalies(multiplier=multiplier, engine=engine).head(limit)
    df["flagged_by_zscore"] = False
    df["flagged_by_iqr"] = True
    return df.to_dict(orient="records")
