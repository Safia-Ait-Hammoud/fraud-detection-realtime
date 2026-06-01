import os
from pyspark.sql.functions import col, current_timestamp
from pyspark.sql.types import LongType, DoubleType


def write_batch_to_bigquery(df_batch, batch_id):
    """
    Écrit un micro-batch vers BigQuery.
    """
    df_batch.cache()

    try:
        count = df_batch.count()  # ← Le UDF ML s'exécute ici, résultat mis en cache

        if count == 0:
            print(f"[Batch {batch_id}] Batch vide, ignoré.")
            return

        project_id = os.environ.get("PROJECT_ID", "").strip().strip('"')
        credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip().strip('"')
        table_name = f"{project_id}.fraud_detection.transactions"

        print(f"[Batch {batch_id}] Écriture de {count} transactions → BigQuery...")

        df_to_write = (
            df_batch.withColumn("transaction_hour", col("transaction_hour").cast(LongType()))
            .withColumn("foreign_transaction", col("foreign_transaction").cast(LongType()))
            .withColumn("location_mismatch", col("location_mismatch").cast(LongType()))
            .withColumn("cardholder_age", col("cardholder_age").cast(LongType()))
            .withColumn("is_fraud", col("is_fraud").cast(LongType()))
            .withColumn("velocity_last_24h", col("velocity_last_24h").cast(DoubleType()))
            .withColumn("confidence_score", col("confidence_score").cast(DoubleType()))
            .withColumn("processing_timestamp", current_timestamp())
            .select(
                "transaction_id",
                "timestamp",
                "amount",
                "transaction_hour",
                "merchant_category",
                "foreign_transaction",
                "location_mismatch",
                "device_trust_score",
                "velocity_last_24h",
                "cardholder_age",
                "is_fraud",
                "confidence_score",
                "processing_timestamp",
            )
        )

        (
            df_to_write.write.format("bigquery")
            .option("table", table_name)
            .option("project", project_id)
            .option("parentProject", project_id)
            .option("credentialsFile", credentials_path)
            .option("writeMethod", "direct")
            .mode("append")
            .save()
        )

        print(f"[Batch {batch_id}] ✅ {count} transactions insérées dans BigQuery.")

    except Exception as e:
        print(f"[Batch {batch_id}] ❌ Erreur : {e}")
        raise  # ← Re-raise pour que Spark gère le retry

    finally:
        df_batch.unpersist()  # ← Libère la mémoire dans tous les cas


def start_bigquery_stream(df_parsed):
    """
    Démarre l'écriture continue via foreachBatch.
    """
    return df_parsed.writeStream.foreachBatch(write_batch_to_bigquery).outputMode("append").start()
