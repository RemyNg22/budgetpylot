from flask import Flask, render_template, request, redirect, flash, session, Response
from datetime import timedelta
import pandas as pd
from datetime import datetime

from models.client import Client
from models.compte import Compte
from models.revenu import Revenu
from models.depense import Depense
from models.credit import Credit
from models.epargne import Epargne
from models.patrimoine import Patrimoine
from services.statistiques import synthese_complete, stats_foyer
from data.csv_manager import exporter_csv, importer_csv
from session_store import get_session_data

app = Flask(__name__)
app.secret_key = "la_cle_secrete_pour_le_dev_exemple_pour_git"
app.permanent_session_lifetime = timedelta(hours=4)
app.jinja_env.globals.update(enumerate=enumerate)

@app.before_request
def make_session_permanent():
    session.permanent = True

JOURS = list(range(1, 29))
MOIS = list(range(1, 13))
MOIS_NOMS = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
    5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
    9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
}
ETAPES = [{"num": 0, "titre": "Accueil", "template": "etape_accueil.html"},
    {"num": 1, "titre": "Personnes & Comptes", "template": "etape_clients_comptes.html"},
    {"num": 2, "titre": "Revenus", "template": "etape_revenus.html"},
    {"num": 3, "titre": "Dépenses","template": "etape_depenses.html"},
    {"num": 4, "titre": "Crédits", "template": "etape_credits.html"},
    {"num": 5, "titre": "Épargne","template": "etape_epargne.html"},
    {"num": 6, "titre": "Patrimoine", "template": "etape_patrimoine.html"},
    {"num": 7, "titre": "Synthèse","template": "etape_synthese.html"}]
NB_ETAPES = len(ETAPES)


# Utilitaires
def sd():
    """
    Retourne les données de session actuelles.
    
    Returns:
        SessionStore: objet contenant clients, comptes et identifiants.
    """
    return get_session_data()


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
    """
    Redirige vers une étape de saisie avec éventuellement un message flash.
    """
    if msg:
        flash(msg)
    etape = parse_int(request.args.get("redirect_etape"), 1)
    return redirect(f"/saisie?etape={etape}")

def redirect_etape(default: int = 1):
    """
    Redirection simple vers une étape spécifique de saisie.
    """
    etape = parse_int(request.args.get("redirect_etape"), default)
    return redirect(f"/saisie?etape={etape}")


# DataFrames

