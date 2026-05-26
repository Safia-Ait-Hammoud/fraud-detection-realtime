-- 01_create_schema.sql
-- Création du dataset (schéma) dans BigQuery pour isoler notre projet
CREATE SCHEMA IF NOT EXISTS fraud_detection
  OPTIONS (
    description = 'Dataset for Real-Time Bank Fraud Detection Pipeline',
    location = 'EU'
  );