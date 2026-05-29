# Financial Transaction Pipeline & Analytics API

![CI](https://github.com/HackVYatharth/financial-pipeline-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A production-grade ETL pipeline and REST analytics API for financial transaction datal/o;

**🔗 Live Project:** [github.com/HackVYatharth/financial-pipeline-api](https://github.com/HackVYatharth/financial-pipeline-api)

---

## Architecture

```
Synthetic Data (Faker)
        │
        ▼
  ┌─────────────┐       ┌─────────────┐       ┌─────────────────┐
  │   Extract   │──────▶│  Transform  │──────▶│  Load (Postgres)│
  │  (extract.py)│      │(transform.py)│      │   (load.py)     │
  └─────────────┘       └─────────────┘       └────────┬────────┘
                                                        │
                                            ┌───────────▼────────────┐
                                            │  Analytical SQL Views  │
                                            │  (monthly, category,   │
                                            │   anomalies, users)    │
                                            └───────────┬────────────┘
                                                        │
                                            ┌───────────▼────────────┐
                                            │     FastAPI Layer       │
                                            │  /transactions          │
                                            │  /analytics             │
                                            │  /anomalies             │
                                            └───────────┬────────────┘
                                                        │
                                            ┌───────────▼────────────┐
                                            │   Apache Airflow DAG   │
                                            │  (daily, 02:00 UTC)    │
                                            └────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data Generation | Python · Faker |
| ETL | Pandas · SQLAlchemy |
| Warehouse | PostgreSQL 15 |
| Analytics | Pandas · NumPy · SciPy |
| API | FastAPI · Pydantic v2 |
| Orchestration | Apache Airflow 2.x |
| Notebooks | JupyterLab · Matplotlib · Seaborn |
| Containers | Docker · Docker Compose |
| Tests | Pytest |

---

## Features

### ETL Pipeline
- Generates **50,000 synthetic transactions** across 500 users, 12 merchant categories, and 4 transaction channels
- ~1% of records are seeded as synthetic anomalies (unusually high amounts)
- Transform stage: deduplication, type casting, date enrichment (year/month/week/quarter/day-of-week), amount bucketing

### Analytics
- **Monthly spend trends** — total spend, transaction count, month-over-month change
- **Category breakdowns** — spend share %, heatmap (category × month)
- **Anomaly detection** — Z-score (per-category, configurable threshold) and IQR (configurable multiplier)
- **User segmentation** — lifetime spend quartile buckets (Bronze → Platinum)
- **Top merchants** by total spend

### FastAPI Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | DB connectivity + transaction count |
| GET | `/transactions/` | Paginated list with filters (category, status, channel) |
| GET | `/transactions/{id}` | Single transaction lookup |
| GET | `/transactions/top-merchants` | Top N merchants by spend |
| GET | `/analytics/monthly-trends` | Spend by month × category |
| GET | `/analytics/monthly-overview` | Overall monthly totals + MoM change |
| GET | `/analytics/weekly-spend` | Weekly aggregates |
| GET | `/analytics/category-breakdown` | Category spend share |
| GET | `/analytics/channel-breakdown` | Online / in-store / mobile / ATM split |
| GET | `/anomalies/summary` | High-level anomaly stats |
| GET | `/anomalies/combined` | Transactions flagged by Z-score OR IQR |
| GET | `/anomalies/zscore` | Z-score anomalies (configurable threshold) |
| GET | `/anomalies/iqr` | IQR anomalies (configurable multiplier) |
| POST | `/pipeline/run` | Manually trigger the ETL pipeline |

### Airflow DAG (`financial_etl_pipeline`)
- Scheduled daily at **02:00 UTC**
- Five tasks: `extract → transform → load → refresh_views → anomaly_alert`
- XCom handoff between tasks; anomaly alert hook (extend to Slack/PagerDuty)

---

## Quick Start

### 1. Docker

```bash
# Clone and start all services (Postgres + API + Airflow)
git clone https://github.com/<your-username>/financial-pipeline-api.git
cd financial-pipeline-api

cp .env.example .env

cd docker
docker compose up --build
```

| Service | URL |
|---|---|
| FastAPI docs | http://localhost:8000/docs |
| Airflow UI | http://localhost:8080 (admin / admin) |
| PostgreSQL | localhost:5432 |

### 2. Local

```bash
# Requires Python 3.11+ and a running PostgreSQL instance
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your Postgres credentials

# Seed the database
python -c "from pipeline.load import run_etl; print(run_etl())"

# Start the API
uvicorn api.main:app --reload

# Open the notebook
cd notebooks && jupyter lab
```

---

## Project Structure

```
financial-pipeline-api/
├── pipeline/
│   ├── config.py          # Env-driven config
│   ├── extract.py         # Faker-based synthetic data generation
│   ├── transform.py       # Cleaning, enrichment, bucketing
│   └── load.py            # PostgreSQL loader + ETL orchestration
├── analytics/
│   ├── trends.py          # Monthly / weekly spend aggregations
│   ├── categories.py      # Category & channel breakdowns
│   └── anomalies.py       # Z-score + IQR anomaly detection
├── api/
│   ├── main.py            # FastAPI app + CORS + health + pipeline trigger
│   ├── database.py        # SQLAlchemy engine + session
│   ├── models.py          # Pydantic response schemas
│   └── routes/
│       ├── transactions.py
│       ├── analytics.py
│       └── anomalies.py
├── airflow/dags/
│   └── etl_pipeline_dag.py
├── notebooks/
│   └── exploratory_analysis.ipynb
├── sql/
│   ├── schema.sql          # DDL + indexes
│   └── analytical_views.sql # 5 reusable SQL views
├── tests/
│   ├── test_pipeline.py
│   └── test_analytics.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Running Tests

```bash
pytest tests/ -v --cov=pipeline --cov=analytics --cov-report=term-missing
```

---

## Anomaly Detection Methods

### Z-Score (per category)
Flags a transaction if its amount is more than `k` standard deviations from the category mean:

```
z = (amount - μ_category) / σ_category
flag if |z| > threshold   (default: 3.0)
```

### IQR (per category)
Flags a transaction outside the whisker bounds:

```
lower = Q1 - k × IQR
upper = Q3 + k × IQR
flag if amount < lower OR amount > upper   (default k: 1.5)
```

Both thresholds are configurable via query parameters on the API and via environment variables.

---

## Sample API Calls

```bash
# Category breakdown
curl http://localhost:8000/analytics/category-breakdown

# Anomaly summary
curl http://localhost:8000/anomalies/summary

# Z-score anomalies with custom threshold
curl "http://localhost:8000/anomalies/zscore?threshold=2.5&limit=50"

# Filter transactions by category and channel
curl "http://localhost:8000/transactions/?category=Travel&channel=online&limit=20"

# Trigger a fresh ETL run
curl -X POST "http://localhost:8000/pipeline/run?num_transactions=10000"
```

---

## 📊 Project Metrics

| Metric | Value |
|--------|-------|
| **Test Coverage** | ~90% target |
| **Default Dataset Size** | 50,000 transactions |
| **Merchant Categories** | 12 |
| **Transaction Channels** | 4 (online, in-store, mobile, ATM) |
| **Anomaly Detection Methods** | 2 (Z-score + IQR) |

---

## 🎓 Learning Outcomes & Interview Value

This project demonstrates:

✅ **ETL Design Patterns** — Modular extract-transform-load with configurable data generation  
✅ **SQL Optimization** — Strategic indexing, analytical views, window functions (LAG for MoM change)  
✅ **Statistical Analysis** — Per-category Z-score and IQR-based anomaly detection  
✅ **API Development** — RESTful design with FastAPI, Pydantic validation, auto-generated docs  
✅ **Workflow Orchestration** — Airflow DAG with task dependencies and XCom state passing  
✅ **Data Visualization** — Jupyter notebook with matplotlib/seaborn (7 chart types)  
✅ **Containerization** — Multi-service Docker Compose stack  
✅ **Testing** — Pytest unit tests with coverage reporting  
✅ **CI/CD** — GitHub Actions pipeline with PostgreSQL service container

---

## 🤝 Contributing

Contributions welcome! Areas for extension:
- Replace Faker with Kafka/Kinesis streaming ingestion
- Add dbt models for SQL transformations
- Implement real-time dashboard with Plotly Dash or Streamlit
- Add authentication (OAuth2, API keys)
- Migrate to BigQuery or Redshift for cloud deployment

---
