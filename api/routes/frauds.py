from fastapi import APIRouter

router = APIRouter(
    prefix="/frauds",
    tags=["Fraudes"]
)

@router.get("/today")
def get_frauds_today():
    return {
        "message": "Endpoint fraudes du jour prêt. En attente des données BigQuery.",
        "data": []
    }
