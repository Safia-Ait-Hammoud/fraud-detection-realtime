import os

def write_batch_to_bigquery(df_batch, batch_id):
    if df_batch.count() == 0:
        return

    # 1. On nettoie proprement les variables
    project_id = os.environ.get("PROJECT_ID", "").replace('"', '').strip()
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").replace('"', '').strip()
    
    table_name = f"{project_id}.fraud_detection.transactions"

    print(f"Traitement du micro-batch {batch_id} ({df_batch.count()} transactions)")

    try:
        # 2. On envoie TOUT explicitement au connecteur BigQuery (Projet + Clé)
        df_batch.write \
            .format("bigquery") \
            .option("table", table_name) \
            .option("project", project_id) \
            .option("parentProject", project_id) \
            .option("credentialsFile", credentials_path) \
            .option("writeMethod", "direct") \
            .mode("append") \
            .save()
            
        print(f"Micro-batch {batch_id} inséré avec succès dans BigQuery !")
        
    except Exception as e:
        print(f"Erreur lors de l'insertion du batch {batch_id} : {e}")

def start_bigquery_stream(df_parsed):
    return df_parsed \
        .writeStream \
        .foreachBatch(write_batch_to_bigquery) \
        .outputMode("append") \
        .start()