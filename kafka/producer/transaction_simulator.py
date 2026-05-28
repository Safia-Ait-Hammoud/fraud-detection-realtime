# kafka/producer/transaction_simulator.py

import random
from datetime import datetime

def generate_smart_transaction():
    """
    Génère une transaction avec injection de 'bruit' statistique 
    pour challenger le modèle Machine Learning.
    """
    is_fraud_attempt = random.random() < 0.015
    is_noisy = random.random() < 0.05  # 5% de chance d'avoir une donnée "bruitée" (Edge Case)

    if not is_fraud_attempt:
        # PROFIL LÉGITIME
        if is_noisy:
            amount = round(random.uniform(800, 2500), 2)
            hour = random.randint(1, 4)                  # Achète la nuit
            foreign = 1                                  # À l'étranger
            mismatch = 1                                 # Adresse différente
            trust = round(random.uniform(0.4, 0.6), 4)   # Score moyen
        else:
            # Comportement normal standard
            amount = max(0.01, random.gauss(50, 30))     # Gaussienne pour un montant naturel
            hour = int(random.gauss(14, 4)) % 24
            foreign = 1 if random.random() < 0.02 else 0
            mismatch = 1 if random.random() < 0.02 else 0
            trust = round(random.uniform(0.8, 1.0), 4)
            
        merchant = random.choices(["Food", "Grocery", "Clothing", "Travel", "Electronics"], weights=[40, 30, 15, 10, 5])[0]
        velocity = random.randint(1, 5)

    else:
        # PROFIL FRAUDEUR
        if is_noisy:
            amount = round(random.uniform(10, 50), 2)    # Petit montant pour passer sous le radar
            hour = random.randint(10, 16)                # En pleine journée
            foreign = 0                                  # Utilise un proxy local
            mismatch = 0                                 # Adresse qui matche
            trust = round(random.uniform(0.6, 0.9), 4)   # Appareil usurpé
            velocity = random.randint(1, 3)              # Vélocité faible
        else:
            # Attaque classique en force
            amount = round(random.uniform(500, 1500), 2) if random.random() > 0.3 else round(random.uniform(0.1, 2.0), 2)
            hour = random.randint(0, 5)
            foreign = 1 if random.random() < 0.80 else 0
            mismatch = 1 if random.random() < 0.80 else 0
            trust = round(random.uniform(0.0, 0.3), 4)
            velocity = random.randint(10, 30)
            
        merchant = random.choices(["Travel", "Electronics", "Clothing"], weights=[40, 40, 20])[0]

    return {
        "transaction_id": f"TXN-{random.randint(100000, 999999)}",
        "timestamp": datetime.now().isoformat(),
        "amount": round(amount, 2),
        "transaction_hour": hour,
        "merchant_category": merchant,
        "foreign_transaction": foreign,
        "location_mismatch": mismatch,
        "device_trust_score": trust,
        "velocity_last_24h": velocity,
        "cardholder_age": random.randint(18, 80)
    }