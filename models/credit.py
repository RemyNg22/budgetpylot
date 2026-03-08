from datetime import datetime

class Credit:

    REGLES_CREDIT = {
        1: {"nom": "Crédit immobilier amortissable", "duree_max": 360},
        2: {"nom": "Crédit in fine", "duree_max": 360},
        3: {"nom": "Prêt relais", "duree_max": 36},
        4: {"nom": "Crédit à la consommation", "duree_max": 120},
        5: {"nom": "Crédit renouvelable", "duree_max": None}
    }

    def __init__(self, type_de_credit, capital_emprunte, crd, taux, duree_initiale, mensualite, fin_credit):

        if type_de_credit not in self.REGLES_CREDIT:
            raise ValueError("Type de crédit invalide")
        
        regles = self.REGLES_CREDIT[type_de_credit]
        duree_max = regles["duree_max"]
        if duree_max and duree_initiale > duree_max:
            raise ValueError(f"La durée maximale pour {regles['nom']} est de {duree_max} mois")
        if duree_initiale <= 0:
            raise ValueError("La durée doit être positive")

        self.type_de_credit = type_de_credit
        self.capital_emprunte = float(capital_emprunte)
        self.crd = float(crd)
        self.taux = float(taux)
        self.duree_initiale = int(duree_initiale)
        self.mensualite = float(mensualite)
        self.fin_credit = datetime.strptime(fin_credit, "%d-%m-%Y")
        self.emprunteur = {}


    def ajouter_emprunteur(self, client, part: float = 1.0):
        """
        Ajoute un client et la part de remboursement qu'il prend en charge.
        pourcentage : fraction de la mensualité (0 < pourcentage <= 1)
        """
        if not (0 < part <=1):
            raise ValueError("La part doit être comprise entre 0 et 1")
        self.emprunteur[client] = part

    def mensualite_client(self, client):
        """
        Renvoie la mensualité que doit payer un client.
        """
        if client not in self.emprunteur:
            raise ValueError("Ce client n'est pas associé à ce crédit")
        return self.mensualite * self.emprunteur[client]

    def nombre_emprunteurs(self):
        """
        Renvoie le nombre d'emprunteurs sur ce crédit.
        """
        return len(self.emprunteur)

    def pourcentages_emprunteurs(self):
        """
        Renvoie un dictionnaire {Client.nom: pourcentage} des parts de mensualité.
        """
        return {c.nom: p for c, p in self.emprunteur.items()}

    def __repr__(self):
        noms = ", ".join([f"{c.nom} ({p*100:.0f}%)" for c, p in self.emprunteur.items()])
        nom_credit = self.REGLES_CREDIT[self.type_de_credit]["nom"]
        return f"{nom_credit} - Mensualité totale: {self.mensualite} € - Emprunteurs: {noms}"