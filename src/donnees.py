
import csv
import os

chemin = os.path.join("donnees", "chargeurs_statistiques_2025.csv")

colonnes = {
    "borne": 0,
    "latitude": 1,
    "longitude": 2,
    "nombre_bornes": 3,
    "arrondissement": 4,
    "mois": 8,
    "nombre_recharges": 9,
    "consommation_kwh": 11
}

with open(chemin, "r", encoding="utf-8-sig", newline="") as fichier:
    donnees_valides = []
    valeurs_manquantes=0
    lignes_ignorees = 0
    total = 0


    lecteur = csv.reader(fichier)

    next(lecteur)

    for ligne in list(lecteur):
        consommation = ligne[colonnes["consommation_kwh"]]
        consommation = consommation.strip().strip('"')

        if consommation != "":
            consommation = float(consommation.replace(",", "."))
            #print(consommation)

            mois = ligne[colonnes["mois"]]
            #récupérer les données valides
            donnees_valides.append({
                        "latitude": ligne[colonnes["latitude"]],
                        "longitude": ligne[colonnes["longitude"]],
                        "nombre_bornes": ligne[colonnes["nombre_bornes"]],
                        "arrondissement": ligne[colonnes["arrondissement"]],
                        "mois": ligne[colonnes["mois"]],
                        "consommation_kwh": consommation
                         })
            #print(ligne[colonnes["latitude"]]) # affiche 45.5095482 flaot
            #print(ligne[colonnes["longitude"]]) # affiche -73.6296806 float
            #print(ligne[colonnes["nombre_bornes"]]) # affiche 2 int
            #break
            
            latitude = ligne[colonnes["latitude"]].strip()
            longitude = ligne[colonnes["longitude"]].strip()
            nombre_bornes = ligne[colonnes["nombre_bornes"]].strip()

            if latitude == "" or longitude == "" or nombre_bornes == "":
                lignes_ignorees += 1
                

                latitude = float(latitude)
                longitude = float(longitude)
                nombre_bornes = int(nombre_bornes)
            else:
                valeurs_manquantes += 1
    print("Lignes ignorées :", lignes_ignorees)
    print("Lignes valides :", len(donnees_valides))

        #if consommation == "":
           # valeurs_manquantes += 1
    #print("Nombre de consommations manquantes :", valeurs_manquantes)
    for donnee in donnees_valides:
        total += donnee["consommation_kwh"]

        moyenne = total / len(donnees_valides) # consommation moyenne

    minimum = min(d["consommation_kwh"] for d in donnees_valides)
    maximum = max(d["consommation_kwh"] for d in donnees_valides)

    print("Consommation minimale :", minimum, "kWh") 
    print("Consommation maximale :", maximum, "kWh")

    print("Consommation moyenne :", moyenne, "kWh")