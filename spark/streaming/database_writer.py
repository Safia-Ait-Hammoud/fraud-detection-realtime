# spark/streaming/database_writer.py

import os

def write_batch_to_bigquery(df_batch, batch_id):
    """
    Fonction exécutée pour chaque micro-batch du flux.
    Prend les transactions récentes et les ajoute à la table BigQuery.
    """
    # Si le paquet de données est vide, on ne fait rien
    if df_batch.count() == 0:
        return

    print(f"Traitement du micro-batch {batch_id} avec {df_batch.count()} transactions...")

    # Récupération de l'ID du projet depuis les variables d'environnement
    project_id = os.environ.get("GCP_PROJECT_ID", "TON_ID_DE_PROJET")
    table_name = f"{project_id}.fraud_detection.transactions"

    try:
        # Écriture dans BigQuery
        df_batch.write \
            .format("bigquery") \
            .option("table", table_name) \
            .mode("append") \
            .save()
        print(f"Micro-batch {batch_id} inséré avec succès dans BigQuery !")
    except Exception as e:
        print(f"Erreur lors de l'insertion du batch {batch_id} : {e}")

def start_bigquery_stream(df_parsed):
    """
    Démarre le flux d'écriture continue vers BigQuery.
    """
    return df_parsed \
        .writeStream \
        .foreachBatch(write_batch_to_bigquery) \
        .outputMode("append") \
        .start()