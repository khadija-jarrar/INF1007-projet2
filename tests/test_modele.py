import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

from src.exceptions import (
    DonneeInvalideError, ModeleIntrouvableError, ModeleNonEntraineError,
)
from src.modele import (
    Modele, colonnes_categorielles, construire_metadonnees,
    rmse_numpy, separer_donnees,
)


@pytest.fixture
def df():
    rng = np.random.default_rng(0)
    n = 80
    puissance = rng.uniform(3, 50, n)
    return pd.DataFrame({
        "puissance_kw": puissance,
        "type_borne": rng.choice(["niveau2", "rapide"], n),
        "consommation_kwh": 2 * puissance + rng.normal(0, 1, n),
    })


def test_rmse_cas_usuel():
    assert rmse_numpy(np.array([1, 2, 3]), np.array([1, 2, 5])) == pytest.approx(np.sqrt(4 / 3))


def test_rmse_egal_sklearn():
    y, p = np.array([3.0, 5.0, 2.5, 7.0]), np.array([2.5, 5.0, 4.0, 8.0])
    assert rmse_numpy(y, p) == pytest.approx(np.sqrt(mean_squared_error(y, p)))


def test_rmse_prediction_parfaite():
    assert rmse_numpy(np.array([1.0, 2.0]), np.array([1.0, 2.0])) == pytest.approx(0.0)


def test_rmse_tailles_differentes():
    with pytest.raises(DonneeInvalideError):
        rmse_numpy(np.array([1, 2, 3]), np.array([1, 2]))


def test_separation_reproductible(df):
    a = separer_donnees(df, "consommation_kwh")
    b = separer_donnees(df, "consommation_kwh")
    pd.testing.assert_frame_equal(a[1], b[1])


def test_separation_cible_absente(df):
    with pytest.raises(DonneeInvalideError):
        separer_donnees(df, "colonne_inexistante")


def test_predire_avant_entrainer(df):
    with pytest.raises(ModeleNonEntraineError):
        Modele(LinearRegression(), ["type_borne"]).predire(df.drop(columns="consommation_kwh"))


def test_entrainer_et_predire(df):
    X, y = df.drop(columns="consommation_kwh"), df["consommation_kwh"]
    m = Modele(LinearRegression(), colonnes_categorielles(X))
    m.entrainer(X, y)
    assert len(m.predire(X)) == len(X)
    assert m.evaluer(X, y)["r2"] > 0.9


def test_sauvegarde_puis_chargement(df, tmp_path):
    X, y = df.drop(columns="consommation_kwh"), df["consommation_kwh"]
    m = Modele(LinearRegression(), colonnes_categorielles(X))
    m.entrainer(X, y)
    chemin = str(tmp_path / "m.joblib")
    m.sauvegarder(chemin)
    recharge = Modele.charger(chemin)
    assert recharge.predire(X) == pytest.approx(m.predire(X))


def test_charger_fichier_absent(tmp_path):
    with pytest.raises(ModeleIntrouvableError):
        Modele.charger(str(tmp_path / "absent.joblib"))


def test_metadonnees(df):
    X = df.drop(columns="consommation_kwh")
    meta = construire_metadonnees(X, "consommation_kwh", {"rmse": 1.0})
    assert meta["categorielles"]["type_borne"] == ["niveau2", "rapide"]
    assert meta["numeriques"]["puissance_kw"]["min"] == pytest.approx(X["puissance_kw"].min())