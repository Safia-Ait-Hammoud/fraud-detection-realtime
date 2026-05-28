# kafka/producer/kafka_producer.py

import json
import time
from kafka import KafkaProducer

# Import de la configuration du simulateur intelligent
from config import KAFKA_BROKER, TOPIC_NAME, INTERVAL_SEC
from transaction_simulator import generate_smart_transaction

# Initialisation du producteur Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    api_version=(3, 7, 0)
)

def start_smart_stream():
    """Envoie un flux infini de transactions simulées intelligemment."""
    print(f"Démarrage du Smart Simulator | Topic : '{TOPIC_NAME}'")
    print(f"Fréquence : 1 message toutes les {INTERVAL_SEC} secondes")
    print("-" * 60)

    count = 0
    try:
        while True:
            # On génère la transaction avec notre logique métier
            transaction = generate_smart_transaction()
            
            # On l'envoie dans le tuyau Kafka
            producer.send(TOPIC_NAME, value=transaction)
            count += 1
            
            alert = "[RISQUE ÉLEVÉ]" if transaction['transaction_hour'] <= 5 and transaction['foreign_transaction'] == 1 else "[NORMAL]"
            print(f"[{count}] {alert} ID: {transaction['transaction_id']} | "
                  f"Montant: ${transaction['amount']:>7.2f} | "
                  f"Catégorie: {transaction['merchant_category']:<12}")
            
            time.sleep(INTERVAL_SEC)

    except KeyboardInterrupt:
        print(f"\nSimulation arrêtée manuellement. Total envoyé : {count}.")
    finally:
        producer.flush()
        producer.close()
        print("Producteur déconnecté proprement.")

if __name__ == "__main__":
    start_smart_stream()