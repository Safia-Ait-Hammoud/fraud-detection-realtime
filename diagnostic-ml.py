# diagnostic_ml.py — à placer à la racine du projet, exécuter avec le venv actif
import sys, os
from pathlib import Path

print("=" * 60)
print("DIAGNOSTIC ML - HORS SPARK")
print("=" * 60)
print(f"Python  : {sys.version}")
print(f"Exe     : {sys.executable}")

# ── 1. Vérification des librairies ─────────────────────────────
print("\n── Librairies ──────────────────────────────────────────")
libs = {}
for name in ["pandas", "numpy", "pyarrow", "xgboost", "sklearn", "joblib"]:
    try:
        mod = __import__(name if name != "sklearn" else "sklearn")
        version = getattr(mod, "__version__", "?")
        libs[name] = version
        print(f"  ✅ {name:<12} {version}")
    except ImportError as e:
        print(f"  ❌ {name:<12} MANQUANT → {e}")

# ── 2. Vérification des chemins du modèle ──────────────────────
print("\n── Fichiers modèle ─────────────────────────────────────")
# Tester LES DEUX chemins possibles
paths_to_test = [
    Path(__file__).resolve().parent / "ml-models" / "trained",
    Path("C:/fraud/ml-models/trained"),
    Path("C:/Users/Lenovo T470/OneDrive/Documents/GitHub/fraud-detection-realtime/ml-models/trained"),
]

MODEL_DIR = None
for p in paths_to_test:
    print(f"  Test : {p}")
    if p.exists():
        print(f"    ✅ Dossier trouvé !")
        MODEL_DIR = p
        break
    else:
        print(f"    ❌ Introuvable")

if MODEL_DIR is None:
    print("\n❌ CRITIQUE : Aucun dossier de modèle trouvé.")
    print("   Crée le dossier et place les fichiers .pkl")
    sys.exit(1)

ARTIFACTS = ["xgb_fraud_model.pkl", "standard_scaler.pkl",
             "merchant_encoder.pkl", "amount_bin_encoder.pkl"]
for f in ARTIFACTS:
    p = MODEL_DIR / f
    size = p.stat().st_size if p.exists() else 0
    print(f"  {'✅' if p.exists() else '❌'} {f} ({size} bytes)")

# ── 3. Chargement des artefacts ────────────────────────────────
print("\n── Chargement joblib ───────────────────────────────────")
import joblib
try:
    model       = joblib.load(MODEL_DIR / "xgb_fraud_model.pkl")
    scaler      = joblib.load(MODEL_DIR / "standard_scaler.pkl")
    merch_enc   = joblib.load(MODEL_DIR / "merchant_encoder.pkl")
    amount_enc  = joblib.load(MODEL_DIR / "amount_bin_encoder.pkl")
    print("  ✅ Tous les artefacts chargés")
    print(f"  ✅ Type modèle : {type(model).__name__}")
except Exception as e:
    print(f"  ❌ ERREUR CHARGEMENT : {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# ── 4. Test prédiction complète ────────────────────────────────
print("\n── Test prédiction ─────────────────────────────────────")
import pandas as pd
import numpy as np

try:
    df = pd.DataFrame({
        'amount': [100.0, 1500.0],
        'transaction_hour': [14, 2],
        'merchant_category': ['Food', 'Electronics'],
        'foreign_transaction': [0, 1],
        'location_mismatch': [0, 1],
        'device_trust_score': [0.9, 0.1],
        'velocity_last_24h': [1.0, 15.0],
        'cardholder_age': [35, 25]
    })

    AMOUNT_Q75 = 242.48
    VELOCITY_MEDIAN = 2.0
    AMOUNT_BINS = [-np.inf, 39.35, 90.48, 160.39, 285.8, np.inf]
    BIN_LABELS  = ['Très Faible', 'Faible', 'Moyen', 'Élevé', 'Très Élevé']
    FEATURE_COLS = [
        'amount', 'amount_log', 'transaction_hour', 'is_night',
        'foreign_transaction', 'location_mismatch', 'device_trust_score',
        'velocity_last_24h', 'cardholder_age', 'high_amount', 'high_velocity',
        'risk_score', 'merchant_category_enc', 'amount_bin_enc'
    ]

    df['amount_log']   = np.log1p(df['amount'])
    df['is_night']     = (df['transaction_hour'] < 6).astype(int)
    df['high_amount']  = (df['amount'] > AMOUNT_Q75).astype(int)
    df['high_velocity']= (df['velocity_last_24h'] > VELOCITY_MEDIAN).astype(int)
    df['risk_score']   = df['foreign_transaction'] + df['location_mismatch'] + df['high_velocity']
    df['amount_bin']   = pd.cut(df['amount'], bins=AMOUNT_BINS, labels=BIN_LABELS)
    df['amount_bin_enc'] = amount_enc.transform(df['amount_bin'].astype(str))
    known = set(merch_enc.classes_)
    df['merchant_category_enc'] = df['merchant_category'].apply(
        lambda x: merch_enc.transform([x])[0] if x in known else 0
    )
    X = scaler.transform(df[FEATURE_COLS])
    preds = model.predict(X)
    probs = model.predict_proba(X)[:, 1]
    print(f"  ✅ Prédictions : {preds}")
    print(f"  ✅ Probabilités: {probs}")
    print("\n✅ TOUT FONCTIONNE — Le problème est dans l'intégration Spark")

except Exception as e:
    print(f"  ❌ ERREUR : {e}")
    import traceback; traceback.print_exc()
    print("\n❌ Le problème est dans le code ML lui-même")