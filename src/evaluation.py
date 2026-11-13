"""Évalue le modèle sauvegardé sur l'ensemble de test et trace le graphique."""
import os

from src.entrainement import CIBLE, charger_donnees_modele
from src.graphiques import enregistrer_figure, figure_predit_vs_reel
from src.modele import Modele, separer_donnees

CHEMIN_GRAPHIQUE = os.path.join("graphiques", "predit_vs_reel.png")


def main() -> None:
    """Recharge le modèle, prédit sur l'ensemble de test et enregistre le graphique."""
    df = charger_donnees_modele()
    _, X_test, _, y_test = separer_donnees(df, CIBLE)
    modele = Modele.charger()
    scores = modele.evaluer(X_test, y_test)
    print({k: round(v, 2) for k, v in scores.items()})
    pred = modele.predire(X_test)
    enregistrer_figure(figure_predit_vs_reel(y_test.to_numpy(), pred), CHEMIN_GRAPHIQUE)
    print(f"Graphique enregistré : {CHEMIN_GRAPHIQUE}")


if __name__ == "__main__":
    main()