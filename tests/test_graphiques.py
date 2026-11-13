import numpy as np
import pytest

from src.graphiques import enregistrer_figure, figure_predit_vs_reel


def test_figure_a_titre_et_axes():
    fig = figure_predit_vs_reel(np.array([1.0, 2.0, 3.0]), np.array([1.1, 1.9, 3.2]))
    ax = fig.axes[0]
    assert ax.get_title() != ""
    assert "réelle" in ax.get_xlabel()
    assert "prédite" in ax.get_ylabel()


def test_enregistrer_figure_cree_le_fichier(tmp_path):
    fig = figure_predit_vs_reel(np.array([1.0, 2.0]), np.array([1.0, 2.5]))
    chemin = tmp_path / "sous_dossier" / "g.png"
    enregistrer_figure(fig, str(chemin))
    assert chemin.exists()