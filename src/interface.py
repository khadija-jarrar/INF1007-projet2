
"""Interface graphique de prédiction de la consommation électrique."""

import csv
import json
import math
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

from src.modele import Modele
from src.prediction import PredictionRecharge


# ==========================================
# 1. CHEMINS DES FICHIERS
# ==========================================

DOSSIER_PROJET = Path(__file__).resolve().parent.parent

CHEMIN_MODELE = DOSSIER_PROJET / "modeles" / "modele.joblib"
CHEMIN_META = DOSSIER_PROJET / "modeles" / "metadonnees.json"
CHEMIN_HISTORIQUE = DOSSIER_PROJET / "historique.csv"


# ==========================================
# 2. CHARGEMENT DES MÉTADONNÉES
# ==========================================

def charger_metadonnees() -> dict:
    """Charge les informations nécessaires à la saisie."""

    with open(CHEMIN_META, "r", encoding="utf-8") as fichier:
        return json.load(fichier)


# ==========================================
# 3. VALIDATION DES SAISIES
# ==========================================

def recuperer_donnees() -> dict:
    """Récupère et valide les cinq caractéristiques."""

    if not entree_latitude.get().strip():
        raise ValueError("Veuillez entrer une latitude.")

    if not entree_longitude.get().strip():
        raise ValueError("Veuillez entrer une longitude.")

    if not entree_bornes.get().strip():
        raise ValueError("Veuillez entrer le nombre de bornes.")

    try:
        latitude = float(
            entree_latitude.get().strip().replace(",", ".")
        )

        longitude = float(
            entree_longitude.get().strip().replace(",", ".")
        )

        nombre_bornes = int(
            entree_bornes.get().strip()
        )

    except ValueError as erreur:
        raise ValueError(
            "Latitude et longitude doivent être des nombres, "
            "et le nombre de bornes doit être un entier."
        ) from erreur

    valeurs = {
        "Latitude": latitude,
        "Longitude": longitude,
        "Nombre de borne": nombre_bornes
    }

    for nom, valeur in valeurs.items():
        limites = metadonnees["numeriques"][nom]

        if not math.isfinite(valeur):
            raise ValueError(
                f"{nom} doit être un nombre fini."
            )

        if not limites["min"] <= valeur <= limites["max"]:
            raise ValueError(
                f"{nom} doit être entre "
                f"{limites['min']} et {limites['max']}."
            )

    arrondissement = entree_arrondissement.get()
    mois = entree_mois.get()

    if arrondissement not in metadonnees["categorielles"]["Arrondissement"]:
        raise ValueError(
            "Veuillez choisir un arrondissement valide."
        )

    if mois not in metadonnees["categorielles"]["mois"]:
        raise ValueError(
            "Veuillez choisir un mois valide."
        )

    return {
        "Latitude": latitude,
        "Longitude": longitude,
        "Nombre de borne": nombre_bornes,
        "Arrondissement": arrondissement,
        "mois": mois
    }


# ==========================================
# 4. ENREGISTREMENT DE L'HISTORIQUE
# ==========================================

def sauvegarder_historique(
    donnees: dict,
    prediction: float
) -> None:
    """Enregistre une prédiction dans un fichier CSV."""

    colonnes = [
        "date",
        "Latitude",
        "Longitude",
        "Nombre de borne",
        "Arrondissement",
        "mois",
        "prediction_kwh"
    ]

    nouveau_fichier = (
        not CHEMIN_HISTORIQUE.exists()
        or CHEMIN_HISTORIQUE.stat().st_size == 0
    )

    with open(
        CHEMIN_HISTORIQUE,
        "a",
        newline="",
        encoding="utf-8"
    ) as fichier:

        writer = csv.DictWriter(
            fichier,
            fieldnames=colonnes
        )

        if nouveau_fichier:
            writer.writeheader()

        writer.writerow({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **donnees,
            "prediction_kwh": round(prediction, 2)
        })


# ==========================================
# 5. PRÉDICTION
# ==========================================

