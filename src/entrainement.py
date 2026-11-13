"""Chargement du CSV des chargeurs et entraînement du modèle."""
import os

import pandas as pd

from src.exceptions import DonneeInvalideError
from src.modele import entrainer_et_sauvegarder

CHEMIN_CSV = os.path.join("donnees", "chargeurs_statistiques_2025.csv")
COLONNE_KWH = "KWH total"
CIBLE = "consommation_kwh"
CARACTERISTIQUES = ["Latitude", "Longitude", "Nombre de borne", "Arrondissement", "mois"]
COLONNES_NUMERIQUES = ["Latitude", "Longitude", "Nombre de borne"]


def convertir_nombre(serie: pd.Series) -> pd.Series:
    """Convertit une colonne texte (ex. '"5691,61765"') en nombres décimaux.

    Reçoit une série. Renvoie une série de floats ; les valeurs non
    convertibles deviennent NaN.
    """
    texte = (
        serie.astype("string")
        .str.replace('"', "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )
    return pd.to_numeric(texte, errors="coerce")


def charger_donnees_modele(chemin: str = CHEMIN_CSV) -> pd.DataFrame:
    """Charge le CSV et renvoie un tableau propre : caractéristiques + cible.

    Lève DonneeInvalideError si le fichier ou une colonne est absent.
    """
    if not os.path.exists(chemin):
        raise DonneeInvalideError(f"Fichier introuvable : {chemin}")
    with open(chemin, "r", encoding="utf-8") as f:
        brut = pd.read_csv(f)

    manquantes = [c for c in CARACTERISTIQUES + [COLONNE_KWH] if c not in brut.columns]
    if manquantes:
        raise DonneeInvalideError(f"Colonnes absentes : {manquantes}")

    df = brut[CARACTERISTIQUES + [COLONNE_KWH]].copy()
    for col in COLONNES_NUMERIQUES:
        df[col] = convertir_nombre(df[col])
    df[CIBLE] = convertir_nombre(df[COLONNE_KWH])
    df = df.drop(columns=[COLONNE_KWH]).dropna()
    df = df[df[CIBLE] > 0]
    return df.reset_index(drop=True)


def main() -> None:
    """Charge les données, entraîne les modèles et affiche les scores."""
    df = charger_donnees_modele()
    print(f"{len(df)} lignes utilisées")
    for nom, scores in entrainer_et_sauvegarder(df, CIBLE).items():
        print(nom, {k: round(v, 2) for k, v in scores.items()})


if __name__ == "__main__":
    main()