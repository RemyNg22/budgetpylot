class VersementPonctuel:
 
    def __init__(self, montant: float, jour: int, mois: int):
        """
        Représente un versement ponctuel sur un compte d'épargne.

        Attributs:
            montant (float): montant du versement.
            jour (int): jour du versement (1-28).
            mois (int): mois du versement (1-12).
        """
        if montant <= 0:
            raise ValueError("Le montant doit être positif")
        if not (1 <= jour <= 28):
            raise ValueError("Le jour doit être compris entre 1 et 28")
        if not (1 <= mois <= 12):
            raise ValueError("Le mois doit être compris entre 1 et 12")
        self.montant = float(montant)
        self.jour = jour
        self.mois = mois
 
    def __repr__(self):
        return f"Versement ponctuel : {self.montant:.2f} EUR le {self.jour}/{self.mois}"


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
        """
        Représente un produit d'épargne d'un client.

        Attributs:
            type_epargne (int): type d'épargne (clé dans TYPE_EPARGNE).
            nom (str): nom du produit (ex: Livret A, PEA, Assurance Vie).
            solde (float): solde actuel de l'épargne.
            versements_permanents (float): versements automatiques mensuels.
            taux (float): taux d'intérêt annuel (%) du produit.
            plafond_min (float | None): minimum légal ou imposé pour le produit.
            plafond_max (float | None): plafond légal ou imposé pour le produit.
            versements_ponctuels (list[VersementPonctuel]): liste des versements ponctuels.
        """
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
        self.versements_ponctuels: list[VersementPonctuel] = []

        if self.plafond_min is not None and self.solde < self.plafond_min:
            raise ValueError("Solde inférieur au minimum requis")

    def ajouter_versement_ponctuel(self, montant: float, jour: int, mois: int):
        """
        Ajoute un versement ponctuel à l'épargne.

        Args:
            montant (float): montant du versement.
            jour (int): jour du versement (1-28).
            mois (int): mois du versement (1-12).

        Returns:
            VersementPonctuel: instance créée et ajoutée à l'épargne.
        """
        vp = VersementPonctuel(montant, jour, mois)
        self.versements_ponctuels.append(vp)
        return vp
 
    def versements_ponctuels_du_mois(self, mois: int) -> float:
        return sum(v.montant for v in self.versements_ponctuels if v.mois == mois)
 
    def total_versements_mois(self, mois: int) -> float:
        return self.versements_permanents + self.versements_ponctuels_du_mois(mois)

    def __repr__(self):
        return f"{self.nom} - Solde: {self.solde} € - Taux: {self.taux}%"