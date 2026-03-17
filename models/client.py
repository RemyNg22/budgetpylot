from models.compte import Compte
from models.credit import Credit
from models.epargne import Epargne
from models.depense import Depense
from models.revenu import Revenu
from models.patrimoine import Patrimoine
from typing import List
from datetime import datetime


class Client:

    def __init__(self, nom: str):
        self.nom = nom
        self.revenus: List[Revenu] = []
        self.depenses: List[Depense] = []
        self.credits: List[Credit] = []
        self.epargnes: List[Epargne] = []
        self.comptes: List[Compte] = []
        self.patrimoines: List[Patrimoine] = []



    # Ajout des éléments
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

    def ajouter_patrimoine(self, patrimoine: Patrimoine):
        self.patrimoines.append(patrimoine)

    # Création date
    def _creer_date(self, jour: int, mois: int, annee: int):
        """
        Crée la date au format jour/mois/année
        tout en sécurisant les jours > 28.
        """
        jour_securise = min(jour, 28)
        return datetime(annee, mois, jour_securise)


    # Revenus
    def revenus_du_mois(self, mois: int):

        total = 0

        for rev in self.revenus:
            total += rev.montant_pour_mois(mois)

        return total



    # Dépenses
    def total_depenses_du_mois(self, mois: int, type_depense: str | None = None):

        total = 0

        for dep in self.depenses:

            if not dep.est_a_appliquer(mois):
                continue

            if type_depense is None or dep.type_depense == type_depense:
                total += dep.montant

        return total


    # Simul financière
    def appliquer_flux_sur_compte(
        self,
        compte: Compte,
        compte_id: int,
        date_du_jour: datetime,
        date_cible: datetime
    ):
        """
        Simule les flux entre date_du_jour et date_cible
        uniquement pour le compte concerné
        """

        mois_actuel = date_du_jour.month
        annee_actuelle = date_du_jour.year

        while True:

            # arrêt simulation
            if datetime(annee_actuelle, mois_actuel, 1) > date_cible:
                break


            # REVENUS
            for rev in self.revenus:

                if getattr(rev, "id_compte", None) != compte_id:
                    continue

                montant = rev.montant_pour_mois(mois_actuel)

                if montant <= 0:
                    continue

                jour = rev.jour or 1

                date_mvt = self._creer_date(jour, mois_actuel, annee_actuelle)

                if date_du_jour <= date_mvt <= date_cible:
                    compte.appliquer_mouvement(montant, "credit", "revenu", date_mvt)


            # DEPENSES
            for dep in self.depenses:

                if getattr(dep, "id_compte", None) != compte_id:
                    continue

                if not dep.est_a_appliquer(mois_actuel):
                    continue

                jour = dep.jour or 1

                mois_depense = (
                    dep.mois if dep.type_depense == "unique"
                    else mois_actuel
                )

                date_mvt = self._creer_date(jour, mois_depense, annee_actuelle)

                if date_du_jour <= date_mvt <= date_cible:
                    compte.appliquer_mouvement(dep.montant, "debit", "depense", date_mvt)


            # CREDITS (mensualités)
            for cred in self.credits:

                if getattr(cred, "id_compte", None) != compte_id:
                    continue

                montant = cred.mensualite_client(self)

                if montant <= 0:
                    continue

                date_mvt = self._creer_date(1, mois_actuel, annee_actuelle)

                if date_du_jour <= date_mvt <= date_cible:
                    compte.appliquer_mouvement(montant, "debit", "credit", date_mvt)


            # MOIS SUIVANT
            if mois_actuel == 12:
                mois_actuel = 1
                annee_actuelle += 1
            else:
                mois_actuel += 1

    # Affichage
    def __repr__(self):

        return (
            f"Client: {self.nom} - "
            f"Revenus: {len(self.revenus)} - "
            f"Dépenses: {len(self.depenses)} - "
            f"Crédits: {len(self.credits)} - "
            f"Comptes: {len(self.comptes)}"
        )