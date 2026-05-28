-- database/sql/02_create_tables.sql

-- 1. Création de la table principale qui stockera le flux temps réel
CREATE TABLE IF NOT EXISTS fraud_detection.transactions (
    transaction_id STRING NOT NULL,
    timestamp STRING,
    amount FLOAT64,
    transaction_hour INT64,
    merchant_category STRING,
    foreign_transaction INT64,
    location_mismatch INT64,
    device_trust_score FLOAT64,
    velocity_last_24h INT64,
    cardholder_age INT64,
    
    -- Résultats de l'inférence ML
    is_fraud INT64,
    confidence_score FLOAT64,
    
    -- Métadonnées du pipeline
    processing_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(processing_timestamp)
-- Le clustering sur la catégorie de marchand optimisera les requêtes du dashboard
CLUSTER BY is_fraud, merchant_category; 


-- 2. Création de la table d'agrégation pour les statistiques en temps réel
CREATE TABLE IF NOT EXISTS fraud_detection.fraud_stats (
    window_start TIMESTAMP NOT NULL,          
    window_end TIMESTAMP NOT NULL,            
    
    -- Métriques pour le dashboard Grafana
    total_transactions INT64 DEFAULT 0,       
    total_frauds INT64 DEFAULT 0,             
    fraud_rate_percentage FLOAT64 DEFAULT 0,  
    avg_fraudulent_amount FLOAT64 DEFAULT 0,  
    avg_processing_latency FLOAT64,           
    
    -- Métadonnées
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(window_start)
CLUSTER BY window_end;