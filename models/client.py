from models.compte import Compte
from models.credit import Credit
from models.epargne import Epargne
from models.depense import Depense
from models.revenu import Revenu
from models.patrimoine import Patrimoine
from typing import List
from datetime import datetime, timedelta
import calendar


class Client:
    """
    Représente un client avec ses comptes, revenus, dépenses, crédits, épargnes et patrimoines.

    Attributs:
        nom (str): nom du client.
        revenus (List[Revenu]): liste des revenus.
        depenses (List[Depense]): liste des dépenses.
        credits (List[Credit]): liste des crédits.
        epargnes (List[Epargne]): liste des épargnes.
        comptes (List[Compte]): liste des comptes bancaires.
        patrimoines (List[Patrimoine]): liste des patrimoines.
    """

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
        """
        Ajoute un revenu au client.
        Si le revenu est principal, les autres revenus sont marqués comme non principaux.
        """
        if revenu.est_revenu_principal:
            for r in self.revenus:
                r.est_revenu_principal = False
        self.revenus.append(revenu)


    def ajouter_depense(self, depense: Depense):
        self.depenses.append(depense)

    def ajouter_credit(self, credit: Credit, part: float = 1.0):
        """Ajoute un crédit au client et définit la part de ce client dans le crédit."""
        credit.ajouter_emprunteur(self, part)
        self.credits.append(credit)

    def attacher_credit(self, credit: Credit):
        """Attache un crédit déjà configuré (emprunteurs et parts déjà enregistrés) sans modifier les parts."""
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
        """Retourne le dernier instant du mois spécifié (23:59:59)."""
        dernier = calendar.monthrange(annee, mois)[1]
        return datetime(annee, mois, dernier, 23, 59, 59)
 

    # Revenus / Dépenses agrégés
    def revenus_du_mois(self, mois: int) -> float:
        """Calcule le total des revenus du client pour le mois donné."""
        return sum(r.montant_pour_mois(mois) for r in self.revenus)
 
    def total_depenses_du_mois(self, mois: int, type_depense: str | None = None) -> float:
        """Calcule le total des dépenses applicables pour le mois, filtré par type si précisé."""
        total = 0.0
        for dep in self.depenses:
            if not dep.est_a_appliquer(mois):
                continue
            if type_depense is None or dep.type_depense == type_depense:
                total += dep.montant
        return total
 
    def revenu_principal(self) -> Revenu | None:
        """Retourne le revenu marqué comme principal, ou None."""
        for r in self.revenus:
            if r.est_revenu_principal:
                return r
        return None
 
   
    # Projection
    @staticmethod
    def projeter_solde_compte(
        compte: Compte,
        compte_id: int,
        proprietaires: "list[Client]",
        aujourd_hui: datetime,
        date_cible: datetime
    ) -> float:
        """
        Calcule le solde estimé du compte à date_cible.
        Agrège les flux de tous les propriétaires (individuel ou joint).
        Point de départ : compte.solde_initial (= solde du jour saisi).
        Chaque flux est appliqué si sa date tombe dans [aujourd_hui, date_cible].
        Pour les crédits : si deja_preleve=True, on saute le mois courant.
        """
        if date_cible <= aujourd_hui:
            return compte.solde_initial
 
        solde = compte.solde_initial
        mois_actuel = aujourd_hui.month
        annee_actuelle = aujourd_hui.year
 
        while True:
            debut_mois = datetime(annee_actuelle, mois_actuel, 1)
            if debut_mois > date_cible:
                break
 
            for client in proprietaires:
 
                # Revenus
                for rev in client.revenus:
                    if getattr(rev, "id_compte", None) != compte_id:
                        continue
                    montant = rev.montant_pour_mois(mois_actuel)
                    if montant <= 0:
                        continue
                    date_flux = Client._creer_date(rev.jour, mois_actuel, annee_actuelle)
                    if aujourd_hui < date_flux <= date_cible:
                        solde += montant
 
                # Dépenses
                for dep in client.depenses:
                    if getattr(dep, "id_compte", None) != compte_id:
                        continue
                    if not dep.est_a_appliquer(mois_actuel):
                        continue
                    mois_dep = dep.mois if dep.type_depense == "unique" else mois_actuel
                    date_flux = Client._creer_date(dep.jour or 1, mois_dep, annee_actuelle)
                    if aujourd_hui < date_flux <= date_cible:
                        solde -= dep.montant
 
                # Crédits
                for cred in client.credits:
                    if getattr(cred, "id_compte", None) != compte_id:
                        continue
                    est_mois_courant = (
                        mois_actuel == aujourd_hui.month
                        and annee_actuelle == aujourd_hui.year
                    )
                    if cred.deja_preleve and est_mois_courant:
                        continue
                    mensualite = cred.mensualite_client(client)
                    if mensualite <= 0:
                        continue
                    date_flux = Client._creer_date(
                        cred.jour_echeance, mois_actuel, annee_actuelle
                    )
                    if aujourd_hui < date_flux <= date_cible:
                        solde -= mensualite
 
            # Mois suivant
            if mois_actuel == 12:
                mois_actuel = 1
                annee_actuelle += 1
            else:
                mois_actuel += 1
 
        return round(solde, 2)
 
    def projeter_solde(
        self,
        compte: Compte,
        compte_id: int,
        aujourd_hui: datetime,
        date_cible: datetime
    ) -> float:
        """Projection de solde pour un compte individuel (façade instance)."""
        return Client.projeter_solde_compte(
            compte, compte_id, [self], aujourd_hui, date_cible
        )
 
    # Les 3 horizons
 
    @staticmethod
    def solde_fin_de_mois(
        compte: Compte,
        compte_id: int,
        proprietaires: "list[Client]",
        aujourd_hui: datetime
    ) -> float:
        """Solde estimé au dernier jour du mois en cours."""
        date_cible = Client._dernier_jour_mois(aujourd_hui.year, aujourd_hui.month)
        return Client.projeter_solde_compte(
            compte, compte_id, proprietaires, aujourd_hui, date_cible
        )
 
    @staticmethod
    def solde_prochain_salaire(
        compte: Compte,
        compte_id: int,
        proprietaires: "list[Client]",
        aujourd_hui: datetime
    ) -> tuple:
        """
        Solde estimé à la veille du prochain versement du revenu principal
        parmi tous les propriétaires.
        Retourne (solde, revenu_principal, date_salaire) ou (None, None, None).
        """
        rev = None
        for client in proprietaires:
            rev = client.revenu_principal()
            if rev:
                break
 
        if rev is None:
            return None, None, None
 
        jour = rev.jour
        date_salaire = Client._creer_date(jour, aujourd_hui.month, aujourd_hui.year)
        if date_salaire <= aujourd_hui:
            if aujourd_hui.month == 12:
                date_salaire = Client._creer_date(jour, 1, aujourd_hui.year + 1)
            else:
                date_salaire = Client._creer_date(
                    jour, aujourd_hui.month + 1, aujourd_hui.year
                )
 
        date_cible = (date_salaire - timedelta(days=1)).replace(
            hour=23, minute=59, second=59
        )
        solde = Client.projeter_solde_compte(
            compte, compte_id, proprietaires, aujourd_hui, date_cible
        )
        return solde, rev, date_salaire
 
    @staticmethod
    def solde_a_date_libre(
        compte: Compte,
        compte_id: int,
        proprietaires: "list[Client]",
        aujourd_hui: datetime,
        date_cible: datetime
    ) -> float:
        """Solde estimé à une date librement choisie."""
        return Client.projeter_solde_compte(
            compte, compte_id, proprietaires, aujourd_hui, date_cible
        )
 
    @staticmethod
    def projections(
        compte: Compte,
        compte_id: int,
        proprietaires: "list[Client]",
        aujourd_hui: datetime,
        date_libre: datetime | None = None
    ) -> dict:
        """
        Retourne les 3 horizons en un seul appel.
        Accepte plusieurs propriétaires pour les comptes joints.
        """
        solde_sal, rev_principal, date_sal = Client.solde_prochain_salaire(
            compte, compte_id, proprietaires, aujourd_hui
        )
 
        return {
            "solde_actuel": compte.solde_initial,
            "fin_de_mois": Client.solde_fin_de_mois(
                compte, compte_id, proprietaires, aujourd_hui
            ),
            "prochain_salaire": solde_sal,
            "revenu_principal": rev_principal.type_de_revenu if rev_principal else None,
            "date_prochain_salaire": date_sal,
            "date_libre": date_libre,
            "solde_date_libre": (
                Client.solde_a_date_libre(
                    compte, compte_id, proprietaires, aujourd_hui, date_libre
                ) if date_libre else None
            ),
            "proprietaires": [c.nom for c in proprietaires],
            "est_joint": len(proprietaires) > 1,
        }
 
    # Affichage
 
    def __repr__(self):
        return (
            f"Client : {self.nom} — "
            f"Revenus : {len(self.revenus)} — "
            f"Dépenses : {len(self.depenses)} — "
            f"Crédits : {len(self.credits)} — "
            f"Comptes : {len(self.comptes)}"
        )