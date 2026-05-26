"""
kafka_producer.py
Simulates real-time bank transactions and sends them to Kafka topic.
"""

import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

# ── Kafka Configuration ───────────────────────────────────────
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME   = 'bank-transactions'

# ── Producer Setup ────────────────────────────────────────────
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_transaction():
    """Generate a fake bank transaction matching your dataset features."""
    amount = round(random.expovariate(1/200), 2)   # realistic skewed amounts

    transaction = {
        # Core fields
        "transaction_id"      : f"TXN-{random.randint(100000, 999999)}",
        "timestamp"           : datetime.now().isoformat(),

        # ── Features your model was trained on ──────────────
        "amount"              : amount,
        "transaction_hour"    : random.randint(0, 23),
        "foreign_transaction" : random.choices([0, 1], weights=[0.85, 0.15])[0],
        "location_mismatch"   : random.choices([0, 1], weights=[0.90, 0.10])[0],
        "device_trust_score"  : round(random.uniform(0, 1), 4),
        "velocity_last_24h"   : random.randint(1, 30),
        "cardholder_age"      : random.randint(18, 80),
    }

    return transaction

def send_transactions(interval_seconds=1.0):
    """Continuously send transactions to Kafka."""
    print(f"🚀 Starting producer → topic: '{TOPIC_NAME}'")
    print(f"   Broker : {KAFKA_BROKER}")
    print(f"   Sending one transaction every {interval_seconds}s\n")

    count = 0
    try:
        while True:
            txn = generate_transaction()
            producer.send(TOPIC_NAME, value=txn)
            count += 1
            print(f"[{count}] Sent → ID: {txn['transaction_id']} | "
                  f"Amount: ${txn['amount']:.2f} | "
                  f"Hour: {txn['transaction_hour']}h | "
                  f"Foreign: {txn['foreign_transaction']}")
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print(f"\n⛔ Stopped. Total sent: {count} transactions.")
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    send_transactions(interval_seconds=1.0)
