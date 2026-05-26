from fastapi import APIRouter

router = APIRouter(
    prefix="/statistics",
    tags=["Statistiques"]
)

@router.get("")
def get_statistics():
    return {
        "message": "Endpoint statistiques prêt. En attente des données BigQuery.",
        "statistics": {
            "total_transactions": 0,
            "total_frauds": 0,
            "fraud_rate": 0.0,
            "average_amount": 0.0
        }
    }
