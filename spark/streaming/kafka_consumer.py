import os
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
from pyspark.sql.functions import col, from_json

# ==============================================================================
# 1. DÉFINITION DU SCHÉMA DE DONNÉES
# ==============================================================================
kafka_schema = StructType(
    [
        StructField("transaction_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("transaction_hour", IntegerType(), True),
        StructField("merchant_category", StringType(), True),
        StructField("foreign_transaction", IntegerType(), True),
        StructField("location_mismatch", IntegerType(), True),
        StructField("device_trust_score", DoubleType(), True),
        StructField("velocity_last_24h", DoubleType(), True),
        StructField("cardholder_age", IntegerType(), True),
    ]
)

# ==============================================================================
# 2. LECTURE DU FLUX KAFKA
# ==============================================================================
def read_from_kafka(spark, topic="bank-transactions"):
    """
    Établit la connexion avec le broker Kafka et s'abonne au topic cible.
    Retourne un DataFrame binaire brut en streaming.
    """
    # Récupération dynamique de l'adresse du broker (Docker vs Local)
    bootstrap_servers = os.getenv("KAFKA_BROKER", "localhost:29092")
    
    print(f" Tentative de connexion au broker Kafka : {bootstrap_servers} sur le topic '{topic}'...")

    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", bootstrap_servers)
        .option("subscribe", topic)
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
    )

# ==============================================================================
# 3. PARSING ET STRUCTURATION DES DONNÉES
# ==============================================================================
def parse_kafka_payload(df_raw):
    """
    Transforme le flux binaire Kafka en données structurées.
    - Convertit la valeur binaire en chaîne JSON.
    - Applique le schéma strict pour éclater le JSON en colonnes SQL distinctes.
    """
    # 1. Cast de la valeur binaire brute en chaîne de caractères (String)
    df_string = df_raw.selectExpr("CAST(value AS STRING) as json_string")

    # 2. Application du schéma JSON pour extraire les colonnes
    df_parsed = df_string.select(from_json(col("json_string"), kafka_schema).alias("data")).select("data.*")

    return df_parsed