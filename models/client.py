from compte import Compte
from credit import Credit
from epargne import Epargne
from depense import Depense
from revenu import Revenu
from typing import List
from datetime import datetime, timedelta


class Client:
    def __init__(self, nom: str):
        self.nom = nom
        self.revenus: List[Revenu] = []
        self.depenses: List[Depense] = []
        self.credits: List[Credit] = []
        self.epargnes: List[Epargne] = []
        self.comptes: List[Compte] = []


    def ajouter_revenu(self, revenu: Revenu):
        self.revenus.append(revenu)

    def ajouter_depense(self, depense: Depense):
        self.depenses.append(depense)

    def ajouter_credit(self, credit: Credit, part: float = 1.0):
        credit.ajouter_emprunteur(self, part)
        self.credits.append(credit)

    def ajouter_epargne(self, epargne: Epargne):
        self.epargnes.append(epargne)

    def ajouter_compte(self, compte: Compte):
        self.comptes.append(compte)


    # Revenus et dépenses
    def revenus_du_mois(self, mois: int):
        """Calcule le total des revenus pour un mois donné"""
        total = 0
        for rev in self.revenus:
            total += rev.montant_pour_mois(mois)
        return total

    def total_depenses_du_mois(self, mois: int, type_depense: str | None = None):
        """Calcule le total des dépenses pour un mois donné"""
        total = 0
        for dep in self.depenses:
            if dep.jour is None:
                continue
            if type_depense is None or dep.type_depense == type_depense:
                total += dep.montant
        return total


    # Simulation des flux
    def appliquer_flux_sur_compte(self, compte: Compte, date_du_jour: datetime, date_cible: datetime):
        """
        Simule tous les mouvements de date_du_jour jusqu'à date_cible
        et applique les flux sur le compte.
        """
        mois_actuel = date_du_jour.month
        annee_actuelle = date_du_jour.year

        while True:
            if datetime(annee_actuelle, mois_actuel, 1) > date_cible:
                break

            for rev in self.revenus:
                montant = rev.montant_pour_mois(mois_actuel)
                if montant > 0:
                    jour = rev.jour or 1

                    jour_mouvement = min(jour, 28)
                    date_mvt = datetime(annee_actuelle, mois_actuel, jour_mouvement)
                    if date_mvt >= date_du_jour and date_mvt <= date_cible:
                        compte.appliquer_mouvement(montant, "credit", "revenu", date_mvt)


            for dep in self.depenses:
                montant = dep.montant
                jour = dep.jour or 1
                jour_mouvement = min(jour, 28)
                date_mvt = datetime(annee_actuelle, mois_actuel, jour_mouvement)
                if date_mvt >= date_du_jour and date_mvt <= date_cible:
                    compte.appliquer_mouvement(montant, "debit", "depense", date_mvt)


            for cred in self.credits:
                montant = cred.mensualite_client(self)
                date_mvt = datetime(annee_actuelle, mois_actuel, 1)
                if date_mvt >= date_du_jour and date_mvt <= date_cible:
                    compte.appliquer_mouvement(montant, "debit", "credit", date_mvt)


            if mois_actuel == 12:
                mois_actuel = 1
                annee_actuelle += 1
            else:
                mois_actuel += 1


    # Affichage
    def __repr__(self):
        return (f"Client: {self.nom} - Revenus: {len(self.revenus)} - "
                f"Dépenses: {len(self.depenses)} - Crédits: {len(self.credits)} - "
                f"Comptes: {len(self.comptes)}")