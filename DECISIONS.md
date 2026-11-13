# Fiche de décisions

| Choix | Options envisagées | Choix retenu et justification | Validé par l'auxiliaire (date) |
|---|---|---|---|
| Variable cible | KWH total ; Taux d'utilisation ; Nombre de recharges | **KWH total** (consommation mensuelle d'une borne, en kWh) : c'est la grandeur demandée par le sujet, et c'est une valeur numérique (régression). | |
| Caractéristiques | Toutes les colonnes ; seulement les colonnes connues à l'avance | **Latitude, Longitude, Nombre de borne, Arrondissement, mois.** Exclusion de « Nombre de recharge », « Temps de connexion », « Taux d'utilisation », etc. : elles sont calculées avec la consommation, ce qui donnerait une fausse prédiction (fuite d'information). | |
| Métrique | Exactitude (inadaptée à une régression) ; MAE ; R² ; RMSE | **RMSE** (même unité que la cible, pénalise les grosses erreurs), complétée par MAE et R². | |
| Modèle | Régression linéaire ; forêt aléatoire | **Forêt aléatoire** (100 arbres, min_samples_leaf=3) : RMSE 1027 contre 1544 pour la régression linéaire et 1973 pour la référence (moyenne), sur séparation aléatoire. | |
| Méthode de séparation | Séparation aléatoire ; séparation par borne | Les deux sont comparées. Par borne (bornes jamais vues) : R² = 0,40 et RMSE 1481 contre 1912 pour la référence. C'est le chiffre le plus honnête pour prédire un nouvel emplacement. | |