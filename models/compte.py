from datetime import datetime
from typing import List, Dict

class Compte:
    def __init__(self, banque: str, nom_compte: str, solde_initial: float):
        self.banque = banque.strip()
        self.nom_compte = nom_compte.strip()
        self.solde_initial = float(solde_initial)
        self.mouvements: List[Dict] = []

    def appliquer_mouvement(self, montant: float, type_mvt: str, source: str, date: datetime):
        if type_mvt not in ("credit", "debit"):
            raise ValueError("type_mvt doit être 'credit' ou 'debit'")
        self.mouvements.append({
            "type": type_mvt,
            "montant": montant,
            "source": source,
            "date": date
        })

    def solde_a_date(self, date: datetime) -> float:
        """Calcule le solde jusqu'à la date demandée"""
        solde = self.solde_initial
        for mv in self.mouvements:
            if mv["date"] <= date:
                if mv["type"] == "credit":
                    solde += mv["montant"]
                else:
                    solde -= mv["montant"]
        return solde

    def __repr__(self):
        return f"{self.nom_compte} ({self.banque}) - Solde initial: {self.solde_initial} €"