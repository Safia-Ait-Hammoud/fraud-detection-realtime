-- database/sql/04_create_views.sql

-- 1. Vue pour la courbe d'évolution temporelle
CREATE OR REPLACE VIEW fraud_detection.vw_fraud_statistics AS
SELECT 
    window_start as time,
    total_transactions,
    total_frauds,
    fraud_rate_percentage,
    avg_fraudulent_amount
FROM 
    fraud_detection.fraud_stats
ORDER BY 
    window_start DESC;

-- 2. Vue pour le tableau des fraudes récentes
CREATE OR REPLACE VIEW fraud_detection.vw_recent_top_frauds AS
SELECT 
    processing_timestamp as time,
    transaction_id,
    amount,
    merchant_category,
    foreign_transaction,
    confidence_score
FROM 
    fraud_detection.transactions
WHERE 
    is_fraud = 1
ORDER BY 
    processing_timestamp DESC
LIMIT 100;

-- 3. NOUVELLE VUE : Répartition de la fraude par catégorie de marchand
CREATE OR REPLACE VIEW fraud_detection.vw_fraud_by_merchant AS
SELECT 
    merchant_category,
    COUNT(*) as fraud_count,
    SUM(amount) as total_fraud_amount
FROM 
    fraud_detection.transactions
WHERE 
    is_fraud = 1
GROUP BY 
    merchant_category
ORDER BY 
    fraud_count DESC;