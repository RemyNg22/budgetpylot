from flask import Flask, render_template, request, redirect, flash
import pandas as pd
from datetime import datetime

# Import classes POO
from models.client import Client
from models.compte import Compte
from models.revenu import Revenu
from models.depense import Depense
from models.credit import Credit
from models.epargne import Epargne
from models.patrimoine import Patrimoine

app = Flask(__name__)
app.secret_key = "secret"

# Stockage global
clients = {}
comptes = {}
next_client_id = 0
next_compte_id = 0
next_item_id = 0

JOURS = list(range(1, 29))
MOIS = list(range(1, 13))

# Utilitaires
def parse_int(value, default=None):
    try:
        if value in (None, ""):
            return default
        return int(value)
    except:
        return default


def parse_float(value, default=None):
    try:
        if value in (None, ""):
            return default
        value = value.replace(",", ".")
        return float(value)
    except:
        return default
    
def parse_str(value, default=""):
    return value.strip() if value else default

def safe_redirect(msg=None):
    if msg:
        flash(msg)
    return redirect("/saisie")


# Dataframe
def generate_df():
    """Crée des DataFrames temporaires pour affichage depuis les objets POO"""
    df_clients = pd.DataFrame([{"id": cid, "nom": c.nom} for cid, c in clients.items()])

    df_comptes = pd.DataFrame([{"id": cid, "nom_compte": c.nom_compte} for cid, c in comptes.items()])

    df_revenus = []
    df_depenses = []
    df_credits = []
    df_epargnes = []
    df_patrimoines = []

    for cid, client in clients.items():
        for r in client.revenus:
            df_revenus.append({
                "id": id(r),
                "type_revenu": r.type_de_revenu,
                "montant": r.montant,
                "periodicite": r.periodicite,
                "jour": r.jour,
                "mois": r.mois,
                "id_client": cid,
                "id_compte": getattr(r, "id_compte", None)
            })
        for d in client.depenses:
            df_depenses.append({
                "id": id(d),
                "nom": d.nom,
                "montant": d.montant,
                "type_depense": d.type_depense,
                "categorie_depense": d.categorie_depense,
                "jour": d.jour,
                "mois": d.mois,
                "id_client": cid,
                "id_compte": getattr(d, "id_compte", None)
            })
        for cr in client.credits:
            df_credits.append({
                "id": id(cr),
                "type_credit": cr.type_de_credit,
                "capital_emprunte": cr.capital_emprunte,
                "crd": cr.crd,
                "taux": cr.taux,
                "duree_initiale": cr.duree_initiale,
                "mensualite": cr.mensualite,
                "fin_credit": cr.fin_credit.strftime("%d-%m-%Y"),
                "id_client": cid,
                "id_compte": getattr(cr, "id_compte", None)
            })
        for e in client.epargnes:
            df_epargnes.append({
                "id": id(e),
                "type_epargne": e.type_epargne,
                "nom": e.nom,
                "solde": e.solde,
                "versement": e.versements_permanents,
                "taux": e.taux,
                "id_client": cid
            })

        for p in client.patrimoines:
            df_patrimoines.append({
                "id": id(p),
                "type_patrimoine": p.type_patrimoine,
                "nom": p.nom,
                "valeur": p.valeur,
                "part": p.part,
                "revenu": id(p.revenu) if p.revenu else None,
                "credit": id(p.credit) if p.credit else None,
                "id_client": cid
            })

    return {
        "clients": df_clients,
        "comptes": df_comptes,
        "revenus": pd.DataFrame(df_revenus),
        "depenses": pd.DataFrame(df_depenses),
        "credits": pd.DataFrame(df_credits),
        "epargnes": pd.DataFrame(df_epargnes),
        "patrimoines": pd.DataFrame(df_patrimoines)
    }

# Routes

@app.route("/")
def index():
    return redirect("/saisie")

