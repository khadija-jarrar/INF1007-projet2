
"""Chargement du CSV des chargeurs et entraînement du modèle."""

import os

import pandas as pd

from src.donnees import charger_donnees
from src.exceptions import DonneeInvalideError
from src.modele import entrainer_et_sauvegarder


CHEMIN_CSV = os.path.join(
    "donnees",
    "chargeurs_statistiques_2025.csv"
)

COLONNE_KWH = "KWH total"
CIBLE = "consommation_kwh"

CARACTERISTIQUES = [
    "Latitude",
    "Longitude",
    "Nombre de borne",
    "Arrondissement",
    "mois"
]

COLONNES_NUMERIQUES = [
    "Latitude",
    "Longitude",
    "Nombre de borne"
]


def convertir_nombre(serie: pd.Series) -> pd.Series:
    """Convertit une série Pandas en nombres décimaux.

    Les valeurs non convertibles deviennent NaN.
    """

    texte = (
        serie.astype("string")
        .str.replace('"', "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )

    return pd.to_numeric(texte, errors="coerce")


def charger_donnees_modele(
    chemin: str = CHEMIN_CSV,
    garder_borne: bool = False
) -> pd.DataFrame:
    """Ancien nettoyage Pandas, conservé pour les tests."""

    if not os.path.exists(chemin):
        raise DonneeInvalideError(
            f"Fichier introuvable : {chemin}"
        )

    with open(chemin, "r", encoding="utf-8") as fichier:
        brut = pd.read_csv(fichier)

    colonnes_requises = (
        CARACTERISTIQUES
        + [COLONNE_KWH]
        + (["Borne"] if garder_borne else [])
    )

    manquantes = [
        colonne
        for colonne in colonnes_requises
        if colonne not in brut.columns
    ]

    if manquantes:
        raise DonneeInvalideError(
            f"Colonnes absentes : {manquantes}"
        )

    df = brut[colonnes_requises].copy()

    for colonne in COLONNES_NUMERIQUES:
        df[colonne] = convertir_nombre(df[colonne])

    df[CIBLE] = convertir_nombre(df[COLONNE_KWH])

    df = df.drop(columns=[COLONNE_KWH]).dropna()
    df = df[df[CIBLE] > 0]

    return df.reset_index(drop=True)


def adapter_donnees_modele(
    chemin: str = CHEMIN_CSV,
    garder_borne: bool = False
) -> pd.DataFrame:
    """Adapte les données nettoyées au format attendu par le modèle.

    Réutilise charger_donnees() pour éviter un second nettoyage.
    """

    donnees = charger_donnees(
        chemin,
        garder_borne=garder_borne
    )

    if not donnees:
        raise DonneeInvalideError(
            "Aucune donnée valide disponible pour le modèle."
        )

    tableau = pd.DataFrame(donnees)

    # Harmoniser les noms de colonnes
    tableau = tableau.rename(columns={
        "latitude": "Latitude",
        "longitude": "Longitude",
        "nombre_bornes": "Nombre de borne",
        "arrondissement": "Arrondissement"
    })

    # Conserver seulement les consommations positives
    tableau = tableau[tableau[CIBLE] > 0].copy()

    if tableau.empty:
        raise DonneeInvalideError(
            "Aucune consommation positive disponible."
        )

    colonnes_finales = CARACTERISTIQUES.copy()

    # La borne sert au regroupement, pas à la prédiction
    if garder_borne:
        tableau["Borne"] = pd.to_numeric(
            tableau["Borne"],
            errors="coerce"
        )

        tableau = tableau.dropna(subset=["Borne"])

        colonnes_finales.append("Borne")

    colonnes_finales.append(CIBLE)

    return tableau[colonnes_finales].reset_index(drop=True)


def main() -> None:
    """Charge les données, entraîne les modèles et affiche les scores."""

    # Utiliser le nettoyage commun de donnees.py
    df = adapter_donnees_modele()

    print(f"{len(df)} lignes utilisées")

    scores_modeles = entrainer_et_sauvegarder(df, CIBLE)

    for nom, scores in scores_modeles.items():
        print(
            nom,
            {
                cle: round(valeur, 2)
                for cle, valeur in scores.items()
            }
        )


if __name__ == "__main__":
    main()
