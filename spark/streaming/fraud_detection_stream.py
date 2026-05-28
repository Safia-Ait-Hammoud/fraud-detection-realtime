# spark/streaming/fraud_detection_stream.py

import os
from pathlib import Path
from dotenv import load_dotenv
from pyspark.sql import SparkSession

# Importation de tes modules locaux
from kafka_consumer import read_from_kafka, parse_kafka_payload
from database_writer import start_bigquery_stream

# 1. Chargement de la configuration et des variables d'environnement
BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = BASE_DIR / 'config' / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)

def create_spark_session():
    """
    Initialise Spark avec les connecteurs requis pour Kafka et Google Cloud BigQuery.
    """
    # Les packages Maven pour Kafka et BigQuery
    spark_packages = (
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
        "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.34.0"
    )

    return SparkSession.builder \
        .appName("FraudDetection_Streaming_Pipeline") \
        .master("local[*]") \
        .config("spark.jars.packages", spark_packages) \
        .getOrCreate()

def main():
    # Initialisation
    spark = create_spark_session()
    
    # Réduction du niveau de logs pour garder un terminal lisible
    spark.sparkContext.setLogLevel("WARN")
    
    print("Démarrage du pipeline PySpark Streaming...")

    # 2. Ingestion : Lecture brute depuis le topic Kafka
    df_raw = read_from_kafka(spark)

    # 3. Transformation : Parsing du JSON selon le schéma strict
    df_transactions = parse_kafka_payload(df_raw)

    print("Connecté au flux Kafka ! En attente des transactions...")
    print("Démarrage de l'écriture en micro-batches vers BigQuery...")

    # 4. Chargement : Écriture en continu vers BigQuery
    query = start_bigquery_stream(df_transactions)

    # Maintien du pipeline actif
    query.awaitTermination()

if __name__ == "__main__":
    main()