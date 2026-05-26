-- database/sql/02_create_tables.sql

-- 1. Création de la table principale qui stockera le flux temps réel
CREATE TABLE IF NOT EXISTS fraud_detection.transactions (
    transaction_id STRING NOT NULL,
    transaction_time FLOAT64,
    
    -- Features du dataset (V1 à V28)
    V1 FLOAT64, V2 FLOAT64, V3 FLOAT64, V4 FLOAT64, V5 FLOAT64,
    V6 FLOAT64, V7 FLOAT64, V8 FLOAT64, V9 FLOAT64, V10 FLOAT64,
    V11 FLOAT64, V12 FLOAT64, V13 FLOAT64, V14 FLOAT64, V15 FLOAT64,
    V16 FLOAT64, V17 FLOAT64, V18 FLOAT64, V19 FLOAT64, V20 FLOAT64,
    V21 FLOAT64, V22 FLOAT64, V23 FLOAT64, V24 FLOAT64, V25 FLOAT64,
    V26 FLOAT64, V27 FLOAT64, V28 FLOAT64,
    
    amount FLOAT64,
    
    -- Résultats de l'inférence ML
    is_fraud BOOLEAN,
    confidence_score FLOAT64,
    
    -- Métadonnées du pipeline
    processing_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(processing_timestamp)
CLUSTER BY is_fraud, transaction_id;


-- 2. Création de la table d'agrégation pour les statistiques en temps réel
CREATE TABLE IF NOT EXISTS fraud_detection.fraud_stats (
    window_start TIMESTAMP NOT NULL,          -- Début de la fenêtre de temps (ex: minute précise)
    window_end TIMESTAMP NOT NULL,            -- Fin de la fenêtre de temps
    
    -- Métriques pour le dashboard Grafana
    total_transactions INT64 DEFAULT 0,       -- Volume total de transactions
    total_frauds INT64 DEFAULT 0,             -- Nombre de fraudes détectées
    fraud_rate_percentage FLOAT64 DEFAULT 0,  -- Taux de fraude (%)
    avg_fraudulent_amount FLOAT64 DEFAULT 0,  -- Montant moyen des fraudes
    avg_processing_latency FLOAT64,           -- Latence moyenne de traitement en millisecondes
    
    -- Métadonnées
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(window_start)
CLUSTER BY window_end;