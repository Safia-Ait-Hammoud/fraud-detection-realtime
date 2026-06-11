from fastapi import APIRouter, HTTPException
from utils.database import get_bq_client, BIGQUERY_PROJECT_ID, BIGQUERY_DATASET

router = APIRouter()

@router.get("/statistics", tags=["Analytics"])
def get_global_statistics():
    """Récupère les KPI globaux de la détection de fraude."""
    try:
        client = get_bq_client()
        query = f"""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) as fraud_count,
                AVG(confidence_score) as avg_fraud_score
            FROM `{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET}.transactions`
        """
        results = list(client.query(query).result())
        
        if results:
            row = results[0]
            total = row.total_transactions or 0
            frauds = row.fraud_count or 0
            return {
                "total_transactions": total,
                "total_frauds": frauds,
                "fraud_rate_percentage": round((frauds / total * 100), 2) if total > 0 else 0,
                "average_confidence_score": round(row.avg_fraud_score or 0, 4)
            }
        return {"error": "Aucune donnée trouvée"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))