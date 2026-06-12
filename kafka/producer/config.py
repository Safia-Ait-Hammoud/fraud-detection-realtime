# kafka/producer/config.py
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:29092")
TOPIC_NAME = 'bank-transactions'
INTERVAL_SEC = 0.5  # Fréquence d'envoi des messages (0.5s pour un flux plus rapide)