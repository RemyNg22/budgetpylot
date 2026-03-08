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

        self.type_de_credit = type_de_credit
        self.capital_emprunte = capital_emprunte
        self.crd = crd
        self.taux = taux
        self.duree_initiale = int(duree_initiale)
        self.mensualite = mensualite
        self.fin_credit = fin_credit

    def conditions_credit(self):

        if self.duree_initiale <= 0:
            raise ValueError("La durée doit être positive")

        regles = self.REGLES_CREDIT[self.type_de_credit]

        duree_max = regles["duree_max"]

        if duree_max and self.duree_initiale > duree_max:
            raise ValueError(
                f"La durée maximale pour {regles['nom']} est de {duree_max} mois"
            )

        return True