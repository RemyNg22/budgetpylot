from flask import Flask, render_template, request, redirect, flash
import pandas as pd
from datetime import datetime

from models.client import Client
from models.compte import Compte
from models.revenu import Revenu
from models.depense import Depense
from models.credit import Credit
from models.epargne import Epargne
from models.patrimoine import Patrimoine
from data.csv_manager import exporter_csv, importer_csv

app = Flask(__name__)
app.secret_key = "secret"

# Stockage en mémoire pour export CSV futur
clients = {}
comptes = {}

# Compteurs globaux
next_client_id = 0
next_compte_id = 0
next_item_id = 0

JOURS = list(range(1, 29))
MOIS = list(range(1, 13))

MOIS_NOMS = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}


# Utilitaires

def parse_int(value, default=None):
    try:
        if value in (None, ""):
            return default
        return int(value)
    except (ValueError, TypeError):
        return default



def parse_float(value, default=None):
    try:
        if value in (None, ""):
            return default
        if isinstance(value, str):
            value = value.replace(",", ".")
        return float(value)
    except (ValueError, TypeError):
        return default


def parse_str(value, default=""):
    return value.strip() if value else default


def safe_redirect(msg=None):
    if msg:
        flash(msg)
    return redirect("/saisie")


def next_id() -> int:
    global next_item_id
    next_item_id += 1
    return next_item_id



# DataFrames

def generate_df():
    """Crée des DataFrames temporaires pour affichage depuis les objets POO"""
    df_clients = pd.DataFrame([{"id": cid, "nom": c.nom} for cid, c in clients.items()])

    df_comptes = pd.DataFrame([
        {
            "id": cid,
            "nom_compte": c.nom_compte,
            "banque": c.banque,
            "solde_initial": c.solde_initial,
            "client_ids": c.client_ids,
            "est_joint": c.est_joint,
            "proprietaires": ", ".join(
                clients[i].nom for i in c.client_ids if i in clients
            ),
        }
        for cid, c in comptes.items()
    ])

    df_revenus = []
    df_depenses = []
    df_credits = []
    df_epargnes = []
    df_patrimoines = []

    for cid, client in clients.items():

        for r in client.revenus:
            df_revenus.append({
                "id": r.item_id,
                "type_revenu": r.type_de_revenu,
                "montant": r.montant,
                "periodicite": r.periodicite,
                "jour": r.jour,
                "mois": r.mois,
                "est_revenu_principal": r.est_revenu_principal,
                "id_client": cid,
                "id_compte": r.id_compte,
            })

        for d in client.depenses:
            df_depenses.append({
                "id": d.item_id,
                "nom": d.nom,
                "montant": d.montant,
                "type_depense": d.type_depense,
                "categorie_depense": d.categorie_depense,
                "jour": d.jour,
                "mois": d.mois,
                "id_client": cid,
                "id_compte": d.id_compte,
            })

        for cr in client.credits:
            df_credits.append({
                "id": cr.item_id,
                "type_credit": cr.nom,
                "capital_emprunte": cr.capital_emprunte,
                "crd": cr.crd,
                "taux": cr.taux,
                "duree_initiale": cr.duree_initiale,
                "mensualite": cr.mensualite,
                "fin_credit": cr.fin_credit.strftime("%d/%m/%Y"),
                "deja_preleve": cr.deja_preleve,
                "id_client": cid,
                "id_compte": cr.id_compte,
            })

        for e in client.epargnes:
            df_epargnes.append({
                "id": e.item_id,
                "type_epargne": e.nom,
                "solde": e.solde,
                "versement": e.versements_permanents,
                "taux": e.taux,
                "id_client": cid,
            })

        for p in client.patrimoines:
            df_patrimoines.append({
                "id": p.item_id,
                "type_patrimoine": p.type_patrimoine,
                "nom": p.nom,
                "valeur": p.valeur,
                "part": p.part,
                "credit": p.credit.nom if p.credit else None,
                "revenu": p.revenu.type_de_revenu if p.revenu else None,
                "id_client": cid,
            })

    return {
        "clients": df_clients,
        "comptes": df_comptes,
        "revenus": pd.DataFrame(df_revenus),
        "depenses": pd.DataFrame(df_depenses),
        "credits": pd.DataFrame(df_credits),
        "epargnes": pd.DataFrame(df_epargnes),
        "patrimoines": pd.DataFrame(df_patrimoines),
    }




# Routes

@app.route("/")
def index():
    return redirect("/saisie")


