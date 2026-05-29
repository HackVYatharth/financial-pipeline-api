# Setup & Usage Guide

## Prerequisites

- **Python 3.11+** (3.10 works but 3.11+ recommended)
- **Docker & Docker Compose** (for containerized setup)
- **PostgreSQL 15** (if running locally without Docker)
- **Git**

---

## Installation Methods

### Method 1: Docker Compose (Recommended for Demo)

This starts **everything**: PostgreSQL, FastAPI, and Airflow in one command.

```bash
# Clone the repo
git clone https://github.com/HackVYatharth/financial-pipeline-api.git
cd financial-pipeline-api

# Copy environment template
cp .env.example .env

# Start all services
cd docker
docker compose up --build
```

**Wait ~60 seconds** for Airflow to initialize, then access:

| Service | URL | Credentials |
|---------|-----|-------------|
| **FastAPI docs** | http://localhost:8000/docs | None |
| **Airflow UI** | http://localhost:8080 | admin / admin |
| **PostgreSQL** | localhost:5432 | postgres / postgres |

To trigger the ETL pipeline:
- **Via API**: `curl -X POST http://localhost:8000/pipeline/run?num_transactions=50000`
- **Via Airflow**: Enable the `financial_etl_pipeline` DAG in the UI and click "Trigger DAG"

---

### Method 2: Local Development (Python Virtual Environment)

#### Step 1: Install PostgreSQL

**Windows:** Download from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)

**macOS:** `brew install postgresql@15 && brew services start postgresql@15`

**Linux:** `sudo apt-get install postgresql-15`

Create the database:
```bash
psql -U postgres
CREATE DATABASE finpipeline;
\q
```

#### Step 2: Python Setup

```bash
# Clone and navigate
git clone https://github.com/HackVYatharth/financial-pipeline-api.git
cd financial-pipeline-api

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Configure Environment

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials if different from defaults
```

#### Step 4: Seed the Database

```bash
python -c "from pipeline.load import run_etl; print(run_etl(num_transactions=50000))"
```

Expected output:
```
INFO:root:Starting ETL: generating 50000 transactions
INFO:root:Extracted 50000 raw records
INFO:root:Transformed to 50000 records
INFO:root:Schema created / verified
INFO:root:Loaded 45123 completed transactions
{'extracted': 50000, 'transformed': 50000, 'loaded': 45123}
```

#### Step 5: Start the API

```bash
uvicorn api.main:app --reload
```

Access at http://localhost:8000/docs

---

## Running the Jupyter Notebook

```bash
# Ensure virtual environment is active
cd notebooks
jupyter lab
```

Open [`exploratory_analysis.ipynb`](notebooks/exploratory_analysis.ipynb) and run all cells. It generates:
- Monthly spend trends (line + bar charts)
- Category breakdown (pie + horizontal bar)
- Channel distribution (3-panel bar chart)
- Anomaly scatter plots (Z-score vs IQR)
- Category × Month heatmap
- User segmentation (quartile buckets)

All charts are saved as PNG files in the `notebooks/` directory.

---

## Airflow Setup (Local, without Docker)

**WARNING:** Airflow on Windows requires WSL or a Linux VM. macOS/Linux only for native install.

```bash
pip install apache-airflow==2.8.1

export AIRFLOW_HOME=~/airflow
airflow db init
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@localhost

# Copy DAGs
mkdir -p ~/airflow/dags
cp airflow/dags/etl_pipeline_dag.py ~/airflow/dags/

# Start Airflow webserver (one terminal)
airflow webserver --port 8080

# Start Airflow scheduler (another terminal)
airflow scheduler
```

---

## Running Tests

```bash
# Full test suite with coverage
pytest tests/ -v --cov=pipeline --cov=analytics --cov-report=html

# View HTML coverage report
# Windows: start htmlcov/index.html
# macOS: open htmlcov/index.html
# Linux: xdg-open htmlcov/index.html
```

Expected: **~90% coverage** across pipeline and analytics modules.

---

## Common API Workflows

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Run ETL and Verify
```bash
# Trigger ETL
curl -X POST "http://localhost:8000/pipeline/run?num_transactions=10000"

# Check transaction count
curl http://localhost:8000/health | jq '.transaction_count'

# Get recent transactions
curl "http://localhost:8000/transactions/?limit=5" | jq '.[].merchant_name'
```

