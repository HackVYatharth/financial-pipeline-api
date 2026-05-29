from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text

from api.database import engine
from api.models import TopMerchantOut, TransactionOut
from analytics.trends import top_merchants

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=List[TransactionOut])
def list_transactions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
):
    filters = ["1=1"]
    params: dict = {"limit": limit, "offset": offset}

    if category:
        filters.append("merchant_category = :category")
        params["category"] = category
    if status:
        filters.append("status = :status")
        params["status"] = status
    if channel:
        filters.append("channel = :channel")
        params["channel"] = channel

    where = " AND ".join(filters)
    query = text(
        f"SELECT * FROM transactions WHERE {where} "
        "ORDER BY transaction_date DESC LIMIT :limit OFFSET :offset"
    )
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)

    return df.to_dict(orient="records")


@router.get("/top-merchants", response_model=List[TopMerchantOut])
def get_top_merchants(limit: int = Query(20, ge=1, le=100)):
    df = top_merchants(engine=engine, limit=limit)
    return df.to_dict(orient="records")


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: str):
    query = text("SELECT * FROM transactions WHERE transaction_id = :tid")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"tid": transaction_id})
    if df.empty:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return df.iloc[0].to_dict()
