-- 01_create_schema.sql
-- Création du dataset (schéma) dans BigQuery
CREATE SCHEMA IF NOT EXISTS fraud_detection
  OPTIONS (
    description = 'Dataset for Real-Time Bank Fraud Detection Pipeline',
    location = 'EU'
  );