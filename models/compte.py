from datetime import datetime

class Compte:

    def __init__(self, banque, nom_compte, solde, jour_actuel):
        
        self.banque = str(banque)
        self.nom_compte = str(nom_compte)
        self.solde = float(solde)
        jour_actuel = datetime.strptime(jour_actuel, "%d-%m-%Y")

    def __repr__(self):
        return f"{self.nom_compte} ({self.banque}) - Solde: {self.solde} €"