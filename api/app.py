from fastapi import FastAPI

from routes.transactions import router as transactions_router
from routes.frauds import router as frauds_router
from routes.statistics import router as statistics_router

app = FastAPI(
    title="Fraud Detection API",
    description="API REST pour consulter les transactions et les statistiques de fraude",
    version="1.0.0"
)

app.include_router(transactions_router)
app.include_router(frauds_router)
app.include_router(statistics_router)

@app.get("/")
def home():
    return {
        "message": "Fraud Detection API is running",
        "docs": "/docs",
        "available_endpoints": [
            "/transactions/recent",
            "/frauds/today",
            "/statistics"
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
