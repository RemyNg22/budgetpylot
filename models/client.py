from compte import Compte
from credit import Credit
from epargne import Epargne
from typing import List

class Client:
    def __init__(self, nom: str, revenu_mensuel: float):
        self.nom = nom
        self.revenu_mensuel = float(revenu_mensuel)
        self.comptes: List[Compte] = []
        self.credits: List[Credit] = []
        self.epargnes: List[Epargne] = []

    def ajouter_compte(self, compte: Compte):
        self.comptes.append(compte)

    def ajouter_credit(self, credit: Credit, part: float = 1.0):
        credit.ajouter_emprunteur(self, part)
        self.credits.append(credit)

    def ajouter_epargne(self, epargne: Epargne):
        self.epargnes.append(epargne)

    def __repr__(self):
        return f"Client: {self.nom} - Revenu: {self.revenu_mensuel} €"