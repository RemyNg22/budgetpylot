class Depense:

    TYPE_DEPENSE = ("fixe", "variable")

    def __init__(self, nom: str, montant: float, type_depense: str, jour: int | None = None):

        if jour is not None and not (1 <= jour <= 31):
            raise ValueError("Le jour doit être compris entre 1 et 31")
        
        if type_depense not in self.TYPE_DEPENSE:
            raise ValueError("Le type de dépense doit être 'fixe' ou 'variable'")
        
        if montant <= 0:
            raise ValueError("Le montant doit être positif")
        
        self.nom = nom
        self.montant = float(montant)
        self.jour = jour
        self.type_depense= type_depense


    def __repr__(self):
        jour_aff = self.jour if self.jour is not None else "non défini"
        return f"{self.nom} ({self.type_depense}) - {self.montant} € le jour {jour_aff}"