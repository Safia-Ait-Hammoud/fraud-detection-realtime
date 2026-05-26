from google.cloud import bigquery
from dotenv import load_dotenv
import os

# Charge la clé GCP depuis le fichier .env
load_dotenv()

try:
    # Initialise le client BigQuery
    client = bigquery.Client()
    print("Connexion BigQuery réussie !")
    print(f"Projet GCP connecté : {client.project}")
except Exception as e:
    print(f"Erreur de connexion : {e}")