def predire_consommation() -> None:
    """Valide les saisies et affiche la consommation estimée."""

    try:
        # Récupérer les caractéristiques
        donnees = recuperer_donnees()

        # Préparer les données pour le modèle
        tableau = pd.DataFrame(
            [donnees],
            columns=metadonnees["colonnes"]
        )

        # Charger le modèle entraîné
        modele = Modele.charger(str(CHEMIN_MODELE))

        # Calculer la consommation estimée
        prediction = float(
            modele.predire(tableau)[0]
        )

        if not math.isfinite(prediction):
            raise ValueError(
                "La prédiction n'est pas un nombre valide."
            )

        # Éviter une consommation négative
        prediction = max(0.0, prediction)

        # Créer l'objet de prédiction (POO)
        resultat = PredictionRecharge(
            prediction,
            donnees["Arrondissement"]
        )

        # Afficher le résultat grâce à __str__()
        texte_resultat.config(
            text=str(resultat),
            fg="green"
        )

        # Sauvegarder l'historique
        sauvegarder_historique(
            donnees,
            prediction
        )

    except ValueError as erreur:
        texte_resultat.config(
            text="Aucune prédiction valide",
            fg="red"
        )
        messagebox.showerror(
            "Données invalides",
            str(erreur)
        )

    except Exception as erreur:
        texte_resultat.config(
            text="Erreur de prédiction",
            fg="red"
        )
        messagebox.showerror(
            "Erreur de prédiction",
            f"Impossible de calculer la prédiction :\n{erreur}"
        )


# ==========================================
# 6. GRAPHIQUE DE L'HISTORIQUE
# ==========================================

def afficher_graphique() -> None:
    """Affiche les consommations prédites enregistrées."""

    if not CHEMIN_HISTORIQUE.exists():
        messagebox.showinfo(
            "Historique vide",
            "Effectuez d'abord une prédiction."
        )
        return

    try:
        historique = pd.read_csv(
            CHEMIN_HISTORIQUE
        )

        valeurs = historique["prediction_kwh"]

        if valeurs.empty:
            messagebox.showinfo(
                "Historique vide",
                "Aucune prédiction disponible."
            )
            return

        fig, ax = plt.subplots(figsize=(8, 4))

        ax.plot(
            range(1, len(valeurs) + 1),
            valeurs,
            marker="o"
        )

        ax.set_title(
            "Historique des prédictions"
        )
        ax.set_xlabel(
            "Numéro de la prédiction"
        )
        ax.set_ylabel(
            "Consommation estimée (kWh)"
        )
        ax.grid(True)

        fig.tight_layout()
        plt.show()

    except Exception as erreur:
        messagebox.showerror(
            "Erreur graphique",
            str(erreur)
        )


# ==========================================
# 7. CONSULTATION DE L'HISTORIQUE
# ==========================================

def afficher_historique() -> None:
    """Affiche les prédictions enregistrées dans une fenêtre."""

    if not CHEMIN_HISTORIQUE.exists():
        messagebox.showinfo(
            "Historique vide",
            "Aucune prédiction enregistrée."
        )
        return

    try:
        with open(
            CHEMIN_HISTORIQUE,
            "r",
            newline="",
            encoding="utf-8"
        ) as fichier:
            lignes = list(
                csv.DictReader(fichier)
            )

        if not lignes:
            messagebox.showinfo(
                "Historique vide",
                "Aucune prédiction enregistrée."
            )
            return

        nouvelle_fenetre = tk.Toplevel(fenetre)
        nouvelle_fenetre.title(
            "Historique des prédictions"
        )
        nouvelle_fenetre.geometry("700x400")

        cadre = tk.Frame(nouvelle_fenetre)
        cadre.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        defilement = tk.Scrollbar(cadre)
        defilement.pack(
            side="right",
            fill="y"
        )

        zone_texte = tk.Text(
            cadre,
            wrap="word",
            yscrollcommand=defilement.set
        )
        zone_texte.pack(
            side="left",
            fill="both",
            expand=True
        )

        defilement.config(
            command=zone_texte.yview
        )

        for ligne in lignes:
            zone_texte.insert(
                "end",
                f"Date : {ligne['date']}\n"
                f"Latitude : {ligne['Latitude']}\n"
                f"Longitude : {ligne['Longitude']}\n"
                f"Nombre de bornes : {ligne['Nombre de borne']}\n"
                f"Arrondissement : {ligne['Arrondissement']}\n"
                f"Mois : {ligne['mois']}\n"
                f"Prédiction : {ligne['prediction_kwh']} kWh\n"
                "----------------------------------\n"
            )

        zone_texte.config(
            state="disabled"
        )

    except Exception as erreur:
        messagebox.showerror(
            "Erreur historique",
            str(erreur)
        )