@app.route("/saisie")
def saisie():
    dfs = generate_df()
    return render_template(
        "saisie_budget.html",
        clients=dfs["clients"].to_dict(orient="records"),
        comptes=dfs["comptes"].to_dict(orient="records"),
        revenus=dfs["revenus"].to_dict(orient="records"),
        depenses=dfs["depenses"].to_dict(orient="records"),
        credits=dfs["credits"].to_dict(orient="records"),
        epargnes=dfs["epargnes"].to_dict(orient="records"),
        patrimoines=dfs["patrimoines"].to_dict(orient="records"),
        type_revenu=Revenu.TYPE_REVENU,
        type_depense = Depense.TYPE_DEPENSE,
        categorie_depense=Depense.CATEGORIE_DEPENSE,
        type_credit={k:v["nom"] for k,v in Credit.REGLES_CREDIT.items()},
        type_epargne={k:v["nom"] for k,v in Epargne.TYPE_EPARGNE.items()},
        type_patrimoine=Patrimoine.TYPE_PATRIMOINE,
        jours=JOURS,
        mois=MOIS
    )

# Client
@app.route("/client", methods=["POST"])
def ajouter_client():
    global next_client_id
    nom = parse_str(request.form.get("nom"))

    if not nom:
        return safe_redirect("Nom invalide")

    clients[next_client_id] = Client(nom)
    next_client_id += 1
    return redirect("/saisie")

@app.route("/supprimer_client/<int:id>")
def supprimer_client(id):
    clients.pop(id, None)
    return redirect("/saisie")

# Compte
@app.route("/compte", methods=["POST"])
def ajouter_compte():
    global next_compte_id

    nom = parse_str(request.form.get("new_compte"))
    client_ids = request.form.getlist("clients")

    if not nom:
        return safe_redirect("Nom de compte invalide")

    compte = Compte("Banque X", nom, 0)

    for cid in client_ids:
        cid = parse_int(cid)
        if cid in clients:
            clients[cid].ajouter_compte(compte)

    comptes[next_compte_id] = compte
    next_compte_id += 1

    return redirect("/saisie")

@app.route("/supprimer_compte/<int:id>")
def supprimer_compte(id):
    comptes.pop(id, None)
    return redirect("/saisie")

# Revenu
@app.route("/revenu", methods=["POST"])
def ajouter_revenu():

    client_id = parse_int(request.form.get("id_client"))
    compte_id = parse_int(request.form.get("id_compte"))

    if client_id not in clients or compte_id not in comptes:
        return safe_redirect("Client ou compte invalide")

    montant = parse_float(request.form.get("montant"))
    if montant is None or montant <= 0:
        return safe_redirect("Montant invalide")

    try:
        rev = Revenu(
            request.form.get("type_revenu"),
            montant,
            request.form.get("periodicite"),
            parse_int(request.form.get("jour")),
            parse_int(request.form.get("mois"))
        )
    except:
        return safe_redirect("Erreur revenu")

    rev.id_compte = compte_id
    clients[client_id].ajouter_revenu(rev)

    return redirect("/saisie")

@app.route("/supprimer_revenu/<int:id_client>/<int:item_id>")
def supprimer_revenu(id_client, item_id):
    client = clients.get(id_client)
    if not client:
        return redirect("/saisie")
    client.revenus = [r for r in client.revenus if id(r) != item_id]
    return redirect("/saisie")

# Depense
@app.route("/depense", methods=["POST"])
def ajouter_depense():

    client_id = parse_int(request.form.get("id_client"))
    compte_id = parse_int(request.form.get("id_compte"))

    if client_id not in clients or compte_id not in comptes:
        return safe_redirect("Client ou compte invalide")

    montant = parse_float(request.form.get("montant"))
    nom = parse_str(request.form.get("nom"))

    if not nom or montant is None or montant <= 0:
        return safe_redirect("Dépense invalide")

    try:
        dep = Depense(
            nom,
            montant,
            request.form.get("type_depense"),
            request.form.get("categorie_depense"),
            parse_int(request.form.get("jour")),
            parse_int(request.form.get("mois"))
        )
    except:
        return safe_redirect("Erreur dépense")

    dep.id_compte = compte_id
    clients[client_id].ajouter_depense(dep)

    return redirect("/saisie")

@app.route("/supprimer_depense/<int:id_client>/<int:item_id>")
def supprimer_depense(id_client, item_id):
    client = clients.get(id_client)
    if not client:
        return redirect("/saisie")
    client.depenses = [d for d in client.depenses if id(d) != item_id]
    return redirect("/saisie")

