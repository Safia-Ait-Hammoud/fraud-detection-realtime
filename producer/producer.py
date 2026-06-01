"""
producer.py — Kafka Transaction Producer (Docker version)
Adapté depuis kafka/producer/kafka_producer.py + transaction_simulator.py
"""
import json
import time
import random
import os
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

# ── Config depuis variables d'environnement ───────────────────────────────────
KAFKA_BROKER  = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC_NAME    = os.getenv("KAFKA_TOPIC", "bank-transactions")
INTERVAL_SEC  = float(os.getenv("PUBLISH_RATE_MS", "500")) / 1000.0

# ── Seuils ML (identiques à ml_inference.py) ─────────────────────────────────
AMOUNT_Q75 = 242.48

def generate_smart_transaction() -> dict:
    """
    Génère une transaction simulée avec 1.5% de fraude.
    Reproduit exactement la logique du transaction_simulator.py original.
    """
    is_fraud_attempt = random.random() < 0.015
    is_stealth_fraud  = random.random() < 0.10

    if not is_fraud_attempt:
        amount   = max(0.50, random.gauss(45, 20)) if random.random() < 0.8 else random.uniform(150, 500)
        hour     = int(random.gauss(14, 4)) % 24
        if hour < 6: hour += 6
        foreign  = 1 if random.random() < 0.05 else 0
        mismatch = 1 if random.random() < 0.05 else 0
        trust    = round(random.uniform(0.7, 1.0), 4)
        velocity = float(random.randint(1, 2)) if random.random() < 0.8 else float(random.randint(3, 5))
        merchant = random.choices(
            ["Food", "Grocery", "Clothing", "Travel", "Electronics"],
            weights=[40, 30, 15, 10, 5]
        )[0]
        age = int(random.gauss(35, 12))

    elif is_stealth_fraud:
        amount   = round(random.uniform(130, 149), 2)
        hour     = random.randint(6, 8)
        foreign  = 0
        mismatch = 0
        trust    = round(random.uniform(0.4, 0.6), 4)
        velocity = 2.0
        merchant = "Electronics"
        age      = random.randint(60, 80)

    else:
        amount   = round(random.uniform(500, 2000), 2) if random.random() > 0.2 else round(random.uniform(0.1, 5.0), 2)
        hour     = random.randint(0, 5)
        foreign  = 1
        mismatch = 1
        trust    = round(random.uniform(0.0, 0.2), 4)
        velocity = float(random.randint(8, 25))
        merchant = random.choices(["Travel", "Electronics"], weights=[60, 40])[0]
        age      = random.randint(18, 65)

    age = max(18, min(age, 90))

    return {
        "transaction_id":     f"TXN-{random.randint(100000, 999999)}",
        "timestamp":          datetime.now().isoformat(),
        "amount":             round(amount, 2),
        "transaction_hour":   hour,
        "merchant_category":  merchant,
        "foreign_transaction": foreign,
        "location_mismatch":  mismatch,
        "device_trust_score": trust,
        "velocity_last_24h":  velocity,
        "cardholder_age":     age,
    }


def create_producer(retries: int = 10, delay: int = 5) -> KafkaProducer:
    for attempt in range(1, retries + 1):
        try:
            p = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
            )
            print(f"[producer] Connecté à Kafka {KAFKA_BROKER}")
            return p
        except KafkaError as e:
            print(f"[producer] Tentative {attempt}/{retries} — Kafka pas prêt : {e}")
            time.sleep(delay)
    raise RuntimeError("Impossible de se connecter à Kafka")


def main():
    producer = create_producer()
    sent = 0

    print(f"[producer] Envoi vers topic '{TOPIC_NAME}' toutes les {INTERVAL_SEC}s")

    while True:
        try:
            tx = generate_smart_transaction()
            producer.send(TOPIC_NAME, key=tx["transaction_id"], value=tx).get(timeout=10)
            sent += 1

            alert = "🚨 FRAUDE" if (tx["transaction_hour"] <= 5 and tx["foreign_transaction"] == 1) else "✅ NORMAL"
            if sent % 50 == 0 or alert == "🚨 FRAUDE":
                print(f"[{sent}] {alert} | {tx['transaction_id']} | ${tx['amount']:>7.2f} | {tx['merchant_category']}")

            time.sleep(INTERVAL_SEC)

        except KeyboardInterrupt:
            print(f"\n[producer] Arrêt. Total envoyé : {sent}")
            break
        except KafkaError as e:
            print(f"[producer] Erreur Kafka : {e}")
            time.sleep(5)

    producer.flush()
    producer.close()


if __name__ == "__main__":
    main()