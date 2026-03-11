from flask import Flask, render_template, request, redirect

from models.revenu import Revenu
from models.depense import Depense
from models.epargne import Epargne

TYPE_REVENU = Revenu.TYPE_REVENU
TYPE_EPARGNE = {k: v["nom"] for k, v in Epargne.TYPE_EPARGNE.items()}
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
        jours=JOURS,
        mois=MOIS)

# AJOUT REVENU
@app.route("/revenu", methods=["POST"])
def ajouter_revenu():

    type_revenu = request.form["type_revenu"]
    montant = float(request.form["montant"])
    periodicite = request.form["periodicite"]
    jour = int(request.form["jour"])

    mois = request.form["mois"]
    mois = int(mois) if mois else None

    revenu = Revenu(type_revenu, montant, periodicite, jour, mois)

    print(revenu)

    return redirect("/saisie")


# AJOUT DEPENSE
@app.route("/depense", methods=["POST"])
def ajouter_depense():

    nom = request.form["nom"]
    montant = float(request.form["montant"])
    type_depense = request.form["type_depense"]
    jour = int(request.form["jour"])

    mois = request.form["mois"]
    mois = int(mois) if mois else None

    depense = Depense(nom, montant, type_depense, jour, mois)

    print(depense)

    return redirect("/saisie")

# AJOUT EPARGNE
@app.route("/epargne", methods=["POST"])
def ajouter_epargne():

    type_epargne = int(request.form["type_epargne"])

    montant_initial = float(request.form["montant_initial"])

    versement_mensuel = request.form["versement_mensuel"]
    versement_mensuel = float(versement_mensuel) if versement_mensuel else 0

    taux = request.form["taux"]
    taux = float(taux) if taux else 0

    epargne = Epargne(
        type_epargne,
        montant_initial,
        versement_mensuel,
        taux
    )

    print(epargne)

    return redirect("/saisie")

if __name__ == "__main__":
    app.run(debug=True)