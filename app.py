from flask import Flask, render_template, request, redirect
from models.revenu import Revenu
from models.depense import Depense
from models.credit import Credit
from models.epargne import Epargne
from data.dataframes import df_credits, df_depenses, df_epargnes, df_revenus

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

    new_id = len(df_revenus)

    df_revenus.loc[new_id] = [
        new_id,
        type_revenu,
        montant,
        periodicite,
        jour,
        mois
    ]

    return redirect("/saisie")

@app.route("/supprimer_revenu/<int:id>")
def supprimer_revenu(id):

    global df_revenus

    df_revenus = df_revenus[df_revenus.id != id]

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

    new_id = len(df_depenses)

    df_depenses.loc[new_id] = [
        new_id,
        nom,
        montant,
        type_depense,
        jour,
        mois
    ]

    return redirect("/saisie")

@app.route("/supprimer_depense/<int:id>")
def supprimer_depense(id):

    global df_depenses

    df_depenses = df_depenses[df_depenses.id != id]

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

    new_id = len(df_epargnes)

    df_epargnes.loc[new_id] = [
        new_id,
        type_epargne,
        solde,
        versement,
        taux
    ]

    return redirect("/saisie")

@app.route("/supprimer_epargne/<int:id>")
def supprimer_epargne(id):

    global df_epargnes

    df_epargnes = df_epargnes[df_epargnes.id != id]

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

    new_id = len(df_credits)

    df_credits.loc[new_id] = [
        new_id,
        type_credit,
        capital_emprunte,
        crd,
        taux,
        duree_initiale,
        mensualite,
        fin_credit
    ]

    return redirect("/saisie")

@app.route("/supprimer_credit/<int:id>")
def supprimer_credit(id):

    global df_credits

    df_credits = df_credits[df_credits.id != id]

    return redirect("/saisie")

if __name__ == "__main__":
    app.run(debug=True)