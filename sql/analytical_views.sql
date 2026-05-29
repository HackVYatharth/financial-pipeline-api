-- Analytical views for reporting layer

CREATE OR REPLACE VIEW vw_monthly_category_spend AS
SELECT
    year,
    month,
    TO_CHAR(transaction_date, 'Mon YYYY')   AS month_label,
    merchant_category,
    COUNT(*)                                 AS transaction_count,
    ROUND(SUM(amount)::numeric, 2)           AS total_spend,
    ROUND(AVG(amount)::numeric, 2)           AS avg_spend,
    ROUND(MIN(amount)::numeric, 2)           AS min_spend,
    ROUND(MAX(amount)::numeric, 2)           AS max_spend
FROM transactions
WHERE status = 'completed'
GROUP BY year, month, month_label, merchant_category;

-- -------------------------------------------------------

CREATE OR REPLACE VIEW vw_overall_monthly_spend AS
SELECT
    year,
    month,
    TO_CHAR(transaction_date, 'Mon YYYY')   AS month_label,
    COUNT(*)                                 AS transaction_count,
    ROUND(SUM(amount)::numeric, 2)           AS total_spend,
    ROUND(AVG(amount)::numeric, 2)           AS avg_spend,
    ROUND(
        SUM(amount) - LAG(SUM(amount)) OVER (ORDER BY year, month),
        2
    )                                        AS mom_change
FROM transactions
WHERE status = 'completed'
GROUP BY year, month, month_label;

-- -------------------------------------------------------

CREATE OR REPLACE VIEW vw_category_share AS
SELECT
    merchant_category,
    COUNT(*)                                 AS transaction_count,
    ROUND(SUM(amount)::numeric, 2)           AS total_spend,
    ROUND(
        100.0 * SUM(amount) / SUM(SUM(amount)) OVER (),
        2
    )                                        AS spend_share_pct
FROM transactions
WHERE status = 'completed'
GROUP BY merchant_category
ORDER BY total_spend DESC;

-- -------------------------------------------------------

CREATE OR REPLACE VIEW vw_anomalies AS
SELECT
    t.*,
    stats.cat_mean,
    stats.cat_std,
    ROUND(
        ((t.amount - stats.cat_mean) / NULLIF(stats.cat_std, 0))::numeric,
        4
    ) AS z_score
FROM transactions t
JOIN (
    SELECT
        merchant_category,
        AVG(amount)    AS cat_mean,
        STDDEV(amount) AS cat_std
    FROM transactions
    WHERE status = 'completed'
    GROUP BY merchant_category
) stats USING (merchant_category)
WHERE
    t.status = 'completed'
    AND ABS((t.amount - stats.cat_mean) / NULLIF(stats.cat_std, 0)) > 3;

-- -------------------------------------------------------

CREATE OR REPLACE VIEW vw_user_spend_summary AS
SELECT
    user_id,
    COUNT(*)                         AS total_transactions,
    ROUND(SUM(amount)::numeric, 2)   AS lifetime_spend,
    ROUND(AVG(amount)::numeric, 2)   AS avg_transaction,
    ROUND(MAX(amount)::numeric, 2)   AS largest_transaction,
    MIN(transaction_date)            AS first_transaction,
    MAX(transaction_date)            AS last_transaction,
    COUNT(DISTINCT merchant_category) AS categories_used
FROM transactions
WHERE status = 'completed'
GROUP BY user_id;
