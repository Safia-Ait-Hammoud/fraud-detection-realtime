# Documentation de l'API REST - Détection de Fraude en Temps Réel

Cette API, développée avec le framework **FastAPI**, sert de couche d'accès aux données analytiques et transactionnelles stockées au sein de Google BigQuery après leur traitement par le pipeline PySpark Streaming. Elle génère automatiquement une documentation interactive Swagger conforme aux spécifications OpenAPI 3.1.

---

## 1. Architecture et Spécifications Techniques

* **Framework Core :** FastAPI (Python 3.12+)
* **Serveur ASGI :** Uvicorn
* **Port par défaut :** `8000`
* **Accès Swagger UI :** `http://localhost:8000/docs`
* **Accès ReDoc :** `http://localhost:8000/redoc`
* **Base de données :** Google BigQuery (Client Cloud natif)

---

## 2. Configuration et Variables d'Environnement

L'API requiert l'accès sécurisé aux ressources de clés de service Google Cloud. Les variables d'environnement suivantes doivent être configurées :

| Variable                           | Description                                           | Valeur par défaut / Exemple    |
| :--------------------------------- | :---------------------------------------------------- | :------------------------------ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Chemin absolu vers le fichier de clé de service JSON | `config/gcp-credentials.json` |
| `BIGQUERY_PROJECT_ID`            | Identifiant du projet Google Cloud Platform (GCP)     | fraud-detection-project-497521  |
| `BIGQUERY_DATASET`               | Nom du jeu de données BigQuery                       | `fraud_detection`             |
| `API_HOST`                       | Interface réseau d'écoute de l'API                  | `0.0.0.0`                     |
| `API_PORT`                       | Port d'exposition réseau                             | `8000`                        |

---

## 3. Guide de Démarrage Rapide

### En local (Mode Développement)

1. Activez votre environnement virtuel et positionnez-vous dans le répertoire de l'API :

   ```bash
   cd api
   ```
2. Installez les dépendances spécifiques :

   ```bash
   pip install -r requirements.txt
   ```
3. Lancez le serveur applicatif avec rechargement automatique :

   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

### Via Docker (Mode Production)

La construction de l'image s'exécute depuis le répertoire racine `api/` pour inclure correctement le contexte des dépendances :

```bash
# Construction de l'image isolée
docker build -t fraud-detection-api:latest -f docker/Dockerfile.api .

# Exécution du conteneur avec injection des variables et volumes
docker run -d \
  -p 8000:8000 \
  -v "$(pwd)/../config:/app/config" \
  -e GOOGLE_APPLICATION_CREDENTIALS="/app/config/gcp-credentials.json" \
  --name fraud-api-service \
  fraud-detection-api:latest
```

---

## 4. Référence des Endpoints (Routes API)

### Analytics

#### `GET /statistics`

Récupère les indicateurs clés de performance (KPI) globaux calculés à partir de la table consolidée dans BigQuery.

* **Réponse de succès (200 OK) :**

  ```json
  {
    "total_transactions": 145080,
    "total_frauds": 11098,
    "fraud_rate_percentage": 7.65,
    "average_confidence_score": 0.8942
  }
  ```

---

### Transactions

#### `GET /transactions/recent`

Extrait la liste chronologique des dernières transactions ingérées par le pipeline, qu'elles soient légitimes ou suspectes.

* **Paramètres de requête (Query Params) :**

  * `limit` (integer, optionnel, défaut : `50`, max : `100`) : Nombre d'enregistrements à retourner.
* **Réponse de succès (200 OK) :**

  ```json
  [
    {
      "transaction_id": "TXN-89472014",
      "timestamp": "2026-06-11 15:04:12 UTC",
      "amount": 1250.00,
      "transaction_hour": 15,
      "merchant_category": "Retail",
      "foreign_transaction": 0,
      "location_mismatch": 1,
      "device_trust_score": 0.34,
      "velocity_last_24h": 4.2,
      "cardholder_age": 28
    }
  ]
  ```

---

### Fraudes

#### `GET /frauds/today`

Filtre et extrait exclusivement les alertes de fraude détectées par les modèles de Machine Learning (XGBoost/Random Forest) durant la journée en cours (`CURRENT_DATE`), triées par score de confiance décroissant.

* **Paramètres de requête (Query Params) :**

  * `limit` (integer, optionnel, défaut : `50`, max : `100`) : Nombre maximum d'alertes à afficher.
* **Réponse de succès (200 OK) :**

  ```json
  [
    {
      "transaction_id": "TXN-99421034",
      "timestamp": "2026-06-11 14:58:33 UTC",
      "amount": 4200.50,
      "merchant": "CryptoExchange",
      "confidence_score": 0.9876,
      "is_fraud": true
    }
  ]
  ```

---

### Vérification d'état (Healthcheck)

#### `GET /` ou `GET /health`

Vérifie la disponibilité opérationnelle de l'instance de l'API. Utilisé par le mécanisme de Healthcheck de Docker et les orchestrateurs de conteneurs.

* **Réponse de succès (200 OK) :**

  ```json
  {
    "status": "online",
    "message": "Bienvenue sur l'API de détection de fraude."
  }
  ```

---

## 5. Schémas de Données (Pydantic Validation)

L'API assure la validation stricte des structures de données entrantes et sortantes grâce aux types natifs de Pydantic :

```python
class Transaction(BaseModel):
    transaction_id: str          # Identifiant unique de la transaction
    timestamp: Optional[str]     # Horodatage d'insertion ISO
    amount: float                # Montant de la transaction en devise de référence
    transaction_hour: int        # Heure de la transaction (0-23)
    merchant_category: str       # Secteur d'activité du commerçant
    foreign_transaction: int     # Indicateur de transaction à l'étranger (0 ou 1)
    location_mismatch: int       # Incohérence géographique détectée (0 ou 1)
    device_trust_score: float    # Score de confiance du terminal (0.0 à 1.0)
    velocity_last_24h: float     # Nombre de transactions effectuées en 24h
    cardholder_age: int          # Âge du titulaire de la carte
```

---

## 6. Gestion des Erreurs et Statuts

L'API encapsule ses erreurs de traitement ou de connectivité sous des formats JSON explicites :

* **422 Unprocessable Entity :** Les paramètres fournis ou le payload JSON ne respectent pas le schéma de validation Pydantic requis.
* **500 Internal Server Error :** Erreur interne lors de l'exécution des requêtes SQL sur le cluster BigQuery ou problème de droits d'accès GCP.

```json
{
  "detail": "Erreur lors de la récupération des fraudes : 400 ProjectId must be non-empty"
}
```
