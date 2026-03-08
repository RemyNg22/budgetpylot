from datetime import datetime
class Compte:

    def __init__(self, banque, nom_compte, solde, jour_actuel, 
                 depenses_fixes:float = 0, depenses_variables: float = 0):
        
        self.banque = str(banque)
        self.nom_compte = str(nom_compte)
        self.solde = float(solde)
        jour_actuel = datetime.strptime(jour_actuel, "%d-%m-%Y")
        self.depenses_fixes = float(depenses_fixes)
        self.depenses_variables = float(depenses_variables)

    def __repr__(self):
        return f"{self.nom_compte} ({self.banque}) - Solde: {self.solde} €"