"""Compare la séparation aléatoire et la séparation par borne."""
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupShuffleSplit, train_test_split

from src.entrainement import CIBLE, charger_donnees_modele
from src.modele import SEED, Modele, colonnes_categorielles


def evaluer(X_train, X_test, y_train, y_test) -> dict:
    """Entraîne la référence et la forêt, renvoie leurs scores sur le test."""
    cats = colonnes_categorielles(X_train)
    candidats = {
        "reference_moyenne": DummyRegressor(strategy="mean"),
        "foret_aleatoire": RandomForestRegressor(
            n_estimators=100, min_samples_leaf=3, random_state=SEED
        ),
    }
    resultats = {}
    for nom, estimateur in candidats.items():
        m = Modele(estimateur, cats, nom)
        m.entrainer(X_train, y_train)
        resultats[nom] = {k: round(v, 2) for k, v in m.evaluer(X_test, y_test).items()}
    return resultats


def main() -> None:
    """Affiche les scores pour les deux types de séparation."""
    df = charger_donnees_modele(garder_borne=True)
    groupes = df["Borne"]
    X = df.drop(columns=[CIBLE, "Borne"])
    y = df[CIBLE]

    print("--- Séparation aléatoire ---")
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=SEED)
    for nom, s in evaluer(X_tr, X_te, y_tr, y_te).items():
        print(nom, s)

    print("--- Séparation par borne (bornes jamais vues en test) ---")
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
    idx_train, idx_test = next(gss.split(X, y, groups=groupes))
    for nom, s in evaluer(
        X.iloc[idx_train], X.iloc[idx_test], y.iloc[idx_train], y.iloc[idx_test]
    ).items():
        print(nom, s)


if __name__ == "__main__":
    main()