"""Tests des fonctions de lecture et d'analyse de donnees.py."""
import csv
import os
import pytest
from src.donnees import (
    DonneeInvalideError,
    calculer_extremes,
    calculer_moyenne,
    calculer_moyenne_numpy,
    charger_donnees,
    convertir_nombre,
    creer_graphique,
    moyennes_par_mois,
)


def exemple_csv(chemin, lignes):
    """Construit un petit CSV conforme pour les tests, sans données externes."""
    with open(chemin, "w", encoding="utf-8", newline="") as fichier:
        lecteur = csv.writer(fichier)
        lecteur.writerow(["col" + str(i) for i in range(12)])
        for mois, consommation, latitude in lignes:
            ligne = [""] * 12
            ligne[1] = latitude
            ligne[2] = "-73.5"
            ligne[3] = "2"
            ligne[4] = "CDN"
            ligne[8] = mois
            ligne[11] = consommation
            lecteur.writerow(ligne)


def test_conversion_virgule():
    assert convertir_nombre('"5691,61765"') == pytest.approx(5691.61765)


def test_conversion_invalide():
    with pytest.raises(DonneeInvalideError):
        convertir_nombre("pas un nombre")


def test_lecture_valide(tmp_path):
    chemin = tmp_path / "exemple.csv"
    exemple_csv(chemin, [("août", '"1234,5"', "45.5")])
    donnees = charger_donnees(str(chemin))
    assert len(donnees) == 1
    assert donnees[0]["consommation_kwh"] == pytest.approx(1234.5)
    assert isinstance(donnees[0]["nombre_bornes"], int)
    assert isinstance(donnees[0]["latitude"], float)


def test_cible_manquante_ignoree(tmp_path):
    chemin = tmp_path / "exemple.csv"
    exemple_csv(chemin, [("août", "", "45.5")])
    assert charger_donnees(str(chemin)) == []


def test_latitude_invalide_ignoree(tmp_path):
    chemin = tmp_path / "exemple.csv"
    exemple_csv(chemin, [("août", "100", "45.5, -73.5")])
    assert charger_donnees(str(chemin)) == []


def test_fichier_absent(tmp_path):
    with pytest.raises(FileNotFoundError):
        charger_donnees(str(tmp_path / "introuvable.csv"))


def test_moyenne():
    donnees = [{"consommation_kwh": 10}, {"consommation_kwh": 20}]
    assert calculer_moyenne(donnees) == pytest.approx(15)
    assert calculer_moyenne_numpy(donnees) == pytest.approx(calculer_moyenne(donnees))


def test_moyenne_liste_vide():
    with pytest.raises(DonneeInvalideError):
        calculer_moyenne([])


def test_extremes():
    donnees = [{"consommation_kwh": 7.5}, {"consommation_kwh": 20.2}]
    assert calculer_extremes(donnees) == pytest.approx((7.5, 20.2))


def test_extremes_liste_vide():
    with pytest.raises(DonneeInvalideError):
        calculer_extremes([])


def test_moyennes_par_mois():
    donnees = [
        {"mois": "janvier", "consommation_kwh": 10},
        {"mois": "janvier", "consommation_kwh": 30},
        {"mois": "février", "consommation_kwh": 8},
    ]
    assert moyennes_par_mois(donnees) == pytest.approx({"janvier": 20, "février": 8})


def test_graphique_enregistre(tmp_path):
    chemin = tmp_path / "graphiques" / "test.png"
    creer_graphique([{"mois": "janvier", "consommation_kwh": 100}], str(chemin))
    assert chemin.is_file()
    assert os.path.getsize(chemin) > 0
