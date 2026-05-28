# spark/streaming/kafka_consumer.py

from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType
from pyspark.sql.functions import col, from_json

# 1. Le schéma
kafka_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("amount", FloatType(), True),
    StructField("transaction_hour", IntegerType(), True),
    StructField("merchant_category", StringType(), True),  # <-- Réintégré selon le contrat !
    StructField("foreign_transaction", IntegerType(), True),
    StructField("location_mismatch", IntegerType(), True),
    StructField("device_trust_score", FloatType(), True),
    StructField("velocity_last_24h", IntegerType(), True),
    StructField("cardholder_age", IntegerType(), True)
])

def read_from_kafka(spark, bootstrap_servers="localhost:9092", topic="bank-transactions"):
    """
    Établit la connexion avec le broker Kafka et s'abonne au topic cible.
    Retourne un DataFrame binaire brut en streaming.
    """
    print(f"Tentative de connexion au broker Kafka : {bootstrap_servers} sur le topic '{topic}'...")
    
    return spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", bootstrap_servers) \
        .option("subscribe", topic) \
        .option("startingOffsets", "latest") \
        .option("failOnDataLoss", "false") \
        .load()

def parse_kafka_payload(df_raw):
    """
    Transforme le flux binaire Kafka en données structurées.
    - Convertit la valeur binaire en chaîne JSON.
    - Applique le schéma strict pour éclater le JSON en colonnes SQL distinctes.
    """
    df_string = df_raw.selectExpr("CAST(value AS STRING) as json_string")
    
    df_parsed = df_string \
        .select(from_json(col("json_string"), kafka_schema).alias("data")) \
        .select("data.*")
        
    return df_parsed