# spark/streaming/ml_inference.py

from pyspark.sql.functions import col, lit

def apply_ml_model(df_parsed):
    """
    Squelette de la fonction d'inférence ML (Phase J8-J11).
    C'est ici que nous intégrerons le modèle XGBoost corrigé du Binôme 1
    via une Pandas UDF (User Defined Function) pour des prédictions ultra-rapides.
    """
    print("[En attente du modèle] - Application de l'inférence ML factice...")
    
    # Pour l'instant, on ajoute des colonnes factices pour que l'écriture BigQuery 
    # fonctionne sans erreur de schéma en attendant le vrai modèle.
    # On simule un score de confiance et on met is_fraud à 0 par défaut.
    
    df_with_predictions = df_parsed \
        .withColumn("confidence_score", lit(0.05)) \
        .withColumn("is_fraud", lit(0))
        
    return df_with_predictions