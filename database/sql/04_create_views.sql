-- database/sql/04_create_views.sql

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Évolution temporelle (courbe principale du dashboard)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW fraud_detection.vw_fraud_statistics AS
SELECT
    window_start          AS time,
    total_transactions,
    total_frauds,
    fraud_rate_percentage,
    avg_fraudulent_amount,
    avg_processing_latency
FROM
    fraud_detection.fraud_stats
ORDER BY
    window_start DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Dernières fraudes détectées (tableau temps réel)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW fraud_detection.vw_recent_top_frauds AS
SELECT
    processing_timestamp  AS time,
    transaction_id,
    amount,
    merchant_category,
    foreign_transaction,
    location_mismatch,
    device_trust_score,
    velocity_last_24h,    -- FLOAT64 dans le nouveau schéma
    confidence_score
FROM
    fraud_detection.transactions
WHERE
    is_fraud = 1
ORDER BY
    processing_timestamp DESC
LIMIT 100;


-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Répartition de la fraude par catégorie de marchand
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW fraud_detection.vw_fraud_by_merchant AS
SELECT
    merchant_category,
    COUNT(*)       AS fraud_count,
    SUM(amount)    AS total_fraud_amount,
    AVG(amount)    AS avg_fraud_amount,
    AVG(confidence_score) AS avg_confidence
FROM
    fraud_detection.transactions
WHERE
    is_fraud = 1
GROUP BY
    merchant_category
ORDER BY
    fraud_count DESC;


-- ─────────────────────────────────────────────────────────────────────────────
-- 4. Santé globale du pipeline (KPIs résumés)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW fraud_detection.vw_pipeline_health AS
SELECT
    COUNT(*)                                              AS total_transactions,
    COUNTIF(is_fraud = 1)                                 AS total_frauds,
    COUNTIF(is_fraud = 0)                                 AS total_legitimate,
    ROUND(COUNTIF(is_fraud = 1) / COUNT(*) * 100, 4)      AS fraud_rate_pct,
    ROUND(AVG(amount), 2)                                 AS avg_transaction_amount,
    ROUND(AVG(IF(is_fraud = 1, amount, NULL)), 2)         AS avg_fraud_amount,
    ROUND(AVG(confidence_score), 4)                       AS avg_confidence_score,
    MIN(processing_timestamp)                             AS pipeline_start,
    MAX(processing_timestamp)                             AS last_event_received
FROM
    fraud_detection.transactions;


-- ─────────────────────────────────────────────────────────────────────────────
-- 5. Détections par heure de la journée (heatmap comportementale)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW fraud_detection.vw_fraud_by_hour AS
SELECT
    transaction_hour,
    COUNT(*)                                            AS total_transactions,
    COUNTIF(is_fraud = 1)                               AS total_frauds,
    ROUND(COUNTIF(is_fraud = 1) / COUNT(*) * 100, 2)   AS fraud_rate_pct
FROM
    fraud_detection.transactions
GROUP BY
    transaction_hour
ORDER BY
    transaction_hour ASC;


-- ─────────────────────────────────────────────────────────────────────────────
-- 6. Score de risque moyen par catégorie (profil de menace)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW fraud_detection.vw_risk_profile_by_merchant AS
SELECT
    merchant_category,
    COUNT(*)                                            AS total_transactions,
    ROUND(AVG(confidence_score), 4)                     AS avg_confidence_score,
    ROUND(AVG(device_trust_score), 4)                   AS avg_device_trust,
    ROUND(AVG(velocity_last_24h), 2)                    AS avg_velocity,  -- FLOAT64
    COUNTIF(is_fraud = 1)                               AS fraud_count,
    ROUND(COUNTIF(is_fraud = 1) / COUNT(*) * 100, 2)   AS fraud_rate_pct
FROM
    fraud_detection.transactions
GROUP BY
    merchant_category
ORDER BY
    avg_confidence_score DESC;