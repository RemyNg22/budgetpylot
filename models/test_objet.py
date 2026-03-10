from compte import Compte
from credit import Credit
from epargne import Epargne
from client import Client
from depense import Depense
from revenu import Revenu
from datetime import datetime


# Création des clients
jean = Client("Jean")
lucie = Client("Lucie")


# Ajout des comptes

compte_courant1 = Compte("LCL", "compte courant Jean", 754.10)
compte_courant_pro = Compte("CIC", "compte pro", 2039)
compte_courant2 = Compte("LCL", "compte lucie", 23001)

jean.ajouter_compte(compte_courant1)
jean.ajouter_compte(compte_courant_pro)
lucie.ajouter_compte(compte_courant2)


# Ajout des revenus
revenu1 = Revenu("salaire", 2500, "mensuelle", jour=30)
prime_interessement = Revenu("prime fixe", 5000, "annuelle", jour=6, mois=6)
revenu2 = Revenu("salaire", 3599, "mensuelle", jour=10)
heritage = Revenu("héritage", 240000, "unique", jour=5, mois=12)

jean.ajouter_revenu(revenu1)
jean.ajouter_revenu(prime_interessement)
lucie.ajouter_revenu(revenu2)
lucie.ajouter_revenu(heritage)


# Ajout des dépenses
depense1 = Depense("loyer", 1200, "fixe", jour=1)
depense2 = Depense("internet", 40, "fixe", jour=5)
depense3 = Depense("courses", 450, "variable", jour=15)
depense4 = Depense("vacances", 2000, "variable", jour=20)

jean.ajouter_depense(depense1)
jean.ajouter_depense(depense2)
jean.ajouter_depense(depense3)

lucie.ajouter_depense(depense1)
lucie.ajouter_depense(depense4)


# Ajout d’un crédit
credit1 = Credit(
    type_de_credit=4,
    capital_emprunte=10000,
    crd=10000,
    taux=5.5,
    duree_initiale=24,
    mensualite=450,
    fin_credit="01-12-2026"
)
jean.ajouter_credit(credit1, part=1.0)


# Simulation des flux
date_du_jour = datetime.strptime("10/03/2026", "%d/%m/%Y")
date_cible = datetime.strptime("30/04/2026", "%d/%m/%Y")

# Appliquer flux pour Jean
for compte in jean.comptes:
    jean.appliquer_flux_sur_compte(compte, date_du_jour, date_cible)

# Appliquer flux pour Lucie
for compte in lucie.comptes:
    lucie.appliquer_flux_sur_compte(compte, date_du_jour, date_cible)


# Affichage des soldes
print("=== Soldes au", date_cible.strftime("%d/%m/%Y"), "===")
for compte in jean.comptes:
    print(f"{jean.nom} - {compte.nom_compte}: {compte.solde_a_date(date_cible):,.2f} €")

for compte in lucie.comptes:
    print(f"{lucie.nom} - {compte.nom_compte}: {compte.solde_a_date(date_cible):,.2f} €")


# Affichage résumé revenus / dépenses
def afficher_resume(client: Client, mois: int):
    print(f"\n=== Résumé {client.nom} pour le mois {mois} ===")
    print("Revenus ce mois:", client.revenus_du_mois(mois))
    print("Total dépenses fixes:", client.total_depenses_du_mois(mois, "fixe"))
    print("Total dépenses variables:", client.total_depenses_du_mois(mois, "variable"))

# Mois d'avril
afficher_resume(jean, mois=4)
afficher_resume(lucie, mois=4)