from database_writer import start_bigquery_stream
from ml_inference import apply_ml_model
from kafka_consumer import read_from_kafka, parse_kafka_payload
from pyspark.sql import SparkSession
from dotenv import load_dotenv
from pathlib import Path
import os
import sys

# ==============================================================================
# CONFIGURATION ENVIRONNEMENT (Dynamique OS)
# ==============================================================================
if os.name == 'nt':
    VENV_PYTHON = "C:\\fraud\\venv\\Scripts\\python.exe"
    os.environ["PYSPARK_PYTHON"] = VENV_PYTHON
    os.environ["PYSPARK_DRIVER_PYTHON"] = VENV_PYTHON
    os.environ["HADOOP_HOME"] = "C:\\hadoop"
    os.environ["JAVA_HOME"] = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.6.10-hotspot"
    os.environ["SPARK_LOCAL_DIRS"] = r"C:\Temp"


BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = BASE_DIR / "config" / ".env"

if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)


def create_spark_session():
    gcp_credentials = os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS", str(BASE_DIR / "config" / "gcp-credentials.json")
    )

    spark_packages = ",".join(
        [
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0",
            "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.36.1",
        ]
    )

    # 1. Initialisation de la configuration de base (Commune à Windows et Linux)
    builder = (
        SparkSession.builder.appName("FraudDetection_Streaming_Pipeline")
        .master("local[*]")
        .config("spark.jars.packages", spark_packages)
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .config("spark.files.overwrite", "true")
        .config("spark.hadoop.google.cloud.auth.service.account.enable", "true")
        .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", gcp_credentials)
        .config("credentialsFile", gcp_credentials)
    )

    # 2. Ajout des configurations spécifiques si on est sous Windows
    if os.name == 'nt':
        builder = (
            builder
            .config("spark.pyspark.python", "C:\\fraud\\venv\\Scripts\\python.exe")
            .config("spark.pyspark.driver.python", "C:\\fraud\\venv\\Scripts\\python.exe")
            .config("spark.hadoop.hadoop.home.dir", "C:\\hadoop")
            .config("spark.local.dir", "C:\\spark-tmp")
            .config(
                "spark.driver.extraJavaOptions",
                "--add-opens=java.base/java.nio=ALL-UNNAMED "
                "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED "
                "--add-opens=java.base/java.lang=ALL-UNNAMED",
            )
            .config(
                "spark.executor.extraJavaOptions",
                "--add-opens=java.base/java.nio=ALL-UNNAMED " 
                "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED",
            )
        )

    return builder.getOrCreate()


def main():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("FATAL")

    streaming_dir = os.path.dirname(os.path.abspath(__file__))
    spark.sparkContext.addPyFile(os.path.join(streaming_dir, "ml_inference.py"))
    spark.sparkContext.addPyFile(os.path.join(streaming_dir, "kafka_consumer.py"))
    spark.sparkContext.addPyFile(os.path.join(streaming_dir, "database_writer.py"))

    print(" Démarrage du pipeline PySpark Streaming...")
    print(" Connexion au flux Kafka...")
    df_raw = read_from_kafka(spark)

    print(" Parsing du payload JSON...")
    df_transactions = parse_kafka_payload(df_raw)

    print(" Application du modèle de Machine Learning (Pandas UDF)...")
    df_enrichi = apply_ml_model(df_transactions)

    print(" Envoi du flux continu vers Google BigQuery...")
    query = start_bigquery_stream(df_enrichi)

    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print("\n Arrêt manuel du pipeline PySpark.")
        query.stop()


if __name__ == "__main__":
    main()