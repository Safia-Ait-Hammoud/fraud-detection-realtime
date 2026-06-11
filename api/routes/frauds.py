from fastapi import APIRouter, HTTPException, Query
from utils.database import get_bq_client, BIGQUERY_PROJECT_ID, BIGQUERY_DATASET
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/frauds/today", tags=["Frauds"])
def get_todays_frauds(limit: int = Query(50, description="Nombre max d'alertes à afficher", le=100)):
    """
    Récupère la liste des fraudes détectées aujourd'hui.
    """
    try:
        client = get_bq_client()
        query = f"""
            SELECT 
                transaction_id, timestamp, amount, merchant_category, 
                confidence_score, is_fraud
            FROM `{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET}.transactions`
            WHERE is_fraud = 1 
              AND DATE(TIMESTAMP(timestamp)) = CURRENT_DATE()
            ORDER BY confidence_score DESC, timestamp DESC
            LIMIT {limit}
        """
        
        results = client.query(query).result()
        
        frauds = []
        for row in results:
            frauds.append({
                "transaction_id": row.transaction_id,
                "timestamp": str(row.timestamp),
                "amount": row.amount,
                "merchant": row.merchant_category,
                "confidence_score": round(row.confidence_score, 4),
                "is_fraud": bool(row.is_fraud)
            })
        return frauds

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des fraudes : {str(e)}")