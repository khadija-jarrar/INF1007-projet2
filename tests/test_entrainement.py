import pandas as pd
import pytest

from src.entrainement import convertir_nombre, charger_donnees_modele
from src.exceptions import DonneeInvalideError


def test_convertir_nombre_virgule_et_guillemets():
    s = pd.Series(['"5691,61765"', '"10190,6552"'])
    assert convertir_nombre(s).tolist() == pytest.approx([5691.61765, 10190.6552])


def test_convertir_nombre_valeur_invalide():
    assert pd.isna(convertir_nombre(pd.Series(["abc"])).iloc[0])


def test_charger_fichier_absent(tmp_path):
    with pytest.raises(DonneeInvalideError):
        charger_donnees_modele(str(tmp_path / "absent.csv"))