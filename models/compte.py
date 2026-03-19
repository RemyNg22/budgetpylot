from datetime import datetime
from typing import List, Dict

class Compte:
    def __init__(self, banque: str, nom_compte: str, solde_initial: float):
        self.banque = banque.strip()
        self.nom_compte = nom_compte.strip()
        self.solde_initial = float(solde_initial)

    def __repr__(self):
        return (
            f"{self.nom_compte} ({self.banque}) "
            f"— Solde actuel : {self.solde_initial:.2f} €"
        )