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
                 credits: list | None = None, revenus=None, revenu=None):
        """
        Représente un bien patrimonial d'un client.

        Attributes:
            type_patrimoine (str): type du bien (ex: Résidence principale, Terrain, Parking/Garage, etc.).
            nom (str): nom ou description du bien.
            valeur (float): valeur totale du bien en euros.
            part (float): pourcentage détenu (0-100).
            credits (list[Credit]): crédits associés au bien.
            revenus (list[Revenu]): revenus générés par le bien (ex: loyers).
        """
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
        self.credits: list = credits if credits is not None else []
        if revenu and not revenus:
            revenus = [revenu]

        self.revenus = revenus if revenus is not None else []
    @property
    def valeur_detention(self) -> float:
        """
        Calcule la valeur détenue du patrimoine selon la part.

        Returns:
            float: valeur réelle détenue du bien.
        """
        return self.valeur * (self.part / 100)
 
    def modifier_valeur(self, nouvelle_valeur: float):
        """
        Modifie la valeur totale du bien.

        Args:
            nouvelle_valeur (float): nouvelle valeur du bien, doit être positive.
        """
        if nouvelle_valeur < 0:
            raise ValueError("La valeur doit être positive")
        self.valeur = float(nouvelle_valeur)
 
    def ajouter_credit(self, credit):
        if credit not in self.credits:
            self.credits.append(credit)
 
    def retirer_credit(self, credit):
        self.credits = [cr for cr in self.credits if cr is not credit]
 
    def ajouter_revenu(self, revenu):
        if revenu not in self.revenus:
            self.revenus.append(revenu)
 
    def retirer_revenu(self, revenu):
        self.revenus = [r for r in self.revenus if r is not revenu]
 
    @property
    def revenu(self):
        """
        Retourne le premier revenu associé au bien, s'il existe.

        Returns:
            Revenu | None: revenu lié au bien ou None si aucun.
        """
        return self.revenus[0] if self.revenus else None
 
    @property
    def credit(self):
        """
        Retourne le premier crédit associé au bien, s'il existe.

        Returns:
            Credit | None: crédit lié au bien ou None si aucun.
        """
        return self.credits[0] if self.credits else None
 
    def __repr__(self):
        noms_credits = ", ".join(cr.nom for cr in self.credits) or "Aucun crédit"
        noms_revenus = ", ".join(r.type_de_revenu for r in self.revenus) or "Aucun revenu"
        return (
            f"{self.type_patrimoine} - {self.nom} : "
            f"{self.valeur} EUR ({self.part}% détenu) | "
            f"Crédits : {noms_credits} | Revenus : {noms_revenus}"
        )