@app.route("/saisie")
def saisie():
    dfs = generate_df()
    client_names = {c["id"]: c["nom"] for c in dfs["clients"].to_dict(orient="records")}
    compte_names = {c["id"]: c["nom_compte"] for c in dfs["comptes"].to_dict(orient="records")}

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
        type_depense=Depense.TYPE_DEPENSE,
        categorie_depense=Depense.CATEGORIE_DEPENSE,
        type_credit={k: v["nom"] for k, v in Credit.REGLES_CREDIT.items()},
        type_epargne={k: v["nom"] for k, v in Epargne.TYPE_EPARGNE.items()},
        type_patrimoine=Patrimoine.TYPE_PATRIMOINE,
        jours=JOURS,
        mois=MOIS,
        mois_noms=MOIS_NOMS,
        client_names=client_names,
        compte_names=compte_names,
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


@app.route("/supprimer_client/<int:cid>")
def supprimer_client(cid):
    clients.pop(cid, None)
    return redirect("/saisie")


# Compte

@app.route("/compte", methods=["POST"])
def ajouter_compte():
    global next_compte_id
    nom = parse_str(request.form.get("new_compte"))
    banque = parse_str(request.form.get("banque"), "Banque X")
    client_ids = request.form.getlist("clients")

    if not nom:
        return safe_redirect("Nom de compte invalide")

    solde_initial = parse_float(request.form.get("solde_initial"), 0)
    compte = Compte(banque, nom, solde_initial)

    for cid_str in client_ids:
        cid = parse_int(cid_str)
        if cid in clients:
            compte.ajouter_proprietaire(cid)
            clients[cid].ajouter_compte(compte)

    comptes[next_compte_id] = compte
    next_compte_id += 1
    return redirect("/saisie")


@app.route("/supprimer_compte/<int:cid>")
def supprimer_compte(cid):
    comptes.pop(cid, None)
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

    est_principal = request.form.get("est_revenu_principal") == "on"

    try:
        rev = Revenu(
            type_de_revenu=request.form.get("type_revenu"),
            montant=montant,
            periodicite=request.form.get("periodicite"),
            jour=parse_int(request.form.get("jour")),
            mois=parse_int(request.form.get("mois")),
            id_compte=compte_id,
            est_revenu_principal=est_principal,
        )
    except ValueError as e:
        return safe_redirect(f"Erreur revenu : {e}")

    rev.item_id = next_id()
    clients[client_id].ajouter_revenu(rev)
    return redirect("/saisie")


@app.route("/supprimer_revenu/<int:id_client>/<int:item_id>")
def supprimer_revenu(id_client, item_id):
    client = clients.get(id_client)
    if client:
        client.revenus = [r for r in client.revenus if r.item_id != item_id]
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
            nom=nom,
            montant=montant,
            type_depense=request.form.get("type_depense"),
            categorie_depense=request.form.get("categorie_depense"),
            jour=parse_int(request.form.get("jour")),
            mois=parse_int(request.form.get("mois")),
            id_compte=compte_id,
        )
    except ValueError as e:
        return safe_redirect(f"Erreur dépense : {e}")

    dep.item_id = next_id()
    clients[client_id].ajouter_depense(dep)
    return redirect("/saisie")


@app.route("/supprimer_depense/<int:id_client>/<int:item_id>")
def supprimer_depense(id_client, item_id):
    client = clients.get(id_client)
    if client:
        client.depenses = [d for d in client.depenses if d.item_id != item_id]
    return redirect("/saisie")


# Credit

@app.route("/credit", methods=["POST"])
def ajouter_credit():
    compte_id = parse_int(request.form.get("id_compte"))
    type_credit = parse_int(request.form.get("type_credit"))
    capital_emprunte = parse_float(request.form.get("capital_emprunte"))
    crd = parse_float(request.form.get("crd"))
    taux = parse_float(request.form.get("taux"))
    duree_initiale = parse_int(request.form.get("duree_initiale"))
    mensualite = parse_float(request.form.get("mensualite"))
    fin_credit_str = request.form.get("fin_credit")
    jour_echeance = parse_int(request.form.get("jour_echeance"), 1)
    date_debut_str = request.form.get("date_debut")
    emprunteurs_ids = request.form.getlist("emprunteurs")
    parts_str = request.form.getlist("parts")

    if not date_debut_str:
        return safe_redirect("La date de début du crédit est obligatoire")

    try:
        date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d")
    except ValueError:
        return safe_redirect("Format date de début invalide")

    if compte_id not in comptes:
        return safe_redirect("Compte invalide")

    compte = comptes[compte_id]

    try:
        cr = Credit(
            type_de_credit=type_credit,
            capital_emprunte=capital_emprunte,
            crd=crd,
            taux=taux,
            duree_initiale=duree_initiale,
            mensualite=mensualite,
            fin_credit=fin_credit_str,
            jour_echeance=jour_echeance,
            compte=compte,
            id_compte=compte_id,
            deja_preleve=request.form.get("deja_preleve") == "on",
        )
    except (ValueError, TypeError) as e:
        return safe_redirect(f"Erreur création crédit : {e}")

    for cid_str, part_str in zip(emprunteurs_ids, parts_str):
        cid = parse_int(cid_str)
        part = (parse_float(part_str, 100) or 100) / 100
        if cid in clients:
            try:
                cr.ajouter_emprunteur(clients[cid], part)
            except ValueError as e:
                return safe_redirect(f"Erreur emprunteur : {e}")

    if cr.nombre_emprunteurs() == 0 and emprunteurs_ids:
        cid = parse_int(emprunteurs_ids[0])
        if cid in clients:
            cr.ajouter_emprunteur(clients[cid], 1.0)

    cr.item_id = next_id()

    for client in cr.emprunteur.keys():
        client.ajouter_credit(cr)

    return redirect("/saisie")


