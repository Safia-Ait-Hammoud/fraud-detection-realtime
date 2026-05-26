from fastapi import APIRouter

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.get("/recent")
def get_recent_transactions():
    return {
        "message": "Endpoint transactions récentes prêt. En attente des données BigQuery.",
        "data": []
    }
