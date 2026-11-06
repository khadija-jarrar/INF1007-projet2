"""Lecture, nettoyage et exploration des bornes de recharge de Montréal (2025)."""

import csv
import os

import matplotlib
matplotlib.use("Agg")  # Permet de sauvegarder les graphiques sans écran.
import matplotlib.pyplot as plt
import numpy as np

# Indices des colonnes dans le fichier CSV
colonnes = {
    "borne": 0,
    "latitude": 1,
    "longitude": 2,
    "nombre_bornes": 3,
    "arrondissement": 4,
    "mois": 8,
    "nombre_recharges": 9,
    "consommation_kwh": 11,
}

MOIS = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"
]


class DonneeInvalideError(ValueError):
    """Signale qu'une donnée fournie ne permet pas d'effectuer le calcul."""


def convertir_nombre(texte: str) -> float:
    """Convertit un nombre CSV en float ; lève DonneeInvalideError si invalide."""
    valeur = texte.strip().strip('"').strip().replace(",", ".")
    try:
        nombre = float(valeur)
    except ValueError as erreur:
        raise DonneeInvalideError(f"Nombre invalide : {texte!r}") from erreur
    if not np.isfinite(nombre):
        raise DonneeInvalideError(f"Nombre non fini : {texte!r}")
    return nombre


def charger_donnees(chemin: str) -> list[dict]:
    """Lit un CSV et retourne les observations complètes ; lève FileNotFoundError si absent.

    Les lignes avec cible vide ou caractéristiques invalides sont ignorées.
    La liste contient latitude, longitude, nombre_bornes, arrondissement,
    mois et consommation_kwh, avec les variables numériques déjà converties.
    """
    if not os.path.isfile(chemin):
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    donnees_valides = []
    valeurs_manquantes = 0
    lignes_ignorees = 0

    with open(chemin, "r", encoding="utf-8-sig", newline="") as fichier:
        lecteur = csv.reader(fichier)
        next(lecteur, None)  # Ignorer les noms des colonnes

        for ligne in lecteur:
            if len(ligne) <= colonnes["consommation_kwh"]:
                lignes_ignorees += 1
                continue

            consommation = ligne[colonnes["consommation_kwh"]]
            consommation = consommation.strip().strip('"')

            if consommation == "":
                valeurs_manquantes += 1
                continue

            latitude = ligne[colonnes["latitude"]].strip()
            longitude = ligne[colonnes["longitude"]].strip()
            nombre_bornes = ligne[colonnes["nombre_bornes"]].strip()
            arrondissement = ligne[colonnes["arrondissement"]].strip()
            mois = ligne[colonnes["mois"]].strip().lower()

            if (latitude == "" or longitude == "" or nombre_bornes == ""
                    or arrondissement == "" or mois == ""):
                lignes_ignorees += 1
                continue

            try:
                consommation = convertir_nombre(consommation)
                latitude = convertir_nombre(latitude)
                longitude = convertir_nombre(longitude)
                nombre_bornes = int(nombre_bornes)
            except (DonneeInvalideError, ValueError):
                lignes_ignorees += 1
                continue

            # Vérifier les plages valides ; ne pas deviner une valeur incorrecte.
            if (not -90 <= latitude <= 90 or not -180 <= longitude <= 180
                    or nombre_bornes <= 0 or consommation < 0 or mois not in MOIS):
                lignes_ignorees += 1
                continue

            #récupérer les données valides
            donnees_valides.append({
                "latitude": latitude,
                "longitude": longitude,
                "nombre_bornes": nombre_bornes,
                "arrondissement": arrondissement,
                "mois": mois,
                "consommation_kwh": consommation,
            })

            #print(ligne[colonnes["latitude"]]) # affiche 45.5095482 flaot
            #print(ligne[colonnes["longitude"]]) # affiche -73.6296806 float
            #print(ligne[colonnes["nombre_bornes"]]) # affiche 2 int
            #break

    # Les compteurs restent disponibles pour vérifier le nettoyage à l'exécution.
    # On ne les retourne pas : cette fonction sert à produire les données propres.
    return donnees_valides


def calculer_moyenne(donnees: list[dict]) -> float:
    """Calcule la consommation moyenne en kWh ; lève une erreur si vide."""
    if len(donnees) == 0:
        raise DonneeInvalideError("Aucune donnée disponible")

    total = 0
    for donnee in donnees:
        total += donnee["consommation_kwh"]

    moyenne = total / len(donnees)  # consommation moyenne
    return moyenne


def calculer_extremes(donnees: list[dict]) -> tuple[float, float]:
    """Retourne le minimum et le maximum en kWh ; lève une erreur si vide."""
    if len(donnees) == 0:
        raise DonneeInvalideError("Aucune donnée disponible")

    minimum = min(d["consommation_kwh"] for d in donnees)
    maximum = max(d["consommation_kwh"] for d in donnees)
    return minimum, maximum


def calculer_moyenne_numpy(donnees: list[dict]) -> float:
    """Calcule la moyenne avec NumPy sans boucle Python pour le calcul."""
    if len(donnees) == 0:
        raise DonneeInvalideError("Aucune donnée disponible")
    valeurs = np.array([d["consommation_kwh"] for d in donnees], dtype=float)
    return float(np.mean(valeurs))


def moyennes_par_mois(donnees: list[dict]) -> dict[str, float]:
    """Retourne la consommation moyenne par mois, uniquement pour les mois présents."""
    sommes = {mois: 0.0 for mois in MOIS}
    nombres = {mois: 0 for mois in MOIS}

    for donnee in donnees:
        mois = donnee["mois"]
        if mois not in sommes:
            raise DonneeInvalideError(f"Mois inconnu : {mois}")
        sommes[mois] += donnee["consommation_kwh"]
        nombres[mois] += 1

    return {mois: sommes[mois] / nombres[mois]
            for mois in MOIS if nombres[mois] > 0}


def creer_graphique(donnees: list[dict], chemin_image: str) -> None:
    """Enregistre un graphique des moyennes mensuelles ; lève une erreur si aucune donnée."""
    moyennes = moyennes_par_mois(donnees)
    if not moyennes:
        raise DonneeInvalideError("Aucune donnée à représenter")

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(list(moyennes.keys()), list(moyennes.values()))
    ax.set_title("Consommation électrique moyenne par mois — Montréal, 2025")
    ax.set_xlabel("Mois")
    ax.set_ylabel("Consommation moyenne (kWh)")
    ax.tick_params(axis="x", rotation=40)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    os.makedirs(os.path.dirname(chemin_image) or ".", exist_ok=True)
    fig.savefig(chemin_image, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    dossier_projet = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chemin = os.path.join(dossier_projet, "donnees", "chargeurs_statistiques_2025.csv")
    chemin_graphique = os.path.join(dossier_projet, "graphiques", "consommation_par_mois.png")

    donnees_valides = charger_donnees(chemin)
    moyenne = calculer_moyenne(donnees_valides)
    minimum, maximum = calculer_extremes(donnees_valides)

    print("Lignes valides :", len(donnees_valides))
    print("Consommation minimale :", minimum, "kWh")
    print("Consommation maximale :", maximum, "kWh")
    print("Consommation moyenne :", moyenne, "kWh")
    print("Moyenne NumPy :", calculer_moyenne_numpy(donnees_valides), "kWh")
    creer_graphique(donnees_valides, chemin_graphique)
    print("Graphique enregistré :", chemin_graphique)
