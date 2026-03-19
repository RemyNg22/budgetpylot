from datetime import datetime

class Credit:

    REGLES_CREDIT = {
        1: {"nom": "Crédit immobilier amortissable", "duree_max": 360},
        2: {"nom": "Crédit in fine", "duree_max": 360},
        3: {"nom": "Prêt relais", "duree_max": 36},
        4: {"nom": "Crédit à la consommation", "duree_max": 120},
        5: {"nom": "Crédit renouvelable", "duree_max": None},
        6: {"nom": "LOA", "duree_max": None},
        7: {"nom": "LLD", "duree_max": None}
    }

    def __init__(self, 
                 type_de_credit : int, 
                 capital_emprunte: float, 
                 crd: float, 
                 taux:float, 
                 duree_initiale: int, 
                 mensualite: float, 
                 fin_credit, 
                 jour_echeance: int=1, 
                 compte=None,
                 id_compte: int | None = None,
                 deja_preleve: bool = False):

        if type_de_credit not in self.REGLES_CREDIT:
            raise ValueError("Type de crédit invalide")

        regles = self.REGLES_CREDIT[type_de_credit]
        duree_max = regles["duree_max"]

        if duree_initiale <= 0:
            raise ValueError("La durée doit être positive")

        if duree_max and duree_initiale > duree_max:
            raise ValueError(f"La durée maximale pour {regles['nom']} est de {duree_max} mois")

        if taux < 0:
            raise ValueError("Le taux doit être positif")

        if mensualite <= 0:
            raise ValueError("La mensualité doit être positive")


        self.type_de_credit = type_de_credit
        self.capital_emprunte = float(capital_emprunte)
        self.crd = float(crd)
        self.taux = float(taux)
        self.duree_initiale = int(duree_initiale)
        self.mensualite = float(mensualite)
        self.jour_echeance = jour_echeance
        self.compte = compte
        self.id_compte = id_compte
        self.deja_preleve = deja_preleve
        self.emprunteur = {}

        if isinstance(fin_credit, datetime):
            self.fin_credit = fin_credit

        elif isinstance(fin_credit, str):
            for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
                try:
                    self.fin_credit = datetime.strptime(fin_credit, fmt)
                    break

                except ValueError:
                    continue
            else:
                raise ValueError('Format de date invalide. Attendu : YYYY-MM-DD ou DD-MM-YYYY')
            
        else:
            raise TypeError("fin_credit doit être une date ou chaine de caractères")


    def ajouter_emprunteur(self, client, part: float = 1.0):
        if not (0 < part <= 1):
            raise ValueError("La part doit être comprise entre 0 et 1")
        ancienne_part = self.emprunteur.get(client, 0)
        if sum(self.emprunteur.values()) - ancienne_part + part > 1:
            raise ValueError("La somme des parts dépasse 100%")
        self.emprunteur[client] = part

    def mensualite_client(self, client):

        if client not in self.emprunteur:
            raise ValueError("Ce client n'est pas associé à ce crédit")

        return self.mensualite * self.emprunteur[client]

    def nombre_emprunteurs(self):
        return len(self.emprunteur)

    def pourcentages_emprunteurs(self):
        return {c.nom: p for c, p in self.emprunteur.items()}

    @property
    def nom(self) -> str:
        """pour accéder au nom du type de crédit."""
        return self.REGLES_CREDIT[self.type_de_credit]["nom"]
 
    def __repr__(self):
        noms = ", ".join(f"{c.nom} ({p * 100:.0f}%)" for c, p in self.emprunteur.items())
        
        return (
            f"{self.nom} - "
            f"Mensualité totale : {self.mensualite} € - "
            f"Emprunteurs : {noms}"
        )