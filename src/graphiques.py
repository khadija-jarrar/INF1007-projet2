"""Graphiques d'évaluation du modèle (réutilisables dans l'interface)."""
import os

import numpy as np
from matplotlib.figure import Figure


def figure_predit_vs_reel(y_vrai: np.ndarray, y_pred: np.ndarray) -> Figure:
    """Construit le graphique « prédit contre réel ».

    Reçoit les consommations réelles et prédites (kWh, même taille).
    Renvoie une figure Matplotlib (ne l'affiche pas, ne l'enregistre pas).
    """
    y_vrai = np.asarray(y_vrai, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    fig = Figure(figsize=(6, 5))
    ax = fig.subplots()
    ax.scatter(y_vrai, y_pred, alpha=0.35, s=12, label="Bornes (ensemble de test)")
    limites = [min(y_vrai.min(), y_pred.min()), max(y_vrai.max(), y_pred.max())]
    ax.plot(limites, limites, "r--", label="Prédiction parfaite")
    ax.set_xlabel("Consommation réelle (kWh)")
    ax.set_ylabel("Consommation prédite (kWh)")
    ax.set_title("Prédit contre réel – consommation mensuelle des bornes")
    ax.legend()
    fig.tight_layout()
    return fig


def enregistrer_figure(fig: Figure, chemin: str) -> None:
    """Enregistre la figure en PNG et crée le dossier si besoin."""
    os.makedirs(os.path.dirname(chemin) or ".", exist_ok=True)
    fig.savefig(chemin, dpi=150)