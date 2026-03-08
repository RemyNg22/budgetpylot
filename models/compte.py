class Compte_Bancaire:

    def __init__(self, banque, nom, solde, taux):
        self.banque = banque
        self.nom = nom
        self.solde = solde
        self.taux = taux
        self.total_credit = 0
        self.total_debit_permanent = 0

    def revenu(self, credit):
        self.total_credit += credit

    def debit_permanent(self, debit_p):
        self.total_debit_permanent += debit_p