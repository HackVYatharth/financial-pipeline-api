"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from api.database import engine
from api.models import ETLRunOut, HealthOut
from api.routes import analytics, anomalies, transactions

app = FastAPI(
    title="Financial Pipeline Analytics API",
    description=(
        "ETL-powered REST API for financial transaction analytics: "
        "spend trends, category breakdowns, and statistical anomaly detection."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(anomalies.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Financial Pipeline Analytics API",
        "docs": "/docs",
        "endpoints": ["/transactions", "/analytics", "/anomalies"],
    }


@app.get("/health", response_model=HealthOut, tags=["Health"])
def health():
    try:
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM transactions")).scalar()
        return HealthOut(status="ok", db_connected=True, transaction_count=count)
    except Exception:
        return HealthOut(status="degraded", db_connected=False)


@app.post("/pipeline/run", response_model=ETLRunOut, tags=["Pipeline"])
def trigger_etl(num_transactions: int = 50000):
    """Manually trigger the ETL pipeline via HTTP POST."""
    from pipeline.load import run_etl

    result = run_etl(num_transactions=num_transactions)
    return ETLRunOut(
        status="success",
        message=f"ETL completed: {result['loaded']} transactions loaded",
        **result,
    )
