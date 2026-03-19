from models.compte import Compte
from models.credit import Credit
from models.epargne import Epargne
from models.depense import Depense
from models.revenu import Revenu
from models.patrimoine import Patrimoine
from typing import List
from datetime import datetime, date, timedelta
import calendar


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
        if revenu.est_revenu_principal:
            for r in self.revenus:
                r.est_revenu_principal = False
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
    @staticmethod
    def _creer_date(jour: int, mois: int, annee: int) -> datetime:
        """Crée une datetime en sécurisant les jours > dernier jour du mois."""
        dernier_jour = calendar.monthrange(annee, mois)[1]
        jour_securise = min(jour, dernier_jour)
        return datetime(annee, mois, jour_securise)
 
    @staticmethod
    def _dernier_jour_mois(annee: int, mois: int) -> datetime:
        dernier = calendar.monthrange(annee, mois)[1]
        return datetime(annee, mois, dernier, 23, 59, 59)


    # Revenus
    def revenus_du_mois(self, mois: int) -> float:
        return sum(r.montant_pour_mois(mois) for r in self.revenus)

    def revenu_principal(self) -> Revenu | None:
        """Retourne le revenu marqué comme principal, ou None."""
        for r in self.revenus:
            if r.est_revenu_principal:
                return r
        return None

    # Dépenses
    def total_depenses_du_mois(self, mois: int, type_depense: str | None = None):

        total = 0

        for dep in self.depenses:

            if not dep.est_a_appliquer(mois):
                continue

            if type_depense is None or dep.type_depense == type_depense:
                total += dep.montant

        return total



    # Simul financière pour projeter le solde
    def projeter_solde(
        self, compte: Compte, compte_id: int,
        aujourd_hui: datetime,
        date_cible: datetime) -> float:
        """
        Calcule le solde estimé du compte à date_cible.
        """

        if date_cible <= aujourd_hui:
            return compte.solde_initial
 
        solde = compte.solde_initial
 
        mois_actuel  = aujourd_hui.month
        annee_actuelle = aujourd_hui.year
 
        while True:
            debut_mois = datetime(annee_actuelle, mois_actuel, 1)
 
            # si on dépasse la date cible
            if debut_mois > date_cible:
                break
 
            # Revenus
            for rev in self.revenus:
 
                if getattr(rev, "id_compte", None) != compte_id:
                    continue
 
                montant = rev.montant_pour_mois(mois_actuel)
                if montant <= 0:
                    continue
 
                date_flux = self._creer_date(rev.jour, mois_actuel, annee_actuelle)
 
                if aujourd_hui < date_flux <= date_cible:
                    solde += montant
 
            # Dépenses
            for dep in self.depenses:
 
                if getattr(dep, "id_compte", None) != compte_id:
                    continue
 
                if not dep.est_a_appliquer(mois_actuel):
                    continue
 
                mois_dep = dep.mois if dep.type_depense == "unique" else mois_actuel
                date_flux = self._creer_date(dep.jour or 1, mois_dep, annee_actuelle)
 
                if aujourd_hui < date_flux <= date_cible:
                    solde -= dep.montant
 
            # Crédits
            for cred in self.credits:
 
                if getattr(cred, "id_compte", None) != compte_id:
                    continue
 
                # Si déjà prélevé ce mois-ci, on saute uniquement le mois actuel
                est_mois_courant = (
                    mois_actuel == aujourd_hui.month
                    and annee_actuelle == aujourd_hui.year
                )
                if cred.deja_preleve and est_mois_courant:
                    continue
 
                mensualite = cred.mensualite_client(self)
                if mensualite <= 0:
                    continue
 
                date_flux = self._creer_date(
                    cred.jour_echeance, mois_actuel, annee_actuelle
                )
 
                if aujourd_hui < date_flux <= date_cible:
                    solde -= mensualite
 
            # Mois suivant
            if mois_actuel == 12:
                mois_actuel    = 1
                annee_actuelle += 1
            else:
                mois_actuel += 1
 
        return round(solde, 2)
 
    # Les 3 horizons pour Flask (solde à fin du mois, jusqu'à salaire et à date voulu)
 
    def solde_fin_de_mois(self, compte: Compte, compte_id: int,
                          aujourd_hui: datetime) -> float:
        """Solde estimé au dernier jour du mois en cours."""

        date_cible = self._dernier_jour_mois(aujourd_hui.year, aujourd_hui.month)
        return self.projeter_solde(compte, compte_id, aujourd_hui, date_cible)
 

    def solde_prochain_salaire(self, compte: Compte, compte_id: int, aujourd_hui: datetime) -> float | None:
        """
        Solde estimé à la veille du prochain versement du revenu principal.
        Retourne None si aucun revenu principal n'est défini.
        """
        rev = self.revenu_principal()
        if rev is None:
            return None
 
        # Cherche le prochain jour du revenu dans le mois courant ou le suivant
        jour = rev.jour
        date_salaire = self._creer_date(jour, aujourd_hui.month, aujourd_hui.year)
 
        # Si le salaire est déjà passé ce mois-ci, on prend le mois suivant
        if date_salaire <= aujourd_hui:
            if aujourd_hui.month == 12:
                date_salaire = self._creer_date(jour, 1, aujourd_hui.year + 1)
            else:
                date_salaire = self._creer_date(jour, aujourd_hui.month + 1, aujourd_hui.year)
 
        # On projette jusqu'à la veille du salaire (solde avant réception)
        date_cible = date_salaire - timedelta(days=1)
        date_cible = date_cible.replace(hour=23, minute=59, second=59)
 
        return self.projeter_solde(compte, compte_id, aujourd_hui, date_cible)
 
    def solde_a_date_libre(self, compte: Compte, compte_id: int,
                           aujourd_hui: datetime, date_cible: datetime) -> float:
        """Solde estimé à une date librement choisie par l'utilisateur."""
        return self.projeter_solde(compte, compte_id, aujourd_hui, date_cible)
 

    def projections(self, compte: Compte, compte_id: int,
                    aujourd_hui: datetime,
                    date_libre: datetime | None = None) -> dict:
        """
        Retourne les 3 horizons les routes Flask et les exports.
        """
        rev_principal = self.revenu_principal()
 
        return {
            "solde_actuel": compte.solde_initial,
            "fin_de_mois": self.solde_fin_de_mois(compte, compte_id, aujourd_hui),
            "prochain_salaire": self.solde_prochain_salaire(compte, compte_id, aujourd_hui),
            "revenu_principal": rev_principal.type_de_revenu if rev_principal else None,
            "date_prochain_salaire": (
                self._prochaine_date_salaire(rev_principal, aujourd_hui)
                if rev_principal else None
            ),
            "date_libre": date_libre,
            "solde_date_libre": (
                self.solde_a_date_libre(compte, compte_id, aujourd_hui, date_libre)
                if date_libre else None
            ),
        }
 
    def _prochaine_date_salaire(self, rev: Revenu, aujourd_hui: datetime) -> datetime:
        """Calcule la date du prochain versement du revenu principal."""
        jour = rev.jour
        date_s = self._creer_date(jour, aujourd_hui.month, aujourd_hui.year)
        if date_s <= aujourd_hui:
            if aujourd_hui.month == 12:
                date_s = self._creer_date(jour, 1, aujourd_hui.year + 1)
            else:
                date_s = self._creer_date(jour, aujourd_hui.month + 1, aujourd_hui.year)
        return date_s
 

    # Affichage
    def __repr__(self):
        return (
            f"Client : {self.nom} — "
            f"Revenus : {len(self.revenus)} — "
            f"Dépenses : {len(self.depenses)} — "
            f"Crédits : {len(self.credits)} — "
            f"Comptes : {len(self.comptes)}"
        )