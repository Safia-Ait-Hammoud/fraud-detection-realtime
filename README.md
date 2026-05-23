# 🔍 Fraud Detection Realtime

Système de détection de fraude bancaire en temps réel.
Pipeline complet : entraînement ML (Random Forest + XGBoost) → streaming Kafka → traitement Spark → stockage BigQuery → visualisation Grafana. Déployé sur AWS.

---

## 🏗️ Architecture

```
Transactions CSV
      ↓
Kafka Producer
      ↓
Spark Streaming  →  Modèle ML (best_model.pkl)
      ↓
BigQuery
      ↓
Grafana Dashboard
```

---

## 📁 Structure du projet

```
fraud-detection-realtime/
├── data/               # Données brutes et préparées
├── notebooks/          # Exploration, entraînement, évaluation
├── ml-models/          # Scripts ML + modèles sauvegardés
├── sql/                # Schémas et requêtes BigQuery
├── scripts/            # Setup, déploiement, monitoring
├── config/             # Configurations local et cloud
├── docker/             # Dockerfiles et Docker Compose
└── docs/               # Documentation et diagrammes
```

---

## ⚙️ Stack technique

| Composant | Technologie |
|---|---|
| ML | Random Forest, XGBoost, scikit-learn |
| Streaming | Apache Kafka |
| Traitement | Apache Spark (PySpark) |
| Base de données | BigQuery |
| Monitoring | Prometheus + Grafana |
| Cloud | AWS |
| Conteneurisation | Docker |

---

## 🚀 Installation

```bash
# 1. Cloner le repo
git clone https://github.com/votre-user/fraud-detection-realtime.git
cd fraud-detection-realtime

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer l'environnement
cp config/.env.example config/.env
# Remplir les variables dans config/.env

# 4. Lancer les services
docker-compose up -d
```


---

## 📊 Dataset

- **Source** : [Kaggle — Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- **Features** : V1-V28 (PCA), Time, Amount
- **Target** : Class (0 = normal, 1 = fraude)
- **Déséquilibre** : ~0.17% de fraudes → traité avec SMOTE

---

## 👥 Équipe

| Binôme | Rôle |
|---|---|
| Binôme 1 | Data & ML + Kafka |
| Binôme 2 | Pipeline Spark + BDD & API |
| Binôme 3 | Infra Cloud + DevOps & Monitoring |

---
