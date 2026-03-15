from flask import Flask, render_template, request, redirect
from models.revenu import Revenu
from models.depense import Depense
from models.credit import Credit
from models.epargne import Epargne
from data.dataframes import df_credits, df_depenses, df_epargnes, df_revenus, df_clients, df_comptes, df_compte_clients

TYPE_REVENU = Revenu.TYPE_REVENU
TYPE_EPARGNE = {k: v["nom"] for k, v in Epargne.TYPE_EPARGNE.items()}
TYPE_CREDIT = {k: v["nom"] for k, v in Credit.REGLES_CREDIT.items()}
JOURS = list(range(1, 29))
MOIS = list(range(1, 13))


app = Flask(__name__)

# ACCUEIL
@app.route("/")
def index():
    return redirect("/saisie")

# PAGE SAISIE
@app.route("/saisie")
def saisie():
    return render_template(
        "saisie_budget.html",
        comptes=df_comptes.to_dict(orient="records"),
        clients=df_clients.to_dict(orient="records"),
        type_revenu=TYPE_REVENU,
        type_epargne=TYPE_EPARGNE,
        type_credit = TYPE_CREDIT,
        jours=JOURS,
        mois=MOIS,
        revenus=df_revenus.to_dict(orient="records"),
        depenses=df_depenses.to_dict(orient="records"),
        epargnes=df_epargnes.to_dict(orient="records"),
        credits=df_credits.to_dict(orient="records")
    )


# AJOUT CLIENT
@app.route("/client", methods=["POST"])
def ajouter_client():
    global df_clients

    nom = request.form["nom"]
    new_id = df_clients["id"].max() + 1 if not df_clients.empty else 0
    df_clients.loc[new_id] = [new_id, nom]
    return redirect("/saisie")


@app.route("/supprimer_client/<int:id>")
def supprimer_client(id):

    global df_clients, df_comptes, df_revenus, df_depenses, df_credits, df_epargnes, df_compte_clients

    comptes_client = df_compte_clients[df_compte_clients.id_client == id]["id_compte"].reset_index(drop=True)
    df_compte_clients = df_compte_clients[df_compte_clients.id_client != id].reset_index(drop=True)
    df_revenus = df_revenus[~df_revenus.id_compte.isin(comptes_client)].reset_index(drop=True)
    df_depenses = df_depenses[~df_depenses.id_compte.isin(comptes_client)].reset_index(drop=True)
    df_credits = df_credits[~df_credits.id_compte.isin(comptes_client)].reset_index(drop=True)
    df_epargnes = df_epargnes[df_epargnes.id_client != id].reset_index(drop=True)
    df_clients = df_clients[df_clients.id != id].reset_index(drop=True)

    return redirect("/saisie")

# AJOUT COMPTE
@app.route("/compte", methods=["POST"])
def ajouter_compte():
    global df_comptes, df_compte_clients

    nom_compte = request.form["new_compte"]
    clients = request.form.getlist("clients")

    if not clients:
        return redirect("/saisie")

    new_id = df_comptes["id"].max() + 1 if not df_comptes.empty else 0

    df_comptes.loc[new_id] = {
        "id": new_id,
        "nom_compte" : nom_compte,
        "id_client": None
    }

    part = 1/len(clients)

    for client in clients:

        df_compte_clients.loc[len(df_compte_clients)] = [
            new_id,
            int(client),
            part
        ]

    return redirect("/saisie")

@app.route("/supprimer_compte/<int:id>")
def supprimer_compte(id):

    global df_comptes, df_revenus, df_depenses, df_credits, df_compte_clients

    df_revenus = df_revenus[df_revenus.id_compte != id].reset_index(drop=True)
    df_depenses = df_depenses[df_depenses.id_compte != id].reset_index(drop=True)
    df_credits = df_credits[df_credits.id_compte != id].reset_index(drop=True)
    df_compte_clients = df_compte_clients[df_compte_clients.id_compte != id].reset_index(drop=True)
    df_comptes = df_comptes[df_comptes.id != id].reset_index(drop=True)

    return redirect("/saisie")


