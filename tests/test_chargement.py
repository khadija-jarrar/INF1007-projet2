import pytest

from src.entrainement import CIBLE, charger_donnees_modele
from src.exceptions import DonneeInvalideError, ModeleIntrouvableError
from src.modele import ecrire_metadonnees, lire_metadonnees

ENTETE = "Latitude,Longitude,Nombre de borne,Arrondissement,mois,KWH total"


def test_charger_donnees_nettoie_et_convertit(tmp_path):
    csv = tmp_path / "mini.csv"
    csv.write_text(
        ENTETE + "\n"
        '45.5,-73.6,2,CDN,août,"5691,61765"\n'
        "45.6,-73.5,4,LSO,mai,\n"          # consommation manquante : retirée
        '45.7,-73.4,2,STL,juin,"100,5"\n',
        encoding="utf-8",
    )
    df = charger_donnees_modele(str(csv))
    assert len(df) == 2
    assert df[CIBLE].tolist() == pytest.approx([5691.61765, 100.5])
    assert "KWH total" not in df.columns


def test_charger_donnees_garde_la_borne_sur_demande(tmp_path):
    csv = tmp_path / "mini.csv"
    csv.write_text(
        ENTETE + ",Borne\n" '45.5,-73.6,2,CDN,août,"10,5",7021\n',
        encoding="utf-8",
    )
    assert "Borne" in charger_donnees_modele(str(csv), garder_borne=True).columns
    assert "Borne" not in charger_donnees_modele(str(csv)).columns


def test_charger_donnees_colonnes_absentes(tmp_path):
    csv = tmp_path / "incomplet.csv"
    csv.write_text("Latitude\n45.5\n", encoding="utf-8")
    with pytest.raises(DonneeInvalideError):
        charger_donnees_modele(str(csv))


def test_metadonnees_ecriture_puis_lecture(tmp_path):
    chemin = str(tmp_path / "dossier" / "meta.json")
    meta = {"cible": "consommation_kwh", "colonnes": ["Latitude", "mois"]}
    ecrire_metadonnees(meta, chemin)
    assert lire_metadonnees(chemin) == meta


def test_lire_metadonnees_fichier_absent(tmp_path):
    with pytest.raises(ModeleIntrouvableError):
        lire_metadonnees(str(tmp_path / "absent.json"))
        