class Depense:

    TYPE_DEPENSE = ("fixe", "variable_mensuelle", "unique")

    def __init__(
        self,
        nom: str,
        montant: float,
        type_depense: str,
        jour: int | None = None,
        mois: int | None = None
    ):

        if type_depense not in self.TYPE_DEPENSE:
            raise ValueError("Type de dépense invalide")

        if montant <= 0:
            raise ValueError("Le montant doit être positif")

        if jour is not None and not (1 <= jour <= 31):
            raise ValueError("Le jour doit être compris entre 1 et 31")

        if mois is not None and not (1 <= mois <= 12):
            raise ValueError("Le mois doit être compris entre 1 et 12")


        if type_depense in ("fixe", "variable_mensuelle") and jour is None:
            raise ValueError("Les dépenses mensuelles doivent avoir un jour")

        if type_depense == "unique":
            if jour is None or mois is None:
                raise ValueError("Une dépense unique doit avoir un jour et un mois")

        self.nom = nom
        self.montant = float(montant)
        self.type_depense = type_depense
        self.jour = jour
        self.mois = mois

    def est_a_appliquer(self, mois_actuel: int):
        """
        Permet de savoir si la dépense doit être appliquée pour un mois donné
        """
        if self.type_depense in ("fixe", "variable_mensuelle"):
            return True

        if self.type_depense == "unique" and self.mois == mois_actuel:
            return True

        return False

    def __repr__(self):

        if self.type_depense == "unique":
            return f"{self.nom} (unique) - {self.montant} € le {self.jour}/{self.mois}"

        return f"{self.nom} ({self.type_depense}) - {self.montant} € chaque mois le {self.jour}"