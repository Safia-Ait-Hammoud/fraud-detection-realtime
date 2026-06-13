import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import statistics, transactions, frauds


# Initialisation de l'API avec documentation Swagger automatique
app = FastAPI(
    title="API Détection de Fraude temps réel",
    description="API permettant l'ingestion de transactions et la consultation des alertes BigQuery.",
    version="1.0.0"
)

# Sécurité (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routes
app.include_router(statistics.router)
app.include_router(transactions.router)
app.include_router(frauds.router)

@app.get("/", tags=["Health"])
def root():
    return {"status": "online", "message": "Bienvenue sur l'API de détection de fraude."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)