# AJOUT REVENU
@app.route("/revenu", methods=["POST"])
def ajouter_revenu():

    global df_revenus

    type_revenu = request.form["type_revenu"]
    montant = float(request.form["montant"])
    periodicite = request.form["periodicite"]
    jour = int(request.form["jour"])

    mois = request.form["mois"]
    mois = int(mois) if mois else None

    id_compte = int(request.form["id_compte"])

    new_id = df_revenus["id"].max() + 1 if not df_revenus.empty else 0

    df_revenus.loc[new_id] = [
        new_id,
        type_revenu,
        montant,
        periodicite,
        jour,
        mois,
        id_compte
    ]

    return redirect("/saisie")

@app.route("/supprimer_revenu/<int:id>")
def supprimer_revenu(id):

    global df_revenus

    df_revenus = df_revenus[df_revenus.id != id].reset_index(drop=True)

    return redirect("/saisie")


# AJOUT DEPENSE
@app.route("/depense", methods=["POST"])
def ajouter_depense():

    global df_depenses

    nom = request.form["nom"]
    montant = float(request.form["montant"])
    type_depense = request.form["type_depense"]
    jour = int(request.form["jour"])

    mois = request.form["mois"]
    mois = int(mois) if mois else None

    id_compte = int(request.form["id_compte"])

    new_id = df_depenses["id"].max() + 1 if not df_depenses.empty else 0

    df_depenses.loc[new_id] = [
        new_id,
        nom,
        montant,
        type_depense,
        jour,
        mois,
        id_compte
    ]

    return redirect("/saisie")

@app.route("/supprimer_depense/<int:id>")
def supprimer_depense(id):

    global df_depenses

    df_depenses = df_depenses[df_depenses.id != id].reset_index(drop=True)

    return redirect("/saisie")

# AJOUT EPARGNE
@app.route("/epargne", methods=["POST"])
def ajouter_epargne():

    global df_epargnes

    type_epargne = int(request.form["type_epargne"])
    solde = float(request.form["solde"])

    versement = request.form["versement_mensuel"]
    versement = float(versement) if versement else 0

    taux = request.form["taux"]
    taux = float(taux) if taux else 0

    id_client = int(request.form["id_client"])

    new_id = df_epargnes["id"].max() + 1 if not df_epargnes.empty else 0

    df_epargnes.loc[new_id] = [
        new_id,
        type_epargne,
        solde,
        versement,
        taux,
        id_client
    ]

    return redirect("/saisie")

@app.route("/supprimer_epargne/<int:id>")
def supprimer_epargne(id):

    global df_epargnes

    df_epargnes = df_epargnes[df_epargnes.id != id].reset_index(drop=True)

    return redirect("/saisie")


# AJOUT CREDIT
@app.route("/credit", methods=["POST"])
def ajouter_credit():
    global df_credits

    type_credit = request.form["type_credit"]
    capital_emprunte = float(request.form["capital_emprunte"])
    crd = float(request.form["crd"])
    taux = float(request.form["taux"])
    duree_initiale = int(request.form["duree_initiale"])
    mensualite = float(request.form["mensualite"])
    fin_credit = request.form["fin_credit"]    
    id_compte = int(request.form["id_compte"])

    new_id = df_credits["id"].max() + 1 if not df_credits.empty else 0

    df_credits.loc[new_id] = [
        new_id,
        type_credit,
        capital_emprunte,
        crd,
        taux,
        duree_initiale,
        mensualite,
        fin_credit,
        id_compte
    ]

    return redirect("/saisie")

@app.route("/supprimer_credit/<int:id>")
def supprimer_credit(id):

    global df_credits

    df_credits = df_credits[df_credits.id != id].reset_index(drop=True)

    return redirect("/saisie")

if __name__ == "__main__":
    app.run(debug=True)