# Credit
@app.route("/credit", methods=["POST"])
def ajouter_credit():
    client_id = parse_int(request.form.get("id_client"))
    compte_id = parse_int(request.form.get("id_compte"))
    type_credit = parse_int(request.form.get("type_credit"))

    capital_emprunte = parse_float(request.form.get("capital_emprunte"))
    crd = parse_float(request.form.get("crd"))
    taux = parse_float(request.form.get("taux"))
    duree_initiale = parse_int(request.form.get("duree_initiale"))
    mensualite = parse_float(request.form.get("mensualite"))
    fin_credit = request.form.get("fin_credit")

    if None in (client_id, compte_id, type_credit, capital_emprunte, crd, taux, duree_initiale, mensualite):
        return safe_redirect("Erreur crédit")

    cr = Credit(type_credit, capital_emprunte, crd, taux, duree_initiale, mensualite, fin_credit)
    cr.id_compte = compte_id

    clients[client_id].ajouter_credit(cr)
    return redirect("/saisie")

@app.route("/supprimer_credit/<int:id_client>/<int:item_id>")
def supprimer_credit(id_client, item_id):
    client = clients.get(id_client)
    if not client:
        return redirect("/saisie")
    client.credits = [c for c in client.credits if id(c) != item_id]
    return redirect("/saisie")


# Epargne
@app.route("/epargne", methods=["POST"])
def ajouter_epargne():
    client_id = parse_int(request.form.get("id_client"))
    type_epargne = parse_int(request.form.get("type_epargne"))
    solde = parse_float(request.form.get("solde"), 0)
    versement = parse_float(request.form.get("versement_mensuel"), 0)
    taux = parse_float(request.form.get("taux"), 0)

    if client_id not in clients or type_epargne is None:
        return safe_redirect("Erreur épargne")

    e = Epargne(type_epargne, solde, versement, taux)
    clients[client_id].ajouter_epargne(e)
    return redirect("/saisie")

@app.route("/supprimer_epargne/<int:id_client>/<int:item_id>")
def supprimer_epargne(id_client, item_id):
    client = clients.get(id_client)
    if not client:
        return redirect("/saisie")
    client.epargnes = [e for e in client.epargnes if id(e) != item_id]
    return redirect("/saisie")


# Patrimoine
@app.route("/patrimoine", methods=["POST"])
def ajouter_patrimoine():

    client_id = parse_int(request.form.get("id_client"))
    revenu_id = parse_int(request.form.get("id_revenu"))
    credit_id = parse_int(request.form.get("id_credit"))

    type_patrimoine = parse_str(request.form.get("type_patrimoine"))
    nom = parse_str(request.form.get("nom"))
    valeur = parse_float(request.form.get("valeur"))
    part = parse_float(request.form.get("part"), 100)

    if client_id not in clients or valeur is None:
        return safe_redirect("Erreur patrimoine")

    revenu_associe = None
    if revenu_id:
        for r in clients[client_id].revenus:
            if id(r) == revenu_id:
                revenu_associe = r
                break

    credit_associe = None
    if credit_id:
        for c in clients[client_id].credits:
            if id(c) == credit_id:
                credit_associe = c
                break

    patrimoine = Patrimoine(
        type_patrimoine,
        nom,
        valeur,
        part,
        revenu=revenu_associe,
        credit=credit_associe
    )

    clients[client_id].ajouter_patrimoine(patrimoine)

    return redirect("/saisie")

@app.route("/supprimer_patrimoine/<int:id_client>/<int:item_id>")
def supprimer_patrimoine(id_client, item_id):
    client = clients.get(id_client)
    if not client:
        return redirect("/saisie")
    client.patrimoines = [p for p in client.patrimoines if id(p) != item_id]
    return redirect("/saisie")

# Tests dataframes
@app.route("/debug")
def debug():
    dfs = generate_df()
    html = ""
    for k,v in dfs.items():
        html += f"<h2>{k}</h2>"
        html += v.to_html()
        html += "<hr>"
    return html

if __name__ == "__main__":
    app.run(debug=True)