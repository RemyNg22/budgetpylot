"""
data/csv_manager.py
===================
Export et import de toutes les données de la session en un seul fichier CSV.

Format : chaque ligne a une colonne "type" qui indique la nature de l'objet.
L'ordre d'export est important pour l'import :
  1. clients
  2. comptes
  3. comptes_proprietaires (relation compte / client)
  4. revenus
  5. depenses
  6. credits
  7. credits_emprunteurs (relation credit / client + part)
  8. epargnes
  9. patrimoines
"""

import csv
import io
from datetime import datetime

# Export

def exporter_csv(clients: dict, comptes: dict) -> str:
    """
    Met toous les objets en mémoire dans un CSV.
    Retourne le contenu CSV sous forme de string.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # En-tête
    writer.writerow(["type", "champ1", "champ2", "champ3", "champ4", "champ5",
                     "champ6", "champ7", "champ8", "champ9", "champ10", "champ11"])

    # Clients
    for cid, client in clients.items():
        writer.writerow(["client", cid, client.nom, "", "", "", "", "", "", "", "", ""])

    # Comptes
    for cid, compte in comptes.items():
        writer.writerow([
            "compte", cid, compte.banque, compte.nom_compte,
            compte.solde_initial, "", "", "", "", "", "", ""
        ])

    # Relations compte / propriétaires
    for cid, compte in comptes.items():
        for client_id in compte.client_ids:
            writer.writerow(["compte_proprietaire", cid, client_id, "", "", "", "", "", "", "", "", ""])

    # Revenus
    for client_id, client in clients.items():
        for r in client.revenus:
            writer.writerow([
                "revenu",
                r.item_id,
                client_id,
                r.id_compte if r.id_compte is not None else "",
                r.type_de_revenu,
                r.montant,
                r.periodicite,
                r.jour if r.jour is not None else "",
                r.mois if r.mois is not None else "",
                int(r.est_revenu_principal),
                "", ""
            ])

    # Dépenses
    for client_id, client in clients.items():
        for d in client.depenses:
            writer.writerow([
                "depense",
                d.item_id,
                client_id,
                d.id_compte if d.id_compte is not None else "",
                d.nom,
                d.montant,
                d.type_depense,
                d.categorie_depense,
                d.jour if d.jour is not None else "",
                d.mois if d.mois is not None else "",
                "", ""
            ])
    # Crédits
    credits_exportes = set()
    for client_id, client in clients.items():
        for cr in client.credits:
            if cr.item_id not in credits_exportes:
                credits_exportes.add(cr.item_id)
                writer.writerow([
                    "credit",
                    cr.item_id,
                    cr.id_compte if cr.id_compte is not None else "",
                    cr.type_de_credit,
                    cr.capital_emprunte,
                    cr.crd,
                    cr.taux,
                    cr.duree_initiale,
                    cr.mensualite,
                    cr.fin_credit.strftime("%Y-%m-%d"),
                    cr.jour_echeance,
                    int(cr.deja_preleve)
                ])

    # Relations crédit / emprunteurs
    credits_exportes_rel = set()
    for client_id, client in clients.items():
        for cr in client.credits:
            if cr.item_id not in credits_exportes_rel:
                credits_exportes_rel.add(cr.item_id)
                for emprunteur, part in cr.emprunteur.items():
                    # On retrouve l'id du client emprunteur
                    emprunteur_id = next(
                        (cid for cid, c in clients.items() if c is emprunteur), None
                    )
                    if emprunteur_id is not None:
                        writer.writerow([
                            "credit_emprunteur",
                            cr.item_id,
                            emprunteur_id,
                            part,
                            "", "", "", "", "", "", "", ""
                        ])

    # Épargnes
    for client_id, client in clients.items():
        for e in client.epargnes:
            writer.writerow([
                "epargne",
                e.item_id,
                client_id,
                e.type_epargne,
                e.solde,
                e.versements_permanents,
                e.taux,
                "", "", "", "", ""
            ])

    # Patrimoines
    for client_id, client in clients.items():
        for p in client.patrimoines:
            credit_id = p.credit.item_id if p.credit else ""
            revenu_id = p.revenu.item_id if p.revenu else ""
            writer.writerow([
                "patrimoine",
                p.item_id,
                client_id,
                p.type_patrimoine,
                p.nom,
                p.valeur,
                p.part,
                credit_id,
                revenu_id,
                "", "", ""
            ])

    return output.getvalue()


# Import

def importer_csv(
    contenu: str,
    clients: dict,
    comptes: dict,
    next_client_id_ref: list,
    next_compte_id_ref: list,
    next_item_id_ref: list
) -> tuple[dict, dict, int, int, int]:
    """
    Recharge tous les objets depuis un CSV exporté.
    Retourne (clients, comptes, next_client_id, next_compte_id, next_item_id).
    """
    from models.client import Client
    from models.compte import Compte
    from models.revenu import Revenu
    from models.depense import Depense
    from models.credit import Credit
    from models.epargne import Epargne
    from models.patrimoine import Patrimoine

    # On repart de zéro
    clients.clear()
    comptes.clear()

    # Index temporaires pour reconstruire les relations
    credits_index = {}
    revenus_index = {}
    next_item_id = 0

    reader = csv.reader(io.StringIO(contenu))
    next(reader)

    # Passe 1 : clients et comptes
    rows = list(reader)

    for row in rows:
        if not row or row[0] == "client":
            if not row:
                continue
            cid = int(row[1])
            nom = row[2]
            clients[cid] = Client(nom)
            if cid >= next_client_id_ref[0]:
                next_client_id_ref[0] = cid + 1

        elif row[0] == "compte":
            cid = int(row[1])
            banque = row[2]
            nom_compte = row[3]
            solde_initial = float(row[4])
            comptes[cid] = Compte(banque, nom_compte, solde_initial)
            if cid >= next_compte_id_ref[0]:
                next_compte_id_ref[0] = cid + 1

    # Passe 2 : relations compte / propriétaires
    for row in rows:
        if not row or row[0] != "compte_proprietaire":
            continue
        compte_id = int(row[1])
        client_id = int(row[2])
        if compte_id in comptes and client_id in clients:
            comptes[compte_id].ajouter_proprietaire(client_id)
            clients[client_id].ajouter_compte(comptes[compte_id])

    # Passe 3 : revenus
    for row in rows:
        if not row or row[0] != "revenu":
            continue
        item_id = int(row[1])
        client_id = int(row[2])
        id_compte = int(row[3]) if row[3] != "" else None
        type_revenu = row[4]
        montant = float(row[5])
        periodicite = row[6]
        jour = int(row[7]) if row[7] != "" else None
        mois = int(row[8]) if row[8] != "" else None
        est_principal = bool(int(row[9]))

        if client_id not in clients:
            continue

        rev = Revenu(
            type_de_revenu=type_revenu,
            montant=montant,
            periodicite=periodicite,
            jour=jour,
            mois=mois,
            id_compte=id_compte,
            est_revenu_principal=est_principal,
        )
        rev.item_id = item_id
        revenus_index[item_id] = rev
        clients[client_id].ajouter_revenu(rev)
        if item_id >= next_item_id:
            next_item_id = item_id + 1

    # Passe 4 : dépenses
    for row in rows:
        if not row or row[0] != "depense":
            continue
        item_id = int(row[1])
        client_id = int(row[2])
        id_compte = int(row[3]) if row[3] != "" else None
        nom = row[4]
        montant = float(row[5])
        type_depense = row[6]
        categorie = row[7]
        jour = int(row[8]) if row[8] != "" else None
        mois = int(row[9]) if row[9] != "" else None

        if client_id not in clients:
            continue

        dep = Depense(
            nom=nom,
            montant=montant,
            type_depense=type_depense,
            categorie_depense=categorie,
            jour=jour,
            mois=mois,
            id_compte=id_compte,
        )
        dep.item_id = item_id
        clients[client_id].ajouter_depense(dep)
        if item_id >= next_item_id:
            next_item_id = item_id + 1

    # Passe 5 : crédits
    for row in rows:
        if not row or row[0] != "credit":
            continue
        item_id = int(row[1])
        id_compte = int(row[2]) if row[2] != "" else None
        type_credit = int(row[3])
        capital_emprunte = float(row[4])
        crd = float(row[5])
        taux = float(row[6])
        duree_initiale = int(row[7])
        mensualite = float(row[8])
        fin_credit = row[9]
        jour_echeance = int(row[10])
        deja_preleve = bool(int(row[11]))

        compte = comptes.get(id_compte) if id_compte is not None else None

        cr = Credit(
            type_de_credit=type_credit,
            capital_emprunte=capital_emprunte,
            crd=crd,
            taux=taux,
            duree_initiale=duree_initiale,
            mensualite=mensualite,
            fin_credit=fin_credit,
            jour_echeance=jour_echeance,
            compte=compte,
            id_compte=id_compte,
            deja_preleve=deja_preleve,
        )
        cr.item_id = item_id
        credits_index[item_id] = cr
        if item_id >= next_item_id:
            next_item_id = item_id + 1

    # Passe 6 : relations crédit / emprunteurs
    for row in rows:
        if not row or row[0] != "credit_emprunteur":
            continue
        credit_id = int(row[1])
        client_id = int(row[2])
        part = float(row[3])

        if credit_id not in credits_index or client_id not in clients:
            continue

        cr = credits_index[credit_id]
        client = clients[client_id]
        cr.ajouter_emprunteur(client, part)
        # On ajoute le crédit au client sans rappeler ajouter_emprunteur
        client.credits.append(cr)

    # Passe 7 : épargnes
    for row in rows:
        if not row or row[0] != "epargne":
            continue
        item_id = int(row[1])
        client_id = int(row[2])
        type_epargne = int(row[3])
        solde = float(row[4])
        versements = float(row[5])
        taux = float(row[6])

        if client_id not in clients:
            continue

        e = Epargne(type_epargne, solde, versements, taux)
        e.item_id = item_id
        clients[client_id].ajouter_epargne(e)
        if item_id >= next_item_id:
            next_item_id = item_id + 1

    # Passe 8 : patrimoines
    for row in rows:
        if not row or row[0] != "patrimoine":
            continue
        item_id = int(row[1])
        client_id = int(row[2])
        type_patrimoine = row[3]
        nom = row[4]
        valeur = float(row[5])
        part = float(row[6])
        credit_id = int(row[7]) if row[7] != "" else None
        revenu_id = int(row[8]) if row[8] != "" else None

        if client_id not in clients:
            continue

        credit_associe = credits_index.get(credit_id) if credit_id else None
        revenu_associe = revenus_index.get(revenu_id) if revenu_id else None

        p = Patrimoine(
            type_patrimoine=type_patrimoine,
            nom=nom,
            valeur=valeur,
            part=part,
            revenu=revenu_associe,
            credit=credit_associe,
        )
        p.item_id = item_id
        clients[client_id].ajouter_patrimoine(p)
        if item_id >= next_item_id:
            next_item_id = item_id + 1

    next_item_id_ref[0] = next_item_id

    return clients, comptes