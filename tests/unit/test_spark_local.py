# test_spark_local.py
from pyspark.sql import SparkSession

# 1. Initialiser la session Spark locale
spark = SparkSession.builder \
    .appName("FraudDetection_LocalTest") \
    .master("local[*]") \
    .getOrCreate()

# 2. Créer un DataFrame simple pour tester 
data = [("1", 0.0, 150.50, False), ("2", 1.5, 2999.99, True)]
columns = ["transaction_id", "Time", "Amount", "is_fraud"]

df = spark.createDataFrame(data, schema=columns)
df.show()

print("PySpark est correctement configuré et prêt !")