
"""Tests du chargement et de l'adaptation des données pour le modèle."""

import csv

import pandas as pd
import pytest

from src.entrainement import (
    adapter_donnees_modele,
    charger_donnees_modele,
    convertir_nombre,
)
from src.exceptions import DonneeInvalideError


def test_convertir_nombre_virgule_et_guillemets():
    serie = pd.Series(['"5691,61765"', '"10190,6552"'])

    resultat = convertir_nombre(serie)

    assert resultat.tolist() == pytest.approx([
        5691.61765,
        10190.6552
    ])


def test_convertir_nombre_valeur_invalide():
    serie = pd.Series(["abc"])

    resultat = convertir_nombre(serie)

    assert pd.isna(resultat.iloc[0])


def test_charger_fichier_absent(tmp_path):
    chemin = tmp_path / "absent.csv"

    with pytest.raises(DonneeInvalideError):
        charger_donnees_modele(str(chemin))


def creer_csv_test(chemin):
    """Crée un CSV minimal compatible avec donnees.py."""

    with open(
        chemin,
        "w",
        encoding="utf-8",
        newline=""
    ) as fichier:

        writer = csv.writer(fichier)

        writer.writerow(
            [f"colonne{i}" for i in range(12)]
        )

        ligne = [""] * 12

        ligne[0] = "7021"
        ligne[1] = "45.5"
        ligne[2] = "-73.5"
        ligne[3] = "2"
        ligne[4] = "CDN"
        ligne[8] = "août"
        ligne[11] = "100"

        writer.writerow(ligne)


def test_adapter_donnees_modele(tmp_path):
    """Vérifie les colonnes et valeurs produites par l'adaptateur."""

    chemin = tmp_path / "exemple.csv"
    creer_csv_test(chemin)

    resultat = adapter_donnees_modele(
        str(chemin),
        garder_borne=True
    )

    assert len(resultat) == 1

    assert resultat.iloc[0]["Borne"] == 7021
    assert resultat.iloc[0]["consommation_kwh"] == 100

    assert "Latitude" in resultat.columns
    assert "Longitude" in resultat.columns
    assert "Nombre de borne" in resultat.columns

    assert resultat.iloc[0]["Latitude"] == pytest.approx(45.5)
    assert resultat.iloc[0]["Longitude"] == pytest.approx(-73.5)


def test_adapter_sans_identifiant_borne(tmp_path):
    """Vérifie que la borne peut être exclue du tableau."""

    chemin = tmp_path / "exemple.csv"
    creer_csv_test(chemin)

    resultat = adapter_donnees_modele(
        str(chemin),
        garder_borne=False
    )

    assert len(resultat) == 1
    assert "Borne" not in resultat.columns

    assert resultat.columns.tolist() == [
        "Latitude",
        "Longitude",
        "Nombre de borne",
        "Arrondissement",
        "mois",
        "consommation_kwh"
    ]
