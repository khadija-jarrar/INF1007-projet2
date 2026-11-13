# INF1007-projet2
## Modèle

- **Cible** : consommation mensuelle d'une borne (KWH total).
- **Modèle retenu** : forêt aléatoire (scikit-learn), sauvegardée avec joblib.
- **Métrique** : RMSE (avec MAE et R²).

| Évaluation | RMSE référence | RMSE forêt | R² forêt |
|---|---|---|---|
| Séparation aléatoire | 1973 | 1027 | 0,73 |
| Séparation par borne | 1912 | 1481 | 0,40 |

**Limites** : une même borne apparaît environ 12 fois (une ligne par mois). Avec une séparation aléatoire, le modèle peut avoir vu la borne à l'entraînement, ce qui rend le score optimiste. Sur des bornes jamais vues, l'erreur moyenne est d'environ 1100 kWh (MAE).

**Outil du chapitre 7** : le décorateur `chronometre` (dans `src/modele.py`) mesure la durée de chaque entraînement.

**Commandes** :
- Entraîner : `python -m src.entrainement`
- Évaluer et tracer le graphique : `python -m src.evaluation`
- Comparer les séparations : `python -m src.validation_groupes`
**Couverture de tests** : 43 % (mesurée avec `coverage run --source=src -m pytest`). Les scripts lancés à la main (`evaluation.py`, `validation_groupes.py`) ne sont pas testés, et `donnees.py` n'a pas encore de tests.