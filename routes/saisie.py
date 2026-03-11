from flask import Blueprint, render_template, request, redirect, url_for
from models.client import Client
from models.revenu import Revenu
from models.depense import Depense

saisie_bp = Blueprint("saisie", __name__, template_folder="../templates")

clients = []

@saisie_bp.route("/budget", methods=["GET", "POST"])
def saisie_budget():
    if request.method == "POST":
        nom_client = request.form.get("nom_client", "Jean")
        client = next((c for c in clients if c.nom == nom_client), None)
        if not client:
            client = Client(nom_client)
            clients.append(client)

        type_revenu = request.form.get("type_revenu")
        montant = float(request.form.get("montant_revenu"))
        jour = int(request.form.get("jour_revenu"))
        mois = request.form.get("mois_revenu")
        mois = int(mois) if mois else None
        periodicite = request.form.get("periodicite")

        revenu = Revenu(type_revenu, montant, periodicite, jour, mois)
        client.ajouter_revenu(revenu)

        return redirect(url_for("saisie.saisie_budget"))

    return render_template("saisie_budget.html",
                           type_revenu=Revenu.TYPE_REVENU,
                           jours=list(range(1, 29)),
                           mois=list(range(1, 13))
                           )

@saisie_bp.route("/depense", methods=["POST"])
def saisie_depense():
    nom_client = request.form.get("nom_client", "Jean")
    client = next((c for c in clients if c.nom == nom_client), None)
    if not client:
        client = Client(nom_client)
        clients.append(client)

    nom = request.form.get("nom_depense")
    montant = float(request.form.get("montant_depense"))
    type_depense = request.form.get("type_depense")
    jour = int(request.form.get("jour_depense"))

    depense = Depense(nom, montant, type_depense, jour)
    client.ajouter_depense(depense)

    return redirect(url_for("saisie.saisie_budget"))