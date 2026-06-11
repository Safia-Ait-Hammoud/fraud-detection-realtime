from fastapi import APIRouter, HTTPException, Query
from typing import List
from models.transaction import Transaction
from utils.database import get_bq_client, BIGQUERY_PROJECT_ID, BIGQUERY_DATASET

router = APIRouter()

@router.get("/transactions/recent", tags=["Transactions"])
def get_recent_transactions(limit: int = Query(50, description="Nombre de transactions à récupérer (max 100)", le=100)):
    """
    Récupère les transactions les plus récentes ingérées dans BigQuery.
    """
    try:
        client = get_bq_client()
        query = f"""
            SELECT 
                transaction_id, timestamp, amount, transaction_hour, 
                merchant_category, foreign_transaction, location_mismatch, 
                device_trust_score, velocity_last_24h, cardholder_age
            FROM `{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET}.transactions`
            ORDER BY timestamp DESC
            LIMIT {limit}
        """
        
        results = client.query(query).result()
        
        transactions = []
        for row in results:
            transactions.append(
                Transaction(
                    transaction_id=row.transaction_id,
                    timestamp=str(row.timestamp),
                    amount=row.amount,
                    transaction_hour=row.transaction_hour,
                    merchant_category=row.merchant_category,
                    foreign_transaction=row.foreign_transaction,
                    location_mismatch=row.location_mismatch,
                    device_trust_score=row.device_trust_score,
                    velocity_last_24h=row.velocity_last_24h,
                    cardholder_age=row.cardholder_age
                )
            )
        return transactions

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des transactions : {str(e)}")