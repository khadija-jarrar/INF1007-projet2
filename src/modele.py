"""Entraînement, évaluation, sauvegarde et prédiction du modèle."""
import json
import os
import time
from functools import wraps
from typing import Callable

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.exceptions import (
    DonneeInvalideError,
    ModeleIntrouvableError,
    ModeleNonEntraineError,
)

SEED = 42
DOSSIER_MODELES = "modeles"
CHEMIN_MODELE = os.path.join(DOSSIER_MODELES, "modele.joblib")
CHEMIN_METADONNEES = os.path.join(DOSSIER_MODELES, "metadonnees.json")


def chronometre(fonction: Callable) -> Callable:
    """Affiche le temps d'exécution de la fonction décorée."""
    @wraps(fonction)
    def enveloppe(*args, **kwargs):
        debut = time.perf_counter()
        resultat = fonction(*args, **kwargs)
        print(f"[chrono] {fonction.__name__} : {time.perf_counter() - debut:.2f} s")
        return resultat
    return enveloppe


def rmse_numpy(y_vrai: np.ndarray, y_pred: np.ndarray) -> float:
    """Calcule le RMSE avec NumPy (vectorisé).

    Reçoit deux tableaux de même taille. Renvoie le RMSE (float).
    Lève DonneeInvalideError si les tailles diffèrent ou si les tableaux sont vides.
    """
    y_vrai = np.asarray(y_vrai, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if y_vrai.shape != y_pred.shape or y_vrai.size == 0:
        raise DonneeInvalideError("Tableaux vides ou de tailles différentes.")
    return float(np.sqrt(np.mean((y_vrai - y_pred) ** 2)))


def separer_donnees(df: pd.DataFrame, cible: str, taille_test: float = 0.2):
    """Sépare le DataFrame en X_train, X_test, y_train, y_test (graine fixée).

    Lève DonneeInvalideError si la colonne cible est absente.
    """
    if cible not in df.columns:
        raise DonneeInvalideError(f"Colonne cible absente : {cible}")
    X = df.drop(columns=[cible])
    y = df[cible]
    return train_test_split(X, y, test_size=taille_test, random_state=SEED)


def colonnes_categorielles(X: pd.DataFrame) -> list[str]:
    """Renvoie les noms des colonnes non numériques (catégorielles) de X."""
    return [c for c in X.columns if not pd.api.types.is_numeric_dtype(X[c])]


class Modele:
    """Enveloppe un estimateur scikit-learn et son pré-traitement."""

    def __init__(self, estimateur, colonnes_cat: list[str], nom: str = "modele"):
        self.nom = nom
        self._estimateur = estimateur
        self._colonnes_cat = colonnes_cat
        self._pipeline: Pipeline | None = None

    @chronometre
    def entrainer(self, X: pd.DataFrame, y: pd.Series) -> None:
        """Entraîne le pipeline (encodage des catégories + estimateur)."""
        prepro = ColumnTransformer(
            [("cat", OneHotEncoder(handle_unknown="ignore"), self._colonnes_cat)],
            remainder="passthrough",
        )
        self._pipeline = Pipeline([("prepro", prepro), ("modele", self._estimateur)])
        self._pipeline.fit(X, y)

    def predire(self, X: pd.DataFrame) -> np.ndarray:
        """Renvoie les prédictions. Lève ModeleNonEntraineError si pas entraîné."""
        if self._pipeline is None:
            raise ModeleNonEntraineError("Le modèle n'est pas entraîné.")
        return self._pipeline.predict(X)

    def evaluer(self, X: pd.DataFrame, y: pd.Series) -> dict[str, float]:
        """Renvoie RMSE, MAE et R² (à calculer sur l'ensemble de test)."""
        pred = self.predire(X)
        return {
            "rmse": rmse_numpy(y.to_numpy(), pred),
            "mae": float(mean_absolute_error(y, pred)),
            "r2": float(r2_score(y, pred)),
        }

    def sauvegarder(self, chemin: str = CHEMIN_MODELE) -> None:
        """Enregistre le pipeline avec joblib."""
        if self._pipeline is None:
            raise ModeleNonEntraineError("Rien à sauvegarder : modèle non entraîné.")
        os.makedirs(os.path.dirname(chemin) or ".", exist_ok=True)
        joblib.dump(self._pipeline, chemin)

    @staticmethod
    def charger(chemin: str = CHEMIN_MODELE) -> "Modele":
        """Recharge un modèle sauvegardé. Lève ModeleIntrouvableError si absent."""
        if not os.path.exists(chemin):
            raise ModeleIntrouvableError(f"Fichier introuvable : {chemin}")
        pipeline = joblib.load(chemin)
        modele = Modele(pipeline.named_steps["modele"], [], nom="charge")
        modele._pipeline = pipeline
        return modele

    def __str__(self) -> str:
        etat = "entraîné" if self._pipeline is not None else "non entraîné"
        return f"Modele({self.nom}, {type(self._estimateur).__name__}, {etat})"


def construire_metadonnees(X: pd.DataFrame, cible: str, metriques: dict) -> dict:
    """Décrit les colonnes d'entrée pour que l'interface se construise toute seule."""
    cats = colonnes_categorielles(X)
    nums = [c for c in X.columns if c not in cats]
    return {
        "cible": cible,
        "colonnes": list(X.columns),
        "numeriques": {c: {"min": float(X[c].min()), "max": float(X[c].max())} for c in nums},
        "categorielles": {c: sorted(X[c].dropna().unique().tolist()) for c in cats},
        "metriques": metriques,
    }


def ecrire_metadonnees(meta: dict, chemin: str = CHEMIN_METADONNEES) -> None:
    """Écrit les métadonnées en JSON."""
    os.makedirs(os.path.dirname(chemin) or ".", exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def lire_metadonnees(chemin: str = CHEMIN_METADONNEES) -> dict:
    """Lit les métadonnées. Lève ModeleIntrouvableError si le fichier est absent."""
    if not os.path.exists(chemin):
        raise ModeleIntrouvableError(f"Fichier introuvable : {chemin}")
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


def entrainer_et_sauvegarder(df: pd.DataFrame, cible: str) -> dict:
    """Compare référence, régression linéaire et forêt; sauvegarde la meilleure."""
    X_train, X_test, y_train, y_test = separer_donnees(df, cible)
    cats = colonnes_categorielles(X_train)

    candidats = {
        "reference_moyenne": DummyRegressor(strategy="mean"),
        "regression_lineaire": LinearRegression(),
        "foret_aleatoire": RandomForestRegressor(n_estimators=200, random_state=SEED),
    }
    resultats, modeles = {}, {}
    for nom, estimateur in candidats.items():
        m = Modele(estimateur, cats, nom)
        m.entrainer(X_train, y_train)
        resultats[nom] = m.evaluer(X_test, y_test)
        modeles[nom] = m

    meilleur = min(
        (n for n in resultats if n != "reference_moyenne"),
        key=lambda n: resultats[n]["rmse"],
    )
    modeles[meilleur].sauvegarder()
    X_complet = df.drop(columns=[cible])
    ecrire_metadonnees(construire_metadonnees(X_complet, cible, {
        "modele": meilleur, **resultats[meilleur],
        "rmse_reference": resultats["reference_moyenne"]["rmse"],
    }))
    return resultats


if __name__ == "__main__":
    # À remplacer par la fonction de chargement de src/donnees.py
    df = pd.read_csv("donnees/donnees_nettoyees.csv")
    for nom, scores in entrainer_et_sauvegarder(df, "consommation_kwh").items():
        print(nom, scores)