# ==========================================
# 8. CRÉATION DE L'INTERFACE
# ==========================================

def main() -> None:
    """Construit et lance l'interface graphique."""

    global fenetre
    global metadonnees
    global entree_latitude
    global entree_longitude
    global entree_bornes
    global entree_arrondissement
    global entree_mois
    global texte_resultat

    fenetre = tk.Tk()
    fenetre.title(
        "Prédiction de la consommation électrique"
    )
    fenetre.geometry("800x780")

    try:
        metadonnees = charger_metadonnees()

    except Exception as erreur:
        messagebox.showerror(
            "Erreur de chargement",
            f"Impossible de charger les métadonnées :\n{erreur}"
        )
        fenetre.destroy()
        return

    # Titre principal
    titre = tk.Label(
        fenetre,
        text="Prédiction de la consommation électrique",
        font=("Arial", 18, "bold")
    )
    titre.pack(pady=15)

    # --------------------------------------
    # Latitude
    # --------------------------------------

    tk.Label(
        fenetre,
        text="Latitude :"
    ).pack(pady=3)

    entree_latitude = tk.Entry(fenetre)
    entree_latitude.pack(pady=3)

    limites_latitude = metadonnees["numeriques"]["Latitude"]

    tk.Label(
        fenetre,
        text=(
            f"Entre {limites_latitude['min']} "
            f"et {limites_latitude['max']}"
        ),
        fg="gray",
        font=("Arial", 9)
    ).pack()

    # --------------------------------------
    # Longitude
    # --------------------------------------

    tk.Label(
        fenetre,
        text="Longitude :"
    ).pack(pady=3)

    entree_longitude = tk.Entry(fenetre)
    entree_longitude.pack(pady=3)

    limites_longitude = metadonnees["numeriques"]["Longitude"]

    tk.Label(
        fenetre,
        text=(
            f"Entre {limites_longitude['min']} "
            f"et {limites_longitude['max']}"
        ),
        fg="gray",
        font=("Arial", 9)
    ).pack()

    # --------------------------------------
    # Nombre de bornes
    # --------------------------------------

    tk.Label(
        fenetre,
        text="Nombre de bornes :"
    ).pack(pady=3)

    entree_bornes = tk.Entry(fenetre)
    entree_bornes.pack(pady=3)

    limites_bornes = metadonnees["numeriques"]["Nombre de borne"]

    tk.Label(
        fenetre,
        text=(
            f"Nombre entier entre "
            f"{int(limites_bornes['min'])} "
            f"et {int(limites_bornes['max'])}"
        ),
        fg="gray",
        font=("Arial", 9)
    ).pack()

    # --------------------------------------
    # Arrondissement
    # --------------------------------------

    tk.Label(
        fenetre,
        text="Arrondissement :"
    ).pack(pady=3)

    entree_arrondissement = ttk.Combobox(
        fenetre,
        values=metadonnees["categorielles"]["Arrondissement"],
        state="readonly",
        width=25
    )
    entree_arrondissement.pack(pady=3)

    # --------------------------------------
    # Mois
    # --------------------------------------

    tk.Label(
        fenetre,
        text="Mois :"
    ).pack(pady=3)

    entree_mois = ttk.Combobox(
        fenetre,
        values=metadonnees["categorielles"]["mois"],
        state="readonly",
        width=25
    )
    entree_mois.pack(pady=3)

    # --------------------------------------
    # Bouton de prédiction
    # --------------------------------------

    bouton_predire = tk.Button(
        fenetre,
        text="Prédire la consommation",
        command=predire_consommation,
        font=("Arial", 11, "bold")
    )
    bouton_predire.pack(pady=15)

    # Résultat
    texte_resultat = tk.Label(
        fenetre,
        text="Aucune prédiction effectuée",
        font=("Arial", 14, "bold")
    )
    texte_resultat.pack(pady=10)

    # --------------------------------------
    # Bouton graphique
    # --------------------------------------

    bouton_graphique = tk.Button(
        fenetre,
        text="Afficher le graphique",
        command=afficher_graphique
    )
    bouton_graphique.pack(pady=5)

    # --------------------------------------
    # Bouton historique
    # --------------------------------------

    bouton_historique = tk.Button(
        fenetre,
        text="Afficher l'historique",
        command=afficher_historique
    )
    bouton_historique.pack(pady=5)

    fenetre.mainloop()


if __name__ == "__main__":
    main()
