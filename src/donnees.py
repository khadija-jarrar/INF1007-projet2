
import os

chemin = os.path.join("donnees", "chargeurs_statistiques_2025.csv")

with open(chemin, "r", encoding="utf-8-sig") as fichier:
    premiere_ligne = fichier.readline()
    lignes = fichier.readlines()

    print("Nombre de lignes :", len(lignes))
    print("Colonnes :", premiere_ligne)
    colonnes = premiere_ligne.strip().split(",")

    print("Nombre de colonnes :", len(colonnes))



