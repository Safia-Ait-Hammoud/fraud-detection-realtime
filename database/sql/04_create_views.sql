-- 04_create_views.sql

-- Vue 1 : Volume de transactions par minute (Pour le Panel Grafana "Transactions/seconde")
CREATE OR REPLACE VIEW fraud_detection.vw_transactions_per_minute AS
SELECT 
    TIMESTAMP_TRUNC(processing_timestamp, MINUTE) as processing_minute,
    COUNT(*) as total_transactions
FROM fraud_detection.transactions
GROUP BY processing_minute;

-- Vue 2 : Statistiques de fraude globales (Taux de fraude, Montant moyen)
CREATE OR REPLACE VIEW fraud_detection.vw_fraud_statistics AS
SELECT 
    COUNTIF(is_fraud = TRUE) as total_frauds,
    COUNT(*) as total_transactions,
    (COUNTIF(is_fraud = TRUE) / COUNT(*)) * 100 as fraud_rate_percentage,
    AVG(CASE WHEN is_fraud = TRUE THEN amount ELSE NULL END) as avg_fraudulent_amount
FROM fraud_detection.transactions;

-- Vue 3 : Top des montants frauduleux récents (Pour le Panel Grafana "Top montants")
CREATE OR REPLACE VIEW fraud_detection.vw_recent_top_frauds AS
SELECT 
    transaction_id,
    amount,
    confidence_score,
    processing_timestamp
FROM fraud_detection.transactions
WHERE is_fraud = TRUE
ORDER BY amount DESC, processing_timestamp DESC
LIMIT 50;