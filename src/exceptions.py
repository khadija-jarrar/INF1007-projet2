"""Exceptions personnalisées du projet."""


class DonneeInvalideError(Exception):
    """Levée quand les données (colonnes, tailles, valeurs) sont inutilisables."""


class ModeleNonEntraineError(Exception):
    """Levée quand on veut prédire ou sauvegarder avant d'avoir entraîné."""


class ModeleIntrouvableError(Exception):
    """Levée quand le fichier du modèle sauvegardé n'existe pas."""