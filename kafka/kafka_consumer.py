"""
kafka_consumer.py
Reads transactions from Kafka, engineers features, scores with your
Random Forest model, and prints fraud alerts in real time.
"""

import json
import numpy as np
import pandas as pd
import joblib
from kafka import KafkaConsumer

# ── Configuration ─────────────────────────────────────────────
KAFKA_BROKER  = 'localhost:9092'
TOPIC_NAME    = 'bank-transactions'
MODEL_PATH    = 'models/rf_fraud_model.pkl'   # path to your pkl
FRAUD_THRESHOLD = 0.5                          # probability above = FRAUD

# ── Load your trained Random Forest model ─────────────────────
print(f"📦 Loading model from: {MODEL_PATH}")
model = joblib.load(MODEL_PATH)
print("✅ Model loaded successfully\n")

# ── Feature engineering (matches 02_data_preparation.ipynb) ───
def engineer_features(txn: dict) -> pd.DataFrame:
    amount = txn['amount']

    AMOUNT_MEAN  = 200.0
    AMOUNT_STD   = 180.0
    AMOUNT_Q75   = 300.0
    VELOCITY_MED = 8.0

    def safe_bin(value, bins, labels, default=0):
        """Cut a single value into a bin, returning default if out of range."""
        result = pd.cut([value], bins=bins, labels=labels, include_lowest=True)
        val = result[0]
        return default if pd.isna(val) else int(val)

    merchant_category_enc = safe_bin(
        amount,
        bins=[0, 50, 200, 500, np.inf],
        labels=[0, 1, 2, 3]
    )

    amount_bin_enc = safe_bin(
        amount,
        bins=[0, 100, 300, 1000, np.inf],
        labels=[0, 1, 2, 3]
    )

    features = {
        "amount"               : amount,
        "amount_log"           : np.log1p(amount),
        "transaction_hour"     : txn['transaction_hour'],
        "is_night"             : int(txn['transaction_hour'] < 6),
        "foreign_transaction"  : txn['foreign_transaction'],
        "location_mismatch"    : txn['location_mismatch'],
        "device_trust_score"   : txn['device_trust_score'],
        "velocity_last_24h"    : txn['velocity_last_24h'],
        "cardholder_age"       : txn['cardholder_age'],
        "high_amount"          : int(amount > AMOUNT_Q75),
        "high_velocity"        : int(txn['velocity_last_24h'] > VELOCITY_MED),
        "risk_score"           : (txn['foreign_transaction']
                                  + txn['location_mismatch']
                                  + int(txn['velocity_last_24h'] > VELOCITY_MED)),
        "merchant_category_enc": merchant_category_enc,
        "amount_bin_enc"       : amount_bin_enc,
    }

    return pd.DataFrame([features])

# ── Consumer Setup ────────────────────────────────────────────
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='latest',          # read new messages only
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print(f"👂 Listening on topic: '{TOPIC_NAME}' | Broker: {KAFKA_BROKER}\n")
print(f"{'ID':<20} {'Amount':>10} {'Score':>8} {'Result'}")
print("-" * 55)

# ── Main loop ─────────────────────────────────────────────────
try:
    for message in consumer:
        txn = message.value

        # Feature engineering
        X = engineer_features(txn)

        # Predict fraud probability
        fraud_prob = model.predict_proba(X)[0][1]
        is_fraud   = fraud_prob >= FRAUD_THRESHOLD

        # Output
        result = "🚨 FRAUD" if is_fraud else "✅ OK"
        print(f"{txn['transaction_id']:<20} "
              f"${txn['amount']:>9.2f} "
              f"{fraud_prob:>8.4f} "
              f"{result}")

        # Optional: save flagged transactions to a file
        if is_fraud:
            with open("fraud_alerts.jsonl", "a") as f:
                txn['fraud_score'] = round(fraud_prob, 4)
                f.write(json.dumps(txn) + "\n")

except KeyboardInterrupt:
    print("\n⛔ Consumer stopped.")
finally:
    consumer.close()
