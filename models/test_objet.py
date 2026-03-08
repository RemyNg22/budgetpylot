from compte import Compte
from credit import Credit
from epargne import Epargne
from client import Client

jean = Client("Jean", revenu_mensuel=3000)


compte_courant = Compte(
    banque="LCL",
    nom_compte="Courant",
    solde=1500,
    jour_actuel="08-03-2026",
    depenses_fixes=500,
    depenses_variables=200
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

print(jean)
print("Comptes :", jean.comptes)
print("Épargnes :", jean.epargnes)
print("Crédits :", jean.credits)
print("Mensualité du crédit pour Alice :", credit1.mensualite_client(jean))