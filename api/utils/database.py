import os
import logging
from pathlib import Path
from google.cloud import bigquery
from google.api_core.client_options import ClientOptions

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
gcp_key_path = BASE_DIR / "config" / "gcp-credentials.json"

if gcp_key_path.exists():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(gcp_key_path)
else:
    logger.warning(f"Fichier de credentials introuvable : {gcp_key_path}")

BIGQUERY_PROJECT_ID = os.getenv("PROJECT_ID", "fraud-detection-project-497521")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "fraud_detection")

def get_bq_client():
    """Initialise et retourne le client BigQuery."""
    try:
        emulator_host = os.getenv("BIGQUERY_EMULATOR_HOST")
        if emulator_host:
            options = ClientOptions(api_endpoint=f"http://{emulator_host}")
            return bigquery.Client(project=BIGQUERY_PROJECT_ID, client_options=options)
        
        return bigquery.Client(project=BIGQUERY_PROJECT_ID)
    except Exception as e:
        logger.error(f"Erreur de connexion à BigQuery: {e}")
        raise