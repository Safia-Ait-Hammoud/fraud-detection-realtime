# Credit Card Fraud Detection — Dataset Features

## Source
- **Platform** : Kaggle
- **URL** : https://www.kaggle.com/datasets/miadul/credit-card-fraud-detection-dataset/data
- **Author** : Miadul
- **Type** : Synthetic dataset (privacy-safe, no real customer data)
- **License** : For educational, research and practice purposes only

---

## Dataset Overview
- **Total Records** : 10,000 transactions
- **Total Features** : 10 (9 input features + 1 target)
- **Target Variable** : is_fraud
- **Task** : Binary Classification (0 = Normal, 1 = Fraud)
- **Class Distribution** : Highly imbalanced — fraud ≈ 1.5% of transactions

---

## Features Description

### 1. transaction_id
- **Type** : int
- **Range** : 1 – 10,000
- **Description** : Unique identifier for each transaction.
- **Signification** : Clé technique sans valeur prédictive. À exclure des modèles ML.

---

### 2. amount
- **Type** : float
- **Range** : 0.00 – 1,471.04
- **Description** : Transaction amount in currency units.
- **Signification** : Montant de la transaction. Peut refléter le comportement d'achat et contribue en combinaison avec d'autres features.

---

### 3. transaction_hour
- **Type** : int
- **Range** : 0 – 23
- **Description** : Hour of the day at which the transaction occurred.
- **Signification** : Signal comportemental temporel. Les fraudes surviennent souvent à des heures inhabituelles comme la nuit ou tôt le matin.

---

### 4. merchant_category
- **Type** : categorical
- **Values** : Food, Clothing, Travel, Grocery, Electronics
- **Description** : Type of merchant involved in the transaction.
- **Signification** : Certains types de commerces sont plus ciblés par les fraudeurs, notamment Travel et Electronics pour leurs achats à forte valeur.

---

### 5. foreign_transaction
- **Type** : binary
- **Values** : 0 = domestic / 1 = international
- **Description** : Indicates whether the transaction was made in a foreign country.
- **Signification** : Signal de risque fort — les fraudeurs opèrent souvent depuis l'étranger avec des cartes volées.

---

### 6. location_mismatch
- **Type** : binary
- **Values** : 0 = match / 1 = mismatch
- **Description** : Discrepancy between billing address and transaction location.
- **Signification** : Une incohérence géographique entre l'adresse de facturation et le lieu de transaction est un indicateur de fraude très discriminant.

---

### 7. device_trust_score
- **Type** : int
- **Range** : 0 – 100
- **Description** : Trust score of the device used. Higher = more trusted device.
- **Signification** : Un score bas indique un appareil inconnu, un VPN ou un navigateur suspect — comportement typique d'un fraudeur.

---

### 8. velocity_last_24h
- **Type** : int
- **Range** : 0 – N
- **Description** : Number of transactions made by the cardholder in the last 24 hours.
- **Signification** : Les fraudeurs multiplient rapidement les transactions avant le blocage de la carte, générant une vélocité anormalement élevée.

---

### 9. cardholder_age
- **Type** : int
- **Range** : 18 – 69
- **Description** : Age of the cardholder.
- **Signification** : Feature démographique. Certaines tranches d'âge peuvent être plus vulnérables à la fraude.

---

### 10. is_fraud ⟵ TARGET
- **Type** : binary
- **Values** : 0 = Normal / 1 = Fraud
- **Description** : Whether the transaction is fraudulent.
- **Signification** : Variable cible. Le fort déséquilibre des classes (98.5% normal / 1.5% fraude) est le défi central du projet.