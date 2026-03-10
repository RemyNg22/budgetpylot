class Epargne:

    TYPE_EPARGNE={
        # Livrets réglementés
        1 : {"nom" : "Livret A", "plafond_min" : 10, "plafond_max" : 22950},
        2 : {"nom" : "LDDS", "plafond_min" : 10, "plafond_max" : 12000},
        3 : {"nom" : "LEP", "plafond_min" : 30, "plafond_max" : 10000},
        4 : {"nom" : "Livret Jeune", "plafond_min" : 10, "plafond_max" : 1600},
        5 : {"nom" : "CEL", "plafond_min" : 300, "plafond_max" : 15300},
        6 : {"nom" : "PEL", "plafond_min" : 225, "plafond_max" : 61200},

        # Livrets bancaires
        7 : {"nom" : "CSL", "plafond_min" : 10, "plafond_max" : None},
        8 : {"nom" : "CAT", "plafond_min" : 10, "plafond_max" : None},

        # Assurance / capitalisation
        9 : {"nom" : "Assurance Vie", "plafond_min" : None , "plafond_max" : None},
        10 : {"nom" : "Contrat de capitalisation", "plafond_min" : None, "plafond_max" : None},

        # Epargne retraite
        11 : {"nom" : "PER individuel", "plafond_min" : None, "plafond_max" : None},

        # Epargne salariale
        12 : {"nom" : "PEE", "plafond_min" : None, "plafond_max" : None},
        13 : {"nom" : "PERCO", "plafond_min" : None, "plafond_max" : None},

        # Placements financiers
        14 : {"nom" : "PEA", "plafond_min" : 15, "plafond_max" : 150000},
        15 : {"nom" : "PEA-PME", "plafond_min" : 15, "plafond_max" : 225000},
        16 : {"nom" : "Compte titres", "plafond_min" : None, "plafond_max" : None},

        # Autre type d'épargne
        17 : {"nom" : "Autre épargne", "plafond_min" : None, "plafond_max" : None}
    }

    def __init__(self, type_epargne, solde, versements_permanents: float= 0, taux: float = 0):
        if type_epargne not in self.TYPE_EPARGNE:
            raise ValueError("Type d'épargne invalide")
        
        if solde < 0:
            raise ValueError("Le solde ne peut pas être négatif")
        
        if taux < 0:
            raise ValueError("Le taux doit être positif")
        
        if versements_permanents < 0:
            raise ValueError("Le versement permanent doit être positif")
        
        produit = self.TYPE_EPARGNE[type_epargne]

        self.type_epargne = type_epargne
        self.nom = produit["nom"]
        self.solde = float(solde)
        self.versements_permanents = float(versements_permanents)
        self.plafond_min = produit["plafond_min"]
        self.plafond_max = produit["plafond_max"]
        self.taux = float(taux)

        if self.plafond_min is not None and self.solde < self.plafond_min:
            raise ValueError("Solde inférieur au minimum requis")
        
    def __repr__(self):
        return f"{self.nom} - Solde: {self.solde} € - Taux: {self.taux}%"