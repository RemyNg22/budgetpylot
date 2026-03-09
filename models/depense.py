class Depense:

    def __init__(self, nom: str, montant: float, jour: int, type_depense: str):

        if not (1 <= jour <= 31):
            raise ValueError("Le jour doit être compris entre 1 et 31")
        
        if type_depense not in ("fixe", "variable"):
            raise ValueError("Le type de dépense doit être 'fixe' ou 'variable'")
        
        self.nom = nom
        self.montant = montant
        self.jour = jour
        self.type_depense= type_depense


    def __repr__(self):
        return f"{self.nom} ({self.type_depense}) - {self.montant} € le jour {self.jour}"