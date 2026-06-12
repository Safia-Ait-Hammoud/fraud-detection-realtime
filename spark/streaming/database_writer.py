import os
import time
from pyspark.sql.functions import col, current_timestamp
from pyspark.sql.types import LongType, DoubleType

from prometheus_client import CollectorRegistry, Counter, Gauge, push_to_gateway

registry = CollectorRegistry()
tx_counter = Counter('transactions_processed_total', 'Transactions traitées par Spark', registry=registry)
fraud_counter = Counter('frauds_detected_total', 'Fraudes détectées par le modèle', registry=registry)
latency_gauge = Gauge('processing_latency_seconds', 'Latence de traitement du micro-batch', registry=registry)

def write_batch_to_bigquery(df_batch, batch_id):
    """
    Écrit un micro-batch vers BigQuery et pousse les métriques vers Prometheus.
    """
    df_batch.cache()
    start_time = time.time()

    try:
        count = df_batch.count()

        if count == 0:
            print(f"[Batch {batch_id}] Batch vide, ignoré.")
            return

        try:
            fraud_count = df_batch.filter(col("is_fraud") == 1).count()
            
            tx_counter.inc(count)
            fraud_counter.inc(fraud_count)
            
            processing_time = time.time() - start_time
            latency_gauge.set(processing_time)
            
            push_to_gateway('localhost:9091', job='spark_streaming', registry=registry)
            
            print(f"[Metrics] Total cumulé envoyé : {tx_counter._value._value} Tx, {fraud_counter._value._value} Fraudes")
        except Exception as metric_err:
            print(f"[Metrics Warning] Impossible d'atteindre le Pushgateway : {metric_err}")


        project_id = os.environ.get("PROJECT_ID", "fraud-detection-project-497521").strip().strip('"')
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

        print(f"[Batch {batch_id}] {count} transactions insérées dans BigQuery.")

    except Exception as e:
        print(f"[Batch {batch_id}] Erreur : {e}")
        raise

    finally:
        df_batch.unpersist()


def start_bigquery_stream(df_parsed):
    """
    Démarre l'écriture continue via foreachBatch.
    """
    return df_parsed.writeStream.foreachBatch(write_batch_to_bigquery).outputMode("append").start()