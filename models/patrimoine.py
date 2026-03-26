from models.credit import Credit
from models.revenu import Revenu

class Patrimoine:

    TYPE_PATRIMOINE = (
        "Résidence principale",
        "Résidence secondaire",
        "Immobilier locatif",
        "Terrain",
        "Parking/Garage",
        "Parts de SCI",
        "Biens d'usage (bijoux, voiture, œuvres d'art)",
        "Autre"
    )

    def __init__(self, type_patrimoine: str, nom: str, valeur: float, part: float = 100, 
                 credits: list | None = None, revenu=None):

        if type_patrimoine not in self.TYPE_PATRIMOINE:
            raise ValueError("Type de patrimoine invalide")

        if valeur < 0:
            raise ValueError("La valeur doit être positive")

        if not (0 < part <= 100):
            raise ValueError("La part doit être comprise entre 0 et 100")

        self.type_patrimoine = type_patrimoine
        self.nom = nom
        self.valeur = float(valeur)
        self.part = float(part)
        self.revenu = revenu
        self.credits: list = credits if credits is not None else []

    @property
    def valeur_detention(self) -> float:
        """Valeur réellement détenue par le client"""
        return self.valeur * (self.part / 100)

    def modifier_valeur(self, nouvelle_valeur: float):
        if nouvelle_valeur < 0:
            raise ValueError("La valeur doit être positive")
        self.valeur = float(nouvelle_valeur)

    def ajouter_credit(self, credit):
        if credit not in self.credits:
            self.credits.append(credit)
 
    def retirer_credit(self, credit):
        self.credits = [cr for cr in self.credits if cr is not credit]

    def ajouter_revenu(self, revenu: Revenu):
        self.revenu = revenu

    @property
    def credit(self):
        """Retourne le premier crédit associé, ou None. Pour compatibilité."""
        return self.credits[0] if self.credits else None
 
    def __repr__(self):
        noms_credits = ", ".join(cr.nom for cr in self.credits) or "Aucun crédit"
        revenu_nom = self.revenu.type_de_revenu if self.revenu else "Aucun revenu"
        return (
            f"{self.type_patrimoine} - {self.nom} : "
            f"{self.valeur} EUR ({self.part}% détenu) | "
            f"Crédits : {noms_credits} | Revenu : {revenu_nom}")