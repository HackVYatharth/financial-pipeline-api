-- Financial Pipeline: Core schema

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id   TEXT        PRIMARY KEY,
    user_id          TEXT        NOT NULL,
    merchant_name    TEXT        NOT NULL,
    merchant_category TEXT       NOT NULL,
    amount           NUMERIC(12, 2) NOT NULL,
    currency         CHAR(3)     NOT NULL DEFAULT 'USD',
    transaction_date TIMESTAMPTZ NOT NULL,
    channel          TEXT        NOT NULL,
    status           TEXT        NOT NULL CHECK (status IN ('completed','pending','failed')),
    city             TEXT,
    country          CHAR(2),
    is_flagged       BOOLEAN     NOT NULL DEFAULT FALSE,
    year             INTEGER,
    month            INTEGER,
    week             INTEGER,
    day_of_week      TEXT,
    hour             INTEGER,
    quarter          INTEGER,
    is_weekend       BOOLEAN,
    amount_bucket    TEXT,
    is_failed        BOOLEAN,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_txn_date       ON transactions (transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_txn_category   ON transactions (merchant_category);
CREATE INDEX IF NOT EXISTS idx_txn_user       ON transactions (user_id);
CREATE INDEX IF NOT EXISTS idx_txn_status     ON transactions (status);
CREATE INDEX IF NOT EXISTS idx_txn_year_month ON transactions (year, month);
CREATE INDEX IF NOT EXISTS idx_txn_flagged    ON transactions (is_flagged) WHERE is_flagged = TRUE;
