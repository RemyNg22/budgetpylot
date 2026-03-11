from compte import Compte
from credit import Credit
from epargne import Epargne
from client import Client
from depense import Depense
from revenu import Revenu
from datetime import datetime


print("\n=== LOGICIEL DE BUDGET ===\n")

date_du_jour = datetime.today()
clients = []


def choisir_client():
    """Permet de sélectionner un client existant"""
    if not clients:
        print("Aucun client enregistré.")
        return None

    for i, c in enumerate(clients):
        print(f"{i+1} - {c.nom}")

    try:
        choix = int(input("Choisir un client : "))
        return clients[choix-1]
    except:
        print("Choix invalide")
        return None


# Création du premier client
while True:

    personne = input("Ajouter une première personne (nom) : ")

    if not personne:
        print("Vous n'avez rien entré")
        continue

    if not personne.isalpha():
        print("Erreur : seules les lettres sont autorisées")
        continue

    nouveau_client = Client(personne)
    clients.append(nouveau_client)

    print("Personne ajoutée.")
    break



# Menu principal
while True:

    print("\n===== MENU =====")

    print("1 - Ajouter une personne")
    print("2 - Ajouter un compte")
    print("3 - Ajouter un revenu")
    print("4 - Ajouter une dépense")
    print("5 - Ajouter un crédit")
    print("6 - Ajouter une épargne")
    print("7 - Afficher les infos à la date du jour")
    print("8 - Simuler une date future")
    print("9 - Quitter")

    try:
        choix = int(input("Votre choix : "))
    except:
        print("Votre choix n'est pas valide.")
        continue



# Ajouter une personne
    if choix == 1:

        personne = input("Nom de la personne : ")

        if not personne:
            print("Vous n'avez rien entré")
            continue

        if not personne.isalpha():
            print("Erreur : seules les lettres sont autorisées")
            continue

        clients.append(Client(personne))
        print("Personne ajoutée")



# Ajouter un compte
    elif choix == 2:

        client = choisir_client()
        if not client:
            continue

        banque = input("Banque : ")
        nom_compte = input("Nom du compte : ")

        try:
            solde = float(input("Solde actuel : "))
        except:
            print("Montant invalide")
            continue

        compte = Compte(banque, nom_compte, solde)
        client.ajouter_compte(compte)

        print("Compte ajouté.")


# Ajouter un revenu
    elif choix == 3:

        client = choisir_client()
        if not client:
            continue

        type_revenu = input("Type de revenu (ex : salaire) : ")

        try:
            montant = float(input("Montant : "))
        except:
            print("Montant invalide")
            continue

        periodicite = input("Periodicité (mensuelle/annuelle/unique) : ")

        try:
            jour = int(input("Jour du versement : "))
        except:
            print("Jour invalide")
            continue

        mois = None

        if periodicite in ["annuelle", "unique"]:
            try:
                mois = int(input("Mois du versement : "))
            except:
                print("Mois invalide")
                continue

        revenu = Revenu(type_revenu, montant, periodicite, jour, mois)

        client.ajouter_revenu(revenu)

        print("Revenu ajouté.")


# Ajouter une dépense
    elif choix == 4:

        client = choisir_client()
        if not client:
            continue

        nom = input("Nom de la dépense : ")

        try:
            montant = float(input("Montant : "))
        except:
            print("Montant invalide")
            continue

        type_depense = input("Type (fixe / variable / unique) : ")

        try:
            jour = int(input("Jour : "))
        except:
            print("Jour invalide")
            continue

        mois = None

        if type_depense == "unique":
            try:
                mois = int(input("Mois : "))
            except:
                print("Mois invalide")
                continue

        depense = Depense(nom, montant, type_depense, jour, mois)

        client.ajouter_depense(depense)

        print("Dépense ajoutée.")


# Ajouter un crédit
    elif choix == 5:

        client = choisir_client()
        if not client:
            continue

        try:
            type_credit = int(input("Type de crédit (1 à 5) : "))
            capital = float(input("Capital emprunté : "))
            crd = float(input("CRD : "))
            taux = float(input("Taux : "))
            duree = int(input("Durée initiale (mois) : "))
            mensualite = float(input("Mensualité : "))
            fin = input("Date fin crédit (JJ/MM/AAAA) : ")
        except:
            print("Erreur de saisie")
            continue

        credit = Credit(
            type_credit,
            capital,
            crd,
            taux,
            duree,
            mensualite,
            datetime.strptime(fin, "%d/%m/%Y")
        )

        client.ajouter_credit(credit)

        print("Crédit ajouté.")


# Ajouter épargne
    elif choix == 6:

        client = choisir_client()
        if not client:
            continue

        try:
            type_epargne = int(input("Type d'épargne : "))
            solde = float(input("Solde : "))
        except:
            print("Erreur de saisie")
            continue

        epargne = Epargne(type_epargne, solde)

        client.ajouter_epargne(epargne)

        print("Epargne ajoutée.")


# Situation actuelle
    elif choix == 7:

        for client in clients:

            print(f"\nClient : {client.nom}")

            for compte in client.comptes:

                solde = compte.solde_a_date(date_du_jour)

                print(
                    f"{compte.nom_compte} : "
                    f"{solde:.2f} € au "
                    f"{date_du_jour.strftime('%d/%m/%Y')}"
                )


# Simulation future
    elif choix == 8:

        try:
            date_str = input("Date cible (JJ/MM/AAAA) : ")
            date_cible = datetime.strptime(date_str, "%d/%m/%Y")
        except:
            print("Date invalide")
            continue

        for client in clients:

            for compte in client.comptes:

                client.appliquer_flux_sur_compte(
                    compte,
                    date_du_jour,
                    date_cible
                )

                solde = compte.solde_a_date(date_cible)

                print(
                    f"{client.nom} - {compte.nom_compte} : "
                    f"{solde:.2f} € au "
                    f"{date_cible.strftime('%d/%m/%Y')}"
                )

# Quitter
    elif choix == 9:

        print("Fin du programme.")
        break


    else:
        print("Choix invalide.")