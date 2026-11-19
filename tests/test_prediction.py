
"""Tests des classes de prédiction."""

import pytest

from src.prediction import Prediction, PredictionRecharge


def test_prediction_simple():
    """Vérifie l'affichage d'une prédiction simple."""
    prediction = Prediction(1500.0)

    assert prediction.afficher() == "Prédiction : 1500.00"


def test_heritage():
    """Vérifie que PredictionRecharge hérite de Prediction."""
    prediction = PredictionRecharge(1500.0, "CDN")

    assert isinstance(prediction, Prediction)


def test_polymorphisme():
    """Vérifie que les deux classes redéfinissent l'affichage."""
    predictions = [
        Prediction(1500.0),
        PredictionRecharge(1500.0, "CDN")
    ]

    resultats = [prediction.afficher() for prediction in predictions]

    assert resultats == [
        "Prédiction : 1500.00",
        "Consommation estimée : 1500.00 kWh (CDN)"
    ]


def test_methode_speciale():
    """Vérifie la méthode spéciale __str__."""
    prediction = PredictionRecharge(5691.62, "CDN")

    assert str(prediction) == (
        "Consommation estimée : 5691.62 kWh (CDN)"
    )
