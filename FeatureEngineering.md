# Feature Engineering — Credit Card Fraud Detection

## Pourquoi pas de data leakage ?

Toutes ces features utilisent uniquement des informations disponibles
au moment de la transaction — pas d'informations futures.
Si on utilisait par exemple "le client a fait une réclamation 3 jours
après", ce serait du data leakage et le modèle tricherait.
Ici tout est propre.

---

## Nouvelles Features

---

### 1. `amount_log`
- **Formule**       : `log1p(amount)`
- **Problème résolu**: `amount` varie de 0.01$ à 1471$ — échelle trop
  large. Le modèle ML a du mal avec des valeurs aussi dispersées car
  1471 écrase les petites valeurs.
- **Solution**      : Le logarithme compresse cette échelle pour que
  0.1$ et 1000$ soient traités de façon plus équilibrée.
  `log1p` au lieu de `log` car il gère le cas amount = 0 sans erreur.
- **Exemple** :
Sans log :  0.1 → 1 → 10 → 100 → 1000    écart énorme
Avec log :  0.1 → 0.7 → 2.4 → 4.6 → 6.9  écart réduit
---

### 2. `amount_zscore`
- **Formule**        : `Z = (amount - moyenne) / écart-type`
- **Problème résolu** : Détecter les montants anormalement élevés
  ou bas par rapport au comportement habituel.
- **Solution**       : Le Z-score mesure à quel point un montant est
  inhabituel. Un achat de 1400$ quand la moyenne est 176$ sera
  immédiatement détecté comme anomalie.
- **Lecture** :
Z ≈ 0        → montant normal
Z > 3        → montant anormalement élevé
Z < -3       → montant anormalement bas
---

### 3. `amount_bin`
- **Formule**        : Quantile-based buckets
                       (petit / moyen / grand / très grand)
- **Problème résolu** : Le montant brut ne capture pas le pattern
  en U des fraudes.
- **Solution**       : Créer des catégories permet au modèle de
  capturer que les fraudes arrivent surtout dans les très petits
  montants (card probing ~0.1$) ET les très grands montants —
  un pattern que le montant brut ne voit pas.

---

### 4. `high_amount`
- **Formule**        : `1 si amount > 75ème percentile, sinon 0`
- **Problème résolu** : Identifier les grosses transactions
  de façon simple et directe.
- **Solution**       : Flag binaire — la transaction est-elle dans
  le top 25% des montants ? Combiné avec `foreign_transaction = 1`,
  ce flag devient un signal fort pour le modèle.

---

### 5. `is_night`
- **Formule**        : `1 si transaction_hour ∈ [0, 5], sinon 0`
- **Problème résolu** : `transaction_hour` brut (0 à 23) est difficile
  à exploiter directement.
- **Solution**       : L'EDA montre que les fraudes se concentrent
  entre 0h et 3h avec un pic à 8.9% à minuit contre une moyenne
  de 1.52%. Un flag direct est plus efficace que l'heure brute.
- **Pourquoi la nuit ?** : La victime dort, les équipes de surveillance
  bancaire sont réduites, plus de temps avant le blocage de la carte.

---

### 6. `high_velocity`
- **Formule**        : `1 si velocity_last_24h > médiane, sinon 0`
- **Problème résolu** : Capturer le comportement d'urgence du fraudeur.
- **Solution**       : Les fraudeurs multiplient rapidement les
  transactions avant le blocage de la carte.
  Vélocité moyenne fraude = 3.2 contre 2.0 pour les légitimes.
  Ce flag binaire capture cette différence directement.

---

### 7. `risk_score`
- **Formule**        :
  `foreign_transaction + location_mismatch + high_velocity`
- **Problème résolu** : Un seul signal ne suffit pas à détecter
  la fraude de façon fiable.
- **Solution**       : Combiner les 3 signaux comportementaux les
  plus forts (confirmés par l'EDA) en un seul score composite de 0 à 3.
- **Lecture** :
0  → aucun signal de risque   → probablement légitime
1  → un signal                → surveillance modérée
2  → deux signaux             → risque élevé
3  → trois signaux combinés   → très probablement fraude

- **Exemple** : Un fraudeur qui opère depuis l'étranger +
  incohérence géographique + haute vélocité obtient un score de 3
  — signal composite extrêmement puissant.

---

## Résumé

| Feature         | Formule                                                   | Problème résolu        | Signal apporté          |
|-----------------|-----------------------------------------------------------|------------------------|-------------------------|
| `amount_log`    | `log1p(amount)`                                           | Échelle trop large     | Distribution équilibrée |
| `amount_zscore` | `(amount - mean) / std`                                   | Montant inhabituel     | Détection d'anomalie    |
| `amount_bin`    | Quantile buckets                                          | Pattern en U           | Catégories de montant   |
| `high_amount`   | `amount > 75th percentile`                                | Gros montant           | Flag binaire simple     |
| `is_night`      | `transaction_hour ∈ [0, 5]`                               | Heure risquée          | Flag nocturne direct    |
| `high_velocity` | `velocity_last_24h > médiane`                             | Transactions rapides   | Flag comportemental     |
| `risk_score`    | `foreign_transaction + location_mismatch + high_velocity` | Signal isolé faible    | Score composite 0–3     |