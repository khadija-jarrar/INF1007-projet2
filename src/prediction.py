
"""Classes représentant les prédictions de consommation."""


class Prediction:
    """Représente une prédiction numérique."""

    def __init__(self, valeur: float):
        self.valeur = valeur

    def afficher(self) -> str:
        """Retourne la valeur prédite."""
        return f"Prédiction : {self.valeur:.2f}"

    def __str__(self) -> str:
        return self.afficher()


class PredictionRecharge(Prediction):
    """Représente une prédiction de consommation électrique."""

    def __init__(self, valeur: float, arrondissement: str):
        super().__init__(valeur)
        self.arrondissement = arrondissement

    def afficher(self) -> str:
        """Retourne la consommation et l'arrondissement."""
        return (
            f"Consommation estimée : {self.valeur:.2f} kWh "
            f"({self.arrondissement})"
        )
