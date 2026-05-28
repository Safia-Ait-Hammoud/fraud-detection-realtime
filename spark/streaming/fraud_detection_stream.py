# spark/streaming/fraud_detection_stream.py

import os
from pathlib import Path
from dotenv import load_dotenv
from pyspark.sql import SparkSession

os.environ["JAVA_HOME"] = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.6.10-hotspot"
os.environ["SPARK_LOCAL_DIRS"] = r"C:\Temp"

from kafka_consumer import read_from_kafka, parse_kafka_payload
from ml_inference import apply_ml_model
from database_writer import start_bigquery_stream

BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = BASE_DIR / 'config' / '.env'

print(f"Chemin du fichier .env : {dotenv_path}")
print(f"Le fichier existe-t-il vraiment sur Windows ? : {dotenv_path.exists()}")

if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)

def create_spark_session():
    # Chemin vers ton fichier de credentials GCP
    gcp_credentials = os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS",
        str(BASE_DIR / "config" / "gcp-credentials.json")
    )

    spark_packages = ",".join([
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0",
        "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.36.1",
    ])

    return SparkSession.builder \
        .appName("FraudDetection_Streaming_Pipeline") \
        .master("local[*]") \
        .config("spark.jars.packages", spark_packages) \
        .config("spark.driver.extraJavaOptions",
                "--add-opens=java.base/java.nio=ALL-UNNAMED "
                "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED "
                "--add-opens=java.base/java.lang=ALL-UNNAMED") \
        .config("spark.executor.extraJavaOptions",
                "--add-opens=java.base/java.nio=ALL-UNNAMED "
                "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED") \
        .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
        .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", gcp_credentials) \
        .config("credentialsFile", gcp_credentials) \
        .getOrCreate()

def main():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print("Démarrage du pipeline PySpark Streaming...")
    print("Connexion au flux Kafka...")
    df_raw = read_from_kafka(spark)

    df_transactions = parse_kafka_payload(df_raw)

    print("Application du modèle de Machine Learning...")
    df_enrichi = apply_ml_model(df_transactions)

    print("Envoi du flux continu vers Google BigQuery...")
    query = start_bigquery_stream(df_enrichi)

    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print("\nArrêt manuel du pipeline PySpark.")
        query.stop()

if __name__ == "__main__":
    main()