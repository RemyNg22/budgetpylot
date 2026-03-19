class Revenu:

    TYPE_REVENU = (
        "salaire", "prime fixe", "bonus", "revenu non salarié", "allocations chômage",
        "pension d'invalidité", "retraite", "RSA", "APL", "allocations familiales",
        "prime d'activité", "bourse étudiante", "loyer", "revenu SCPI", "intérêt d'épargne",
        "coupon obligataire", "héritage", "donation", "gain exceptionnel",
        "vente d'actifs", "indemnité", "virement reçu", "remboursement", "autre"
    )

    PERIODE = ("mensuelle", "annuelle", "unique")

    def __init__(self, type_de_revenu: str, montant: float, periodicite: str, 
                 jour: int | None = None, mois: int | None = None, 
                 id_compte: int | None = None, est_revenu_principal: bool=False):

        if type_de_revenu not in self.TYPE_REVENU:
            raise ValueError("Type de revenu invalide")

        if periodicite not in self.PERIODE:
            raise ValueError("La périodicité doit être 'mensuelle', 'annuelle' ou 'unique'")

        if montant <= 0:
            raise ValueError("Le montant doit être positif")

        if jour is not None and not (1 <= jour <= 31):
            raise ValueError("Le jour doit être compris entre 1 et 31")

        if mois is not None and not (1 <= mois <= 12):
            raise ValueError("Le mois doit être compris entre 1 et 12")

        if periodicite in ("annuelle", "unique") and mois is None:
            raise ValueError("Pour un revenu annuel ou unique, le mois doit être précisé")

        self.type_de_revenu = type_de_revenu
        self.montant = float(montant)
        self.jour = jour or 1
        self.periodicite = periodicite
        self.mois = mois
        self.id_compte = id_compte
        self.est_revenu_principal= est_revenu_principal

    def montant_pour_mois(self, mois_actuel: int) -> float:
        if self.periodicite == "mensuelle":
            return self.montant
        elif self.periodicite in ("annuelle", "unique") and self.mois == mois_actuel:
            return self.montant
        return 0

    def __repr__(self):
        principal = " - revenu principal" if self.est_revenu_principal else ""
        return (
            f"{self.type_de_revenu} : {self.montant:.2f} € "
            f"({self.periodicite}, jour : {self.jour}, mois : {self.mois})"
            f"{principal}"
        )