### 3. Analytics Queries
```bash
# Monthly overview
curl http://localhost:8000/analytics/monthly-overview | jq

# Category spend share
curl http://localhost:8000/analytics/category-breakdown | jq '.[] | {category: .merchant_category, share: .spend_share_pct}'

# Top 10 merchants
curl http://localhost:8000/transactions/top-merchants?limit=10 | jq
```

### 4. Anomaly Detection
```bash
# Summary stats
curl http://localhost:8000/anomalies/summary | jq

# Get Z-score anomalies with stricter threshold
curl "http://localhost:8000/anomalies/zscore?threshold=2.5&limit=20" | jq '.[] | {merchant: .merchant_name, amount: .amount, z_score: .z_score}'

# Combined (Z-score OR IQR)
curl http://localhost:8000/anomalies/combined?limit=50 | jq
```

---

## Troubleshooting

### `psycopg2` install fails
**Windows:** Install Microsoft C++ Build Tools from [visualstudio.microsoft.com](https://visualstudio.microsoft.com/downloads/)

**Alternative:** Use `psycopg2-binary` (already in `requirements.txt`)

### Port 5432 already in use
Another PostgreSQL instance is running. Either:
- Stop it: `sudo systemctl stop postgresql` (Linux) or Services panel (Windows)
- Change `DB_PORT` in `.env` to 5433 and update your Postgres config

### Docker Compose hangs on Airflow init
Increase Docker memory limit to **4GB+** in Docker Desktop settings.

### `ModuleNotFoundError` when running tests
Ensure you're in the project root and virtual environment is active:
```bash
cd financial-pipeline-api
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pytest tests/
```

---

## Next Steps for Extension

### 1. Add Real-Time Streaming
Replace batch Faker generation with **Kafka** or **AWS Kinesis** for streaming ingestion.

### 2. Swap PostgreSQL for BigQuery
Update `DATABASE_URL` in `.env`:
```
DATABASE_URL=bigquery://project-id/dataset-name
```
Requires `pip install sqlalchemy-bigquery` and GCP service account key.

### 3. Add dbt for Transformation
Move SQL views from `sql/analytical_views.sql` into dbt models for version-controlled, tested transformations.

### 4. Deploy to Cloud
- **API**: Deploy FastAPI on **Render**, **Railway**, or **AWS ECS**
- **Airflow**: Use **Google Cloud Composer** or **AWS MWAA** (Managed Airflow)
- **Database**: Migrate to **RDS PostgreSQL** or **Cloud SQL**

### 5. Add Authentication
Integrate **OAuth2** or **API keys** using FastAPI's `Security` dependency.

---

## Interview Talking Points

When discussing this project in **Deloitte / ZS / Mastercard** interviews:

1. **ETL Design**: "I used a modular extract-transform-load pattern with configurable synthetic data generation via Faker. The transform layer enriches raw transactions with date parts and amount buckets for efficient analytical queries."

2. **Anomaly Detection**: "I implemented two statistical methods — Z-score for parametric outliers and IQR for distribution-free detection. Both are per-category to avoid false positives from cross-category variance. Thresholds are exposed as API query parameters for business user control."

3. **Orchestration**: "The Airflow DAG runs daily at 02:00 UTC with five tasks in a dependency chain. I used XCom for inter-task state passing and built an anomaly alert hook that's ready for Slack or PagerDuty integration."

4. **API Design**: "I chose FastAPI for automatic OpenAPI docs, Pydantic validation, and async support. The endpoint structure mirrors common analytics questions — monthly trends, category breakdowns, and drill-downs into anomalies."

5. **Scalability**: "The PostgreSQL schema uses six indexes on high-cardinality columns (date, category, user). For 10M+ rows, I'd migrate to Redshift or BigQuery and replace Airflow with dbt for SQL-based transformations."

6. **Production Readiness**: "I wrote Pytest unit tests covering the ETL logic and anomaly detection. The Docker Compose setup mirrors a production stack. For deployment, I'd add logging (structlog), metrics (Prometheus), and secret management (AWS Secrets Manager)."

---

## License

MIT — Free to use for portfolio, learning, and commercial projects.

Built to demonstrate **data engineering + analytics** skills for fintech consulting roles.
