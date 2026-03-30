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
                 mensualite: float, 
                 jour_echeance: int, 
                 capital_emprunte: float | None = None, 
                 crd: float | None = None, 
                 taux:float | None = None, 
                 duree_initiale: int | None = None, 
                 fin_credit=None, 
                 compte=None,
                 id_compte: int | None = None,
                 deja_preleve: bool = False):
        """
        Représente un crédit avec ses caractéristiques et ses emprunteurs.

        Attributs:
            type_de_credit (int): identifiant du type de crédit.
            mensualite (float): montant de la mensualité totale.
            jour_echeance (int): jour du mois de l'échéance (1-28).
            capital_emprunte (float | None): capital initial emprunté.
            crd (float | None): capital restant dû.
            taux (float | None): taux du crédit.
            duree_initiale (int | None): durée initiale en mois.
            fin_credit (datetime | None): date de fin du crédit.
            compte: compte associé au crédit.
            id_compte (int | None): ID du compte associé.
            deja_preleve (bool): indique si la mensualité du mois courant a déjà été prélevée.
            emprunteur (dict): dictionnaire {Client: part} indiquant la part de chaque emprunteur.
        """

        if type_de_credit not in self.REGLES_CREDIT:
            raise ValueError("Type de crédit invalide")

        regles = self.REGLES_CREDIT[type_de_credit]
        if mensualite <= 0:
            raise ValueError("La mensualité doit être positive")
 
        if not (1 <= jour_echeance <= 28):
            raise ValueError("Le jour d'échéance doit être compris entre 1 et 28")
 
 
        if duree_initiale is not None:
            if duree_initiale <= 0:
                raise ValueError("La durée doit être positive")
            duree_max = regles["duree_max"]
            if duree_max and duree_initiale > duree_max:
                raise ValueError(
                    f"La durée maximale pour {regles['nom']} est de {duree_max} mois"
                )
 
        if taux is not None and taux < 0:
            raise ValueError("Le taux doit être positif")
 
        if capital_emprunte is not None and capital_emprunte < 0:
            raise ValueError("Le capital emprunté doit être positif")
 
        if crd is not None and crd < 0:
            raise ValueError("Le CRD doit être positif")
 
        self.type_de_credit = type_de_credit
        self.mensualite = float(mensualite)
        self.jour_echeance = int(jour_echeance)
        self.capital_emprunte = float(capital_emprunte) if capital_emprunte is not None else None
        self.crd = float(crd) if crd is not None else None
        self.taux = float(taux) if taux is not None else None
        self.duree_initiale = int(duree_initiale) if duree_initiale is not None else None
        self.compte = compte
        self.id_compte = id_compte
        self.deja_preleve = deja_preleve
        self.emprunteur = {}
 
        if fin_credit is None:
            self.fin_credit = None
        elif isinstance(fin_credit, datetime):
            self.fin_credit = fin_credit
        elif isinstance(fin_credit, str) and fin_credit.strip() != "":
            for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
                try:
                    self.fin_credit = datetime.strptime(fin_credit, fmt)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("Format de date invalide. Attendu : YYYY-MM-DD ou DD-MM-YYYY")
        else:
            self.fin_credit = None
 
    def ajouter_emprunteur(self, client, part: float = 1.0):
        if not (0 < part <= 1):
            raise ValueError("La part doit être comprise entre 0 et 1")
        ancienne_part = self.emprunteur.get(client, 0)
        if sum(self.emprunteur.values()) - ancienne_part + part > 1.0001:
            raise ValueError("La somme des parts dépasse 100%")
        self.emprunteur[client] = part
 
    def mensualite_client(self, client) -> float:
        """
        Retourne la mensualité du crédit à la charge du client.

        Args:
            client: objet Client associé au crédit.

        Returns:
            float: montant mensuel pour le client.

        Raises:
            ValueError: si le client n'est pas associé au crédit.
        """
        if client not in self.emprunteur:
            raise ValueError("Ce client n'est pas associé à ce crédit")
        
        return self.mensualite * self.emprunteur[client]
 
    def nombre_emprunteurs(self) -> int:
        """Retourne le nombre d'emprunteurs attachés au crédit."""
        return len(self.emprunteur)
    
    def pourcentages_emprunteurs(self) -> dict:
        """Retourne un dictionnaire {nom_client: part} des emprunteurs."""
        return {c.nom: p for c, p in self.emprunteur.items()}

    @property
    def nom(self) -> str:
        return self.REGLES_CREDIT[self.type_de_credit]["nom"]
 
    def mois_restants(self) -> int | None:
        """Retourne le nombre de mois restants si fin_credit est renseignée."""
        if self.fin_credit is None:
            return None
        delta = self.fin_credit - datetime.now()
        return max(0, round(delta.days / 30.44))
 
    def cout_total_restant(self, client) -> float | None:
        """
        Coût total restant (intérêts) pour la part du client.
        Nécessite fin_credit, crd et mensualite.
        """
        mois = self.mois_restants()
        if mois is None or self.crd is None:
            return None
        part = self.emprunteur.get(client, 1.0)
        return round(max(0, self.mensualite_client(client) * mois - self.crd * part), 2)
 
    def __repr__(self):
        noms = ", ".join(f"{c.nom} ({p * 100:.0f}%)" for c, p in self.emprunteur.items())
        return f"{self.nom} - Mensualité : {self.mensualite}€ - Emprunteurs : {noms}"