@app.route("/supprimer_credit/<int:id_client>/<int:item_id>")
def supprimer_credit(id_client, item_id):
    client = clients.get(id_client)
    if client:
        client.credits = [c for c in client.credits if c.item_id != item_id]
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

    try:
        e = Epargne(type_epargne, solde, versement, taux)
    except ValueError as e_err:
        return safe_redirect(f"Erreur épargne : {e_err}")

    e.item_id = next_id()
    clients[client_id].ajouter_epargne(e)
    return redirect("/saisie")


@app.route("/supprimer_epargne/<int:id_client>/<int:item_id>")
def supprimer_epargne(id_client, item_id):
    client = clients.get(id_client)
    if client:
        client.epargnes = [e for e in client.epargnes if e.item_id != item_id]
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

    client = clients[client_id]

    revenu_associe = next(
        (r for r in client.revenus if r.item_id == revenu_id), None
    ) if revenu_id else None

    credit_associe = next(
        (c for c in client.credits if c.item_id == credit_id), None
    ) if credit_id else None

    try:
        patrimoine = Patrimoine(
            type_patrimoine=type_patrimoine,
            nom=nom,
            valeur=valeur,
            part=part,
            revenu=revenu_associe,
            credit=credit_associe,
        )
    except ValueError as e:
        return safe_redirect(f"Erreur patrimoine : {e}")

    patrimoine.item_id = next_id()
    client.ajouter_patrimoine(patrimoine)
    return redirect("/saisie")


@app.route("/supprimer_patrimoine/<int:id_client>/<int:item_id>")
def supprimer_patrimoine(id_client, item_id):
    client = clients.get(id_client)
    if client:
        client.patrimoines = [p for p in client.patrimoines if p.item_id != item_id]
    return redirect("/saisie")


# Debug

@app.route("/debug")
def debug():
    dfs = generate_df()
    html = ""
    for k, v in dfs.items():
        html += f"<h2>{k}</h2>{v.to_html()}<hr>"
    return html


# Projection

@app.route("/projection/<int:id_compte>", methods=["GET"])
def projection(id_compte):
    compte = comptes.get(id_compte)
    if not compte:
        return safe_redirect("Compte introuvable")

    proprietaires = [clients[cid] for cid in compte.client_ids if cid in clients]
    if not proprietaires:
        return safe_redirect("Aucun propriétaire associé à ce compte")

    aujourd_hui = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    date_libre = None
    date_libre_str = request.args.get("date_libre")
    if date_libre_str:
        try:
            date_libre = datetime.strptime(date_libre_str, "%Y-%m-%d")
        except ValueError:
            flash("Format de date libre invalide (attendu : YYYY-MM-DD)")

    resultats = Client.projections(compte, id_compte, proprietaires, aujourd_hui, date_libre)

    return render_template(
        "projection.html",
        compte=compte,
        id_compte=id_compte,
        proprietaires=proprietaires,
        resultats=resultats,
        aujourd_hui=aujourd_hui,
        date_libre_str=date_libre_str or "",
    )

# Export / Import CSV
 
@app.route("/export_csv")
def export_csv():
    from flask import Response
    contenu = exporter_csv(clients, comptes)
    nom_fichier = f"budgetpylot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        contenu,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nom_fichier}"}
    )
 
 
@app.route("/import_csv", methods=["POST"])
def import_csv():
    global next_client_id, next_compte_id, next_item_id
 
    fichier = request.files.get("fichier_csv")
    if not fichier or fichier.filename == "":
        return safe_redirect("Aucun fichier sélectionné")
 
    try:
        contenu = fichier.read().decode("utf-8")
    except Exception as e:
        return safe_redirect(f"Erreur lecture fichier : {e}")
 
    ref_client = [next_client_id]
    ref_compte = [next_compte_id]
    ref_item = [next_item_id]
 
    try:
        importer_csv(contenu, clients, comptes, ref_client, ref_compte, ref_item)
    except Exception as e:
        return safe_redirect(f"Erreur import CSV : {e}")
 
    next_client_id = ref_client[0]
    next_compte_id = ref_compte[0]
    next_item_id = ref_item[0]
 
    flash("Données importées avec succès")
    return redirect("/saisie")

if __name__ == "__main__":
    app.run(debug=True)