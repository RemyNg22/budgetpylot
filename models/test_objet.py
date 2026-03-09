from compte import Compte
from credit import Credit
from epargne import Epargne
from client import Client
from depense import Depense

jean = Client("Jean", revenu_mensuel=3000)


compte_courant = Compte(
    banque="LCL",
    nom_compte="Courant",
    solde=1500,
    jour_actuel="08-03-2026"
)

jean.ajouter_compte(compte_courant)


epargne1 = Epargne(type_epargne=1, solde=5000, versements_permanents=100, taux=1.5)
epargne2 = Epargne(type_epargne=6, solde=10000, versements_permanents=200, taux=1.5)

jean.ajouter_epargne(epargne1)
jean.ajouter_epargne(epargne2)

credit1 = Credit(
    type_de_credit=1,
    capital_emprunte=200000,
    crd=14500,
    taux=3.0,
    duree_initiale=240,
    mensualite=1000,
    fin_credit="01-01-2043"
)


jean.ajouter_credit(credit1, part=1.0)

depenses1 = Depense(nom='Loyer', montant=680, jour=5, type_depense="fixe")
depenses2 = Depense('Assurance', 60, 5, "fixe")
depenses3 = Depense('Nourriture', 230, 7, "variable")
depenses4 = Depense('Resto', 70, 9, "variable")

jean.ajouter_depenses(depenses1)
jean.ajouter_depenses(depenses2)
jean.ajouter_depenses(depenses3)
jean.ajouter_depenses(depenses4)

print(jean)
print("Comptes :", jean.comptes)
print("Épargnes :", jean.epargnes)
print("Crédits :", jean.credits)
print("Dépenses :", jean.depenses)
print("Mensualité du crédit pour Alice :", credit1.mensualite_client(jean))