import random
from datetime import datetime

def generate_smart_transaction():
    """
    Génère une transaction basée sur les réelles corrélations de l'EDA.
    Simule des comportements légitimes, des attaques en force, 
    et des attaques "furtives" qui tentent de contourner les seuils du modèle ML.
    """
    # 1.5% de fraude, comme dans le dataset d'origine
    is_fraud_attempt = random.random() < 0.015
    # 10% des fraudes essaieront d'esquiver les seuils de l'EDA
    is_stealth_fraud = random.random() < 0.10 

    if not is_fraud_attempt:
        # ─── PROFIL LÉGITIME ──────────────────────────────────────────
        # Les montants sont majoritairement sous le Q75 (150$)
        amount = max(0.50, random.gauss(45, 20)) if random.random() < 0.8 else random.uniform(150, 500)
        # Heures de journée principalement (7h - 23h)
        hour = int(random.gauss(14, 4)) % 24
        if hour < 6: hour += 6 
        
        foreign = 1 if random.random() < 0.05 else 0
        mismatch = 1 if random.random() < 0.05 else 0
        
        # Le Device Trust Score est très important (Généralement élevé pour les légitimes)
        trust = round(random.uniform(0.7, 1.0), 4)
        
        # Vélocité sous la médiane (2.0) la plupart du temps
        velocity = float(random.randint(1, 2)) if random.random() < 0.8 else float(random.randint(3, 5))
        
        merchant = random.choices(["Food", "Grocery", "Clothing", "Travel", "Electronics"], weights=[40, 30, 15, 10, 5])[0]
        age = int(random.gauss(35, 12)) # Âge moyen autour de 35 ans

    else:
        # ─── PROFIL FRAUDEUR ──────────────────────────────────────────
        if is_stealth_fraud:
            # FRAUDE FURTIVE (Adversarial) : Tente de contourner les règles ML
            # Montant juste sous le seuil critique (ex: Q75 = 150$)
            amount = round(random.uniform(130, 149), 2)
            # Heure juste après la limite de "is_night" (6h)
            hour = random.randint(6, 8)
            # Pas de transactions étrangères pour ne pas alerter le risk_score
            foreign = 0
            mismatch = 0
            # Trust score moyen (appareil inconnu mais pas blacklisté)
            trust = round(random.uniform(0.4, 0.6), 4)
            # Vélocité limite (Médiane = 2.0)
            velocity = 2.0
            merchant = "Electronics"
            age = random.randint(60, 80) # Cible les personnes âgées
            
        else:
            # FRAUDE CLASSIQUE EN FORCE (Déclenche le top 5 des variables)
            # Très gros montants ou multiples micro-transactions
            amount = round(random.uniform(500, 2000), 2) if random.random() > 0.2 else round(random.uniform(0.1, 5.0), 2)
            # is_night = 1 (Pleine nuit)
            hour = random.randint(0, 5)
            # Fait exploser le risk_score
            foreign = 1 
            mismatch = 1 
            # Device trust score catastrophique
            trust = round(random.uniform(0.0, 0.2), 4)
            # high_velocity = 1
            velocity = float(random.randint(8, 25))
            merchant = random.choices(["Travel", "Electronics"], weights=[60, 40])[0]
            age = random.randint(18, 65)

    # Sécurité pour éviter un âge irréaliste
    age = max(18, min(age, 90))

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
        "cardholder_age": age
    }