def generate_df():
    """Génère des DataFrames pandas pour toutes les entités de la session."""
    s = sd()
    clients = s.clients
    comptes = s.comptes

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

        seen_cr = set()
        for cr in client.credits:
            if id(cr) in seen_cr:
                continue
            seen_cr.add(id(cr))
            part_client = cr.emprunteur.get(client, 1.0)
            mensualite_client = round(cr.mensualite * part_client, 2)
            df_credits.append({
                "id": cr.item_id,
                "type_credit": cr.nom,
                "capital_emprunte": cr.capital_emprunte,
                "crd": cr.crd,
                "taux": cr.taux,
                "duree_initiale": cr.duree_initiale,
                "mensualite": cr.mensualite,
                "mensualite_client": mensualite_client,
                "part_client": round(part_client * 100, 1),
                "fin_credit": cr.fin_credit.strftime("%d/%m/%Y") if cr.fin_credit else None,
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
                "nb_versements_ponctuels": len(e.versements_ponctuels),
                "versements_ponctuels": [
                    {"montant": vp.montant, "jour": vp.jour, "mois": vp.mois, "index": i}
                    for i, vp in enumerate(e.versements_ponctuels)
                ],
                "id_client": cid,
            })

        for p in client.patrimoines:
            df_patrimoines.append({
                "id": p.item_id,
                "type_patrimoine": p.type_patrimoine,
                "nom": p.nom,
                "valeur": p.valeur,
                "part": p.part,
                "credits": [{"id": cr.item_id, "nom": cr.nom} for cr in p.credits],
                "revenus": [{"id": r.item_id, "type": r.type_de_revenu, "montant": r.montant} for r in p.revenus],
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
    return redirect("/saisie?etape=0")


@app.route("/saisie")
def saisie():
    s = sd()
    etape = parse_int(request.args.get("etape"), 0)
    etape = max(0, min(etape, NB_ETAPES - 1))
    info_etape = ETAPES[etape]
    dfs = generate_df()
    client_names = {c["id"]: c["nom"] for c in dfs["clients"].to_dict(orient="records")}
    compte_names = {c["id"]: c["nom_compte"] for c in dfs["comptes"].to_dict(orient="records")}

    params = dict(
        etape=etape,
        etapes=ETAPES,
        nb_etapes=NB_ETAPES,
        etape_precedente=etape - 1 if etape > 0 else None,
        etape_suivante=etape + 1 if etape < NB_ETAPES - 1 else None,
        clients=dfs["clients"].to_dict(orient="records"),
        comptes=dfs["comptes"].to_dict(orient="records"),
        revenus=dfs["revenus"].to_dict(orient="records"),
        depenses=dfs["depenses"].to_dict(orient="records"),
        credits=dfs["credits"].to_dict(orient="records"),
        epargnes=dfs["epargnes"].to_dict(orient="records"),
        patrimoines=dfs["patrimoines"].to_dict(orient="records"),
        client_names=client_names,
        compte_names=compte_names,
        type_revenu=Revenu.TYPE_REVENU,
        type_depense=Depense.TYPE_DEPENSE,
        categorie_depense=Depense.CATEGORIE_DEPENSE,
        type_credit={k: v["nom"] for k, v in Credit.REGLES_CREDIT.items()},
        type_epargne={k: v["nom"] for k, v in Epargne.TYPE_EPARGNE.items()},
        type_patrimoine=Patrimoine.TYPE_PATRIMOINE,
        jours=JOURS,
        mois=MOIS,
        mois_noms=MOIS_NOMS,
        mois_actuel=datetime.now().month,
        annee_actuelle=datetime.now().year,
        tous_clients=s.clients,
        ids_selectionnes=[],
    )
    return render_template(info_etape["template"], **params)

# Client

@app.route("/client", methods=["POST"])
def ajouter_client():
    s = sd()
    nom = parse_str(request.form.get("nom"))
    if not nom:
        return safe_redirect("Nom invalide")
    s.clients[s.next_client_id] = Client(nom)
    s.next_client_id += 1
    return redirect_etape()


@app.route("/supprimer_client/<int:cid>")
def supprimer_client(cid):
    s = sd()
    s.clients.pop(cid, None)
    return redirect_etape()


# Compte

@app.route("/compte", methods=["POST"])
def ajouter_compte():
    s = sd()
    nom = parse_str(request.form.get("new_compte"))
    banque = parse_str(request.form.get("banque"), "Banque X")
    client_ids = request.form.getlist("clients")
    if not nom:
        return safe_redirect("Nom de compte invalide")
    solde_initial = parse_float(request.form.get("solde_initial"), 0)
    compte = Compte(banque, nom, solde_initial)
    for cid_str in client_ids:
        cid = parse_int(cid_str)
        if cid in s.clients:
            compte.ajouter_proprietaire(cid)
            s.clients[cid].ajouter_compte(compte)
    s.comptes[s.next_compte_id] = compte
    s.next_compte_id += 1
    return redirect_etape()


@app.route("/supprimer_compte/<int:cid>")
def supprimer_compte(cid):
    s = sd()
    s.comptes.pop(cid, None)
    return redirect_etape()


# Revenu

@app.route("/revenu", methods=["POST"])
def ajouter_revenu():
    s = sd()
    client_id = parse_int(request.form.get("id_client"))
    compte_id = parse_int(request.form.get("id_compte"))
    if client_id not in s.clients or compte_id not in s.comptes:
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
    rev.item_id = s.next_id()
    s.clients[client_id].ajouter_revenu(rev)
    return redirect_etape()


@app.route("/supprimer_revenu/<int:id_client>/<int:item_id>")
def supprimer_revenu(id_client, item_id):
    s = sd()
    client = s.clients.get(id_client)
    if client:
        client.revenus = [r for r in client.revenus if r.item_id != item_id]
    return redirect_etape()


# Depense

@app.route("/depense", methods=["POST"])
def ajouter_depense():
    s = sd()
    client_id = parse_int(request.form.get("id_client"))
    compte_id = parse_int(request.form.get("id_compte"))
    if client_id not in s.clients or compte_id not in s.comptes:
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
    dep.item_id = s.next_id()
    s.clients[client_id].ajouter_depense(dep)
    return redirect_etape()


@app.route("/supprimer_depense/<int:id_client>/<int:item_id>")
def supprimer_depense(id_client, item_id):
    s = sd()
    client = s.clients.get(id_client)
    if client:
        client.depenses = [d for d in client.depenses if d.item_id != item_id]
    return redirect_etape()


# Credit

@app.route("/credit", methods=["POST"])
def ajouter_credit():
    s = sd()
    compte_id = parse_int(request.form.get("id_compte"))
    type_credit = parse_int(request.form.get("type_credit"))
    mensualite = parse_float(request.form.get("mensualite"))
    jour_echeance = parse_int(request.form.get("jour_echeance"), 1)
    emprunteurs_ids = request.form.getlist("emprunteurs")
    parts_str = request.form.getlist("parts")

    if mensualite is None or mensualite <= 0:
        return safe_redirect("La mensualité est obligatoire et doit être positive")
    if not jour_echeance or not (1 <= jour_echeance <= 28):
        return safe_redirect("Le jour d'échéance est obligatoire (entre 1 et 28)")
    if compte_id not in s.comptes:
        return safe_redirect("Compte invalide")

    capital_emprunte = parse_float(request.form.get("capital_emprunte"))
    crd = parse_float(request.form.get("crd"))
    taux = parse_float(request.form.get("taux"))
    duree_initiale = parse_int(request.form.get("duree_initiale"))
    fin_credit_str = request.form.get("fin_credit") or None
    compte = s.comptes[compte_id]

    try:
        cr = Credit(
            type_de_credit=type_credit,
            mensualite=mensualite,
            jour_echeance=jour_echeance,
            capital_emprunte=capital_emprunte,
            crd=crd,
            taux=taux,
            duree_initiale=duree_initiale,
            fin_credit=fin_credit_str,
            compte=compte,
            id_compte=compte_id,
            deja_preleve=request.form.get("deja_preleve") == "on",
        )
    except (ValueError, TypeError) as e:
        return safe_redirect(f"Erreur création crédit : {e}")

    for cid_str, part_str in zip(emprunteurs_ids, parts_str):
        cid = parse_int(cid_str)
        part = (parse_float(part_str, 100) or 100) / 100
        if cid in s.clients:
            try:
                cr.ajouter_emprunteur(s.clients[cid], part)
            except ValueError as e:
                return safe_redirect(f"Erreur emprunteur : {e}")

    if cr.nombre_emprunteurs() == 0 and emprunteurs_ids:
        cid = parse_int(emprunteurs_ids[0])
        if cid in s.clients:
            cr.ajouter_emprunteur(s.clients[cid], 1.0)

    cr.item_id = s.next_id()
    for client in cr.emprunteur.keys():
        client.attacher_credit(cr)
    return redirect_etape()


@app.route("/supprimer_credit/<int:id_client>/<int:item_id>")
def supprimer_credit(id_client, item_id):
    s = sd()
    client = s.clients.get(id_client)
    if client:
        client.credits = [c for c in client.credits if c.item_id != item_id]
    return redirect_etape()


# Epargne

@app.route("/epargne", methods=["POST"])
def ajouter_epargne():
    s = sd()
    client_id = parse_int(request.form.get("id_client"))
    type_epargne = parse_int(request.form.get("type_epargne"))
    solde = parse_float(request.form.get("solde"), 0)
    versement = parse_float(request.form.get("versement_mensuel"), 0)
    taux = parse_float(request.form.get("taux"), 0)
    if client_id not in s.clients or type_epargne is None:
        return safe_redirect("Erreur épargne")
    try:
        e = Epargne(type_epargne, solde, versement, taux)
    except ValueError as e_err:
        return safe_redirect(f"Erreur épargne : {e_err}")
    e.item_id = s.next_id()
    s.clients[client_id].ajouter_epargne(e)
    return redirect_etape()


@app.route("/supprimer_epargne/<int:id_client>/<int:item_id>")
def supprimer_epargne(id_client, item_id):
    s = sd()
    client = s.clients.get(id_client)
    if client:
        client.epargnes = [e for e in client.epargnes if e.item_id != item_id]
    return redirect_etape()


@app.route("/epargne_versement_ponctuel/<int:id_client>/<int:epargne_id>", methods=["POST"])
def ajouter_versement_ponctuel(id_client, epargne_id):
    s = sd()
    client = s.clients.get(id_client)
    if not client:
        return safe_redirect("Client introuvable")
    epargne = next((e for e in client.epargnes if e.item_id == epargne_id), None)
    if not epargne:
        return safe_redirect("Epargne introuvable")
    montant = parse_float(request.form.get("vp_montant"))
    jour = parse_int(request.form.get("vp_jour"))
    mois = parse_int(request.form.get("vp_mois"))
    if not montant or not jour or not mois:
        return safe_redirect("Versement ponctuel : tous les champs sont obligatoires")
    try:
        epargne.ajouter_versement_ponctuel(montant, jour, mois)
    except ValueError as e:
        return safe_redirect(f"Erreur versement ponctuel : {e}")
    return redirect_etape()


@app.route("/supprimer_versement_ponctuel/<int:id_client>/<int:epargne_id>/<int:vp_index>")
def supprimer_versement_ponctuel(id_client, epargne_id, vp_index):
    s = sd()
    client = s.clients.get(id_client)
    if not client:
        return safe_redirect("Client introuvable")
    epargne = next((e for e in client.epargnes if e.item_id == epargne_id), None)
    if not epargne:
        return safe_redirect("Epargne introuvable")
    if 0 <= vp_index < len(epargne.versements_ponctuels):
        epargne.versements_ponctuels.pop(vp_index)
    return redirect_etape()


# Patrimoine

@app.route("/patrimoine", methods=["POST"])
def ajouter_patrimoine():
    s = sd()
    client_id = parse_int(request.form.get("id_client"))
    revenu_ids = request.form.getlist("id_revenus")
    credit_ids = request.form.getlist("id_credits")
    type_patrimoine = parse_str(request.form.get("type_patrimoine"))
    nom = parse_str(request.form.get("nom"))
    valeur = parse_float(request.form.get("valeur"))
    part = parse_float(request.form.get("part"), 100)
    if client_id not in s.clients or valeur is None:
        return safe_redirect("Erreur patrimoine")
    client = s.clients[client_id]

    tous_revenus = []
    seen_r = set()
    for c in s.clients.values():
        for r in c.revenus:
            if id(r) not in seen_r:
                seen_r.add(id(r))
                tous_revenus.append(r)

    revenus_associes = [
        rv for rv in tous_revenus
        if rv.item_id in [parse_int(x) for x in revenu_ids]
    ]

    tous_credits = []
    seen_c = set()
    for c in s.clients.values():
        for cr in c.credits:
            if id(cr) not in seen_c:
                seen_c.add(id(cr))
                tous_credits.append(cr)

    credits_associes = [
        cr for cr in tous_credits
        if cr.item_id in [parse_int(x) for x in credit_ids]
    ]

    try:
        patrimoine = Patrimoine(
            type_patrimoine=type_patrimoine,
            nom=nom,
            valeur=valeur,
            part=part,
            revenus=revenus_associes,
            credits=credits_associes,
        )
    except ValueError as e:
        return safe_redirect(f"Erreur patrimoine : {e}")
    patrimoine.item_id = s.next_id()
    client.ajouter_patrimoine(patrimoine)
    return redirect_etape()


@app.route("/supprimer_patrimoine/<int:id_client>/<int:item_id>")
def supprimer_patrimoine(id_client, item_id):
    s = sd()
    client = s.clients.get(id_client)
    if client:
        client.patrimoines = [p for p in client.patrimoines if p.item_id != item_id]
    return redirect_etape()

"""
# Debug

@app.route("/debug")
def debug():
    dfs = generate_df()
    html = ""
    for k, v in dfs.items():
        html += f"<h2>{k}</h2>{v.to_html()}<hr>"
    return html
"""

# Projection
@app.route("/projection/<int:id_compte>", methods=["GET"])
def projection(id_compte):
    s = sd()
    compte = s.comptes.get(id_compte)
    if not compte:
        return safe_redirect("Compte introuvable")
    proprietaires = [s.clients[cid] for cid in compte.client_ids if cid in s.clients]
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
    ids_proprietaires = [cid for cid in compte.client_ids if cid in s.clients]
    url_retour = request.referrer or "/saisie?etape=7"
    return render_template(
        "projection.html",
        compte=compte,
        id_compte=id_compte,
        proprietaires=proprietaires,
        resultats=resultats,
        aujourd_hui=aujourd_hui,
        date_libre_str=date_libre_str or "",
        ids_proprietaires=ids_proprietaires,
        url_retour=url_retour,
    )


# Statistiques

@app.route("/stats")
def stats():
    s = sd()
    ids = request.args.getlist("clients")
    if not ids:
        return safe_redirect("Aucun client sélectionné")
    liste_clients = [s.clients[parse_int(i)] for i in ids if parse_int(i) in s.clients]
    if not liste_clients:
        return safe_redirect("Clients introuvables")
    mois = parse_int(request.args.get("mois"), datetime.now().month)
    annee = parse_int(request.args.get("annee"), datetime.now().year)
    nb_mois_libre = parse_int(request.args.get("nb_mois_epargne"), None)
    synthese = synthese_complete(liste_clients, s.comptes, mois, annee, nb_mois_libre)
    return render_template(
        "stats.html",
        liste_clients=liste_clients,
        tous_clients=s.clients,
        ids_selectionnes=[parse_int(i) for i in ids],
        synthese=synthese,
        mois=mois,
        annee=annee,
        mois_noms=MOIS_NOMS,
        nb_mois_epargne=nb_mois_libre or 12,
    )


# Export / Import CSV
@app.route("/export_csv")
def export_csv():
    s = sd()
    contenu = exporter_csv(s.clients, s.comptes)
    nom_fichier = f"budgetpylot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        contenu,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nom_fichier}"}
    )


@app.route("/import_csv", methods=["POST"])
def import_csv():
    s = sd()
    fichier = request.files.get("fichier_csv")
    if not fichier or fichier.filename == "":
        return safe_redirect("Aucun fichier sélectionné")
    try:
        contenu = fichier.read().decode("utf-8")
    except Exception as e:
        return safe_redirect(f"Erreur lecture fichier : {e}")
    ref_client = [s.next_client_id]
    ref_compte = [s.next_compte_id]
    ref_item = [s.next_item_id]
    try:
        importer_csv(contenu, s.clients, s.comptes, ref_client, ref_compte, ref_item)
    except Exception as e:
        return safe_redirect(f"Erreur import CSV : {e}")
    s.next_client_id = ref_client[0]
    s.next_compte_id = ref_compte[0]
    s.next_item_id = ref_item[0]
    flash("Données importées avec succès")
    return redirect("/saisie?etape=1")

# Reset

@app.route("/reset")
def reset():
    s = sd()
    s.reset()
    flash("Données réinitialisées")
    return redirect("/saisie?etape=0")


# A propos

@app.route("/apropos")
def apropos():
    return render_template("apropos.html")


if __name__ == "__main__":
    app.run(debug=True)