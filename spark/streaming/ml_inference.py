import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from pyspark.sql.functions import pandas_udf, col
from pyspark.sql.types import StructType, StructField, IntegerType, FloatType, DoubleType

# ─── 1. CHEMINS VERS LES FICHIERS SAUVEGARDÉS ───
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = Path("C:/fraud/ml-models/trained")

# ─── 2. SEUILS FIXES (Tirés de l'exploration des données) ───
VELOCITY_MEDIAN = 2.0 
AMOUNT_Q75 = 242.48
AMOUNT_BINS = [-np.inf, 39.35, 90.48, 160.39, 285.8, np.inf]
BIN_LABELS = ['Très Faible', 'Faible', 'Moyen', 'Élevé', 'Très Élevé']

# Ordre exact des colonnes attendues par le modèle
FEATURE_COLS = [
    'amount', 'amount_log', 'transaction_hour', 'is_night',
    'foreign_transaction', 'location_mismatch', 'device_trust_score',
    'velocity_last_24h', 'cardholder_age', 'high_amount', 'high_velocity',
    'risk_score', 'merchant_category_enc', 'amount_bin_enc'
]

# Variables globales pour éviter de recharger les modèles à chaque transaction
_model = None
_scaler = None
_merchant_enc = None
_amount_enc = None

def load_ml_artifacts():
    """Charge le modèle et les encodeurs en mémoire sur les exécuteurs Spark."""
    global _model, _scaler, _merchant_enc, _amount_enc
    if _model is None:
        print("Chargement des artefacts ML (Modèle, Scaler, Encodeurs)...")
        _model = joblib.load(MODEL_DIR / "xgb_fraud_model.pkl") 
        _scaler = joblib.load(MODEL_DIR / "standard_scaler.pkl")
        _merchant_enc = joblib.load(MODEL_DIR / "merchant_encoder.pkl")
        _amount_enc = joblib.load(MODEL_DIR / "amount_bin_encoder.pkl")
    return _model, _scaler, _merchant_enc, _amount_enc

ml_output_schema = StructType([
    StructField("is_fraud", IntegerType(), True),
    StructField("confidence_score", DoubleType(), True)
])

# ─── 3. PANDAS UDF ───
@pandas_udf(ml_output_schema)
def predict_fraud_udf(amount: pd.Series, hour: pd.Series, merchant: pd.Series, 
                      foreign: pd.Series, mismatch: pd.Series, trust: pd.Series, 
                      velocity: pd.Series, age: pd.Series) -> pd.DataFrame:
    
    model, scaler, merchant_enc, amount_enc = load_ml_artifacts()
    
    # Étape A : Reconstruire les données brutes
    df = pd.DataFrame({
        'amount': amount,
        'transaction_hour': hour,
        'merchant_category': merchant,
        'foreign_transaction': foreign,
        'location_mismatch': mismatch,
        'device_trust_score': trust,
        'velocity_last_24h': velocity,
        'cardholder_age': age
    })
    
    # Étape B : Ingénierie des caractéristiques
    df['amount_log'] = np.log1p(df['amount'])
    df['is_night'] = (df['transaction_hour'] < 6).astype(int)
    df['high_amount'] = (df['amount'] > AMOUNT_Q75).astype(int)
    df['high_velocity'] = (df['velocity_last_24h'] > VELOCITY_MEDIAN).astype(int)
    df['risk_score'] = df['foreign_transaction'] + df['location_mismatch'] + df['high_velocity']
    
    # Étape C : Application des encodeurs
    df['amount_bin'] = pd.cut(df['amount'], bins=AMOUNT_BINS, labels=BIN_LABELS)
    df['amount_bin_enc'] = amount_enc.transform(df['amount_bin'].astype(str))
    
    # (Sécurité pour éviter que le pipeline plante si un nouveau marchand apparaît)
    known_merchants = set(merchant_enc.classes_)
    df['merchant_category_enc'] = df['merchant_category'].apply(
        lambda x: merchant_enc.transform([x])[0] if x in known_merchants else 0
    )
    
    # Étape D : Trier les colonnes et standardiser
    X_final = df[FEATURE_COLS]
    X_scaled = scaler.transform(X_final)
    
    # Étape E : Prédiction
    predictions = model.predict(X_scaled)
    
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X_scaled)[:, 1]
    else:
        probabilities = [float(p) for p in predictions] 
        
    return pd.DataFrame({
        "is_fraud": pd.Series(predictions).astype("int32"),
        "confidence_score": pd.Series(probabilities).astype("float64")
    })

# ─── 4. L'APPEL DE LA FONCTION POUR LE STREAMING ───
def apply_ml_model(df_transactions):
    """
    Applique le modèle au flux PySpark en temps réel.
    """
    print("Application de l'inférence ML temps réel...")
    
    df_enrichi = df_transactions.withColumn(
        "ml_results", 
        predict_fraud_udf(
            col("amount"),
            col("transaction_hour"),
            col("merchant_category"),
            col("foreign_transaction"),
            col("location_mismatch"),
            col("device_trust_score"),
            col("velocity_last_24h"),
            col("cardholder_age")
        )
    )
    
    # On éclate le résultat pour avoir des colonnes propres pour BigQuery
    df_final = df_enrichi \
        .withColumn("is_fraud", col("ml_results.is_fraud")) \
        .withColumn("confidence_score", col("ml_results.confidence_score")) \
        .drop("ml_results")
        
    return df_final