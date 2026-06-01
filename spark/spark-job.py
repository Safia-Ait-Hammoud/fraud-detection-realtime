"""
spark-job.py — Job Spark Structured Streaming (Docker version)
Remplace les chemins Windows par des variables d'environnement Docker.
Utilise le vrai modèle XGBoost des collègues ML.
"""
from spark_streaming_app.kafka_alert_producer import publish_alert
from spark_streaming_app.bigquery_writer import write_batch
from spark_streaming_app.ml_inference import apply_ml_model
import sys
import os
import logging

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import (
    StructType, StringType, DoubleType,
    IntegerType
)

sys.path.insert(0, "/app")


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── Spark Session ─────────────────────────────────────────────────────────────
spark = SparkSession.builder \
    .appName("FraudDetection_Streaming_Pipeline") \
    .config("spark.sql.streaming.schemaInference", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
log.info("Spark session démarrée — version %s", spark.version)

# ── Schéma des transactions (format des collègues) ────────────────────────────
SCHEMA = StructType() \
    .add("transaction_id",      StringType(),  nullable=False) \
    .add("timestamp",           StringType(),  nullable=True) \
    .add("amount",              DoubleType(),  nullable=False) \
    .add("transaction_hour",    IntegerType(), nullable=True) \
    .add("merchant_category",   StringType(),  nullable=True) \
    .add("foreign_transaction", IntegerType(), nullable=True) \
    .add("location_mismatch",   IntegerType(), nullable=True) \
    .add("device_trust_score",  DoubleType(),  nullable=True) \
    .add("velocity_last_24h",   DoubleType(),  nullable=True) \
    .add("cardholder_age",      IntegerType(), nullable=True)

# ── Lecture Kafka ─────────────────────────────────────────────────────────────
KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "bank-transactions")

raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .option("maxOffsetsPerTrigger", 200) \
    .load()

log.info("Kafka stream connecté — topic: %s", KAFKA_TOPIC)

# ── Parse JSON ────────────────────────────────────────────────────────────────
transactions = raw_stream \
    .selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), SCHEMA).alias("data")) \
    .select("data.*") \
    .filter(col("transaction_id").isNotNull())

# ── Appliquer le modèle ML ────────────────────────────────────────────────────
scored = apply_ml_model(transactions) \
    .withColumn("processed_at", current_timestamp())

# ── foreachBatch : BigQuery + alertes Kafka ───────────────────────────────────


def process_batch(batch_df: DataFrame, batch_id: int):
    rows = [r.asDict() for r in batch_df.collect()]
    if not rows:
        return

    log.info("Batch %d — %d transactions", batch_id, len(rows))
    write_batch(rows)

    frauds = [r for r in rows if r.get("is_fraud") == 1]
    for txn in frauds:
        publish_alert(txn)
    if frauds:
        log.info("Batch %d — %d fraude(s) détectée(s) 🚨", batch_id, len(frauds))


# ── Démarrer le streaming ─────────────────────────────────────────────────────
query = scored.writeStream \
    .foreachBatch(process_batch) \
    .option("checkpointLocation", "/tmp/spark-checkpoints/main") \
    .trigger(processingTime="5 seconds") \
    .outputMode("append") \
    .start()

log.info("Streaming démarré — en attente de transactions...")
query.awaitTermination()
