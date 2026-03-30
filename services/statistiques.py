"""
Calculs statistiques et financiers sur un ou plusieurs clients.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
from models.client import Client

SEGMENTS_CAMEMBERT = {
    "Loyer": "Loyer",
    "Charge immobilière (hors crédit)": "Loyer",
    "Assurance habitation": "Assurances",
    "Assurance automobile": "Assurances",
    "Assurance santé": "Assurances",
    "Autre assurance": "Assurances",
    "Electricité": "Energie",
    "Gaz": "Energie",
    "Autre énergie": "Energie",
    "Box internet": "Numérique",
    "Forfait mobile": "Numérique",
    "Abonnement numérique": "Numérique",
    "Impôts et taxes": "Impôts",
    "Alimentation": "Dépenses courantes",
    "Transport": "Transport",
    "Habillement": "Loisirs",
    "Frais de santé": "Santé",
    "Loisir": "Loisirs",
    "Vacances": "Loisirs",
    "Autre (hors crédit, LLD, LOA)": "Autre",
}


# Budget mensuel

def stats_budget(clients: list, mois: int, annee: int) -> dict:

    revenus_detail = []
    total_revenus_mois = 0.0
    total_revenus_annualises = 0.0

    for client in clients:
        for r in client.revenus:
            montant = r.montant_pour_mois(mois)
            if montant > 0:
                revenus_detail.append({
                    "client": client.nom,
                    "type": r.type_de_revenu,
                    "montant": montant,
                    "periodicite": r.periodicite,
                    "principal": r.est_revenu_principal,
                })
                total_revenus_mois += montant
            if r.periodicite == "mensuelle":
                total_revenus_annualises += r.montant * 12
            elif r.periodicite == "annuelle":
                total_revenus_annualises += r.montant

    revenus_mensuels_moyens = round(total_revenus_annualises / 12, 2)

    depenses_detail = []
    total_depenses = 0.0
    total_fixes = 0.0
    total_variables = 0.0
    total_uniques = 0.0
    depenses_par_categorie: dict[str, float] = {}

    for client in clients:
        for d in client.depenses:
            if not d.est_a_appliquer(mois):
                continue
            depenses_detail.append({
                "client": client.nom,
                "nom": d.nom,
                "montant": d.montant,
                "type": d.type_depense,
                "categorie": d.categorie_depense,
                "jour": d.jour,
            })
            total_depenses += d.montant
            depenses_par_categorie[d.categorie_depense] = (
                depenses_par_categorie.get(d.categorie_depense, 0) + d.montant
            )
            if d.type_depense == "fixe":
                total_fixes += d.montant
            elif d.type_depense == "variable_mensuelle":
                total_variables += d.montant
            else:
                total_uniques += d.montant

    # Crédits
    # La mensualité est pondérée par la part de chaque client sélectionné.
    seen_credits = set()
    credits_detail = []
    total_mensualites = 0.0
    for client in clients:
        for cr in client.credits:
            if id(cr) in seen_credits:
                continue
            seen_credits.add(id(cr))
            m = sum(
                cr.mensualite_client(c)
                for c in clients
                if c in cr.emprunteur
            )
            total_mensualites += m
            credits_detail.append({
                "client": ", ".join(c.nom for c in clients if c in cr.emprunteur),
                "nom": cr.nom,
                "mensualite": round(m, 2),
                "taux": cr.taux,
                "crd": cr.crd,
            })

    total_epargne_mois = 0.0
    for client in clients:
        for e in client.epargnes:
            total_epargne_mois += e.total_versements_mois(mois)

    total_charges = total_depenses + total_mensualites
    solde_mensuel = total_revenus_mois - total_charges
    reste_a_vivre = total_revenus_mois - total_fixes - total_mensualites

    taux_effort_epargne = (
        round(total_epargne_mois / total_revenus_mois * 100, 2)
        if total_revenus_mois > 0 else 0.0
    )

    capacite_epargne_mensuelle = round(reste_a_vivre - total_variables, 2)

    segments: dict[str, float] = {
        "Loyer": 0.0, "Assurances": 0.0, "Energie": 0.0, "Numérique": 0.0,
        "Impôts": 0.0, "Dépenses courantes": 0.0, "Transport": 0.0,
        "Santé": 0.0, "Loisirs": 0.0, "Autre": 0.0,
        "Epargne": round(total_epargne_mois, 2),
        "Crédits": round(total_mensualites, 2),
    }
    for cat, montant in depenses_par_categorie.items():
        segment = SEGMENTS_CAMEMBERT.get(cat, "Autre")
        segments[segment] = round(segments[segment] + montant, 2)

    return {
        "mois": mois,
        "annee": annee,
        "revenus_detail": revenus_detail,
        "total_revenus_mois": round(total_revenus_mois, 2),
        "revenus_mensuels_moyens": revenus_mensuels_moyens,
        "total_revenus_annualises": round(total_revenus_annualises, 2),
        "depenses_detail": depenses_detail,
        "total_depenses": round(total_depenses, 2),
        "total_fixes": round(total_fixes, 2),
        "total_variables": round(total_variables, 2),
        "total_uniques": round(total_uniques, 2),
        "depenses_par_categorie": {k: round(v, 2) for k, v in depenses_par_categorie.items()},
        "credits_detail": credits_detail,
        "total_mensualites": round(total_mensualites, 2),
        "total_charges": round(total_charges, 2),
        "total_epargne_mois": round(total_epargne_mois, 2),
        "taux_effort_epargne": taux_effort_epargne,
        "solde_mensuel": round(solde_mensuel, 2),
        "reste_a_vivre": round(reste_a_vivre, 2),
        "capacite_epargne_mensuelle": capacite_epargne_mensuelle,
        "segments_camembert": {k: v for k, v in segments.items() if v > 0},
    }


# Comptes et projections
def stats_comptes(clients: list, comptes_dict: dict, compte_ids: list) -> dict:
    from models.client import Client as ClientModel
    aujourd_hui = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    detail_comptes = []

    for compte_id in compte_ids:
        compte = comptes_dict.get(compte_id)
        if not compte:
            continue

        proprietaires_compte = clients

        fin_mois = ClientModel.solde_fin_de_mois(
            compte, compte_id, proprietaires_compte, aujourd_hui
        )
        solde_sal, rev_principal, date_sal = ClientModel.solde_prochain_salaire(
            compte, compte_id, proprietaires_compte, aujourd_hui
        )

        evolution_12_mois = []
        for i in range(12):
            date_fin = aujourd_hui + relativedelta(months=i + 1)
            date_fin = (date_fin.replace(day=1)
                        + relativedelta(months=1)
                        - relativedelta(days=1))
            solde_proj = ClientModel.projeter_solde_compte(
                compte, compte_id, proprietaires_compte, aujourd_hui, date_fin
            )
            evolution_12_mois.append({
                "mois": (aujourd_hui + relativedelta(months=i + 1)).strftime("%b %Y"),
                "solde": solde_proj,
            })

        detail_comptes.append({
            "id": compte_id,
            "nom": compte.nom_compte,
            "banque": compte.banque,
            "est_joint": compte.est_joint,
            "solde_actuel": compte.solde_initial,
            "solde_fin_mois": fin_mois,
            "solde_prochain_salaire": solde_sal,
            "date_prochain_salaire": date_sal.strftime("%d/%m/%Y") if date_sal else None,
            "revenu_principal": rev_principal.type_de_revenu if rev_principal else None,
            "evolution_12_mois": evolution_12_mois,
        })

    return {"comptes": detail_comptes}

# Pondération bancaire des revenus
PONDERATION_REVENUS = {
    "Salaire": 1.00,
    "Prime fixe": 0.50,
    "Bonus":0.00,
    "Revenu non salarié":1.00,
    "Allocations chômage":  0.00,
    "Pension d'invalidité":0.00,
    "Retraite": 1.00,
    "RSA": 0.00,
    "APL": 0.00,
    "Allocations familiales": 0.50,
    "Prime d'activité": 0.00,
    "Bourse étudiante":0.00,
    "Revenu locatif": 0.70,
    "Revenu SCPI": 0.70,
    "Intérêt d'épargne": 0.50,
    "Coupon obligataire": 0.00,
    "Héritage":0.00,
    "Donation":0.00,
    "Gain exceptionnel": 0.00,
    "Vente d'actifs": 0.00,
    "Indemnité":0.00,
    "Virement reçu": 0.00,
    "Remboursement": 0.00,
    "Autre": 0.00,
}


def _revenus_ponderes_mensuels(client: Client) -> tuple[float, list]:
    """Revenus mensuels pondérés selon la grille bancaire."""
    total = 0.0
    detail = []
    for r in client.revenus:
        coeff = PONDERATION_REVENUS.get(r.type_de_revenu, 0.0)
        if coeff == 0.0:
            continue
        if r.periodicite == "mensuelle":
            montant_mensuel = r.montant
        elif r.periodicite == "annuelle":
            montant_mensuel = r.montant / 12
        else:
            continue
        montant_pondere = montant_mensuel * coeff
        total += montant_pondere
        detail.append({
            "client": client.nom,
            "type": r.type_de_revenu,
            "montant_brut": round(montant_mensuel, 2),
            "coefficient": coeff,
            "montant_pondere": round(montant_pondere, 2),
        })
    return round(total, 2), detail


def _charges_endettement(client: Client) -> float:
    """Charges bancaires : loyers + impôts + mensualités crédits (pondérées)."""
    charges = 0.0
    for d in client.depenses:
        if d.categorie_depense == "Loyer":
            charges += d.montant
        elif d.categorie_depense == "Impôts et taxes":
            charges += d.montant
    for cr in client.credits:
        if client in cr.emprunteur:
            charges += cr.mensualite_client(client)
    return round(charges, 2)


def _charges_capacite(client: Client, inclure_loyer: bool) -> float:
    charges = 0.0
    for d in client.depenses:
        if d.categorie_depense == "Impôts et taxes":
            charges += d.montant
        if inclure_loyer and d.categorie_depense in ("Loyer"):
            charges += d.montant
    for cr in client.credits:
        if client in cr.emprunteur:
            charges += cr.mensualite_client(client)
    return round(charges, 2)


# Endettement individuel
def stats_endettement(client: Client) -> dict:
    """Taux d'endettement bancaire. Seuil HCSF 35%."""
    revenus_ponderes, detail_revenus = _revenus_ponderes_mensuels(client)
    charges = _charges_endettement(client)

    taux_endettement = (charges / revenus_ponderes * 100) if revenus_ponderes > 0 else 0.0

    crd_total = sum(cr.crd for cr in client.credits if cr.crd is not None)

    aujourd_hui = datetime.now()
    detail_credits = []
    for cr in client.credits:
        part_client = cr.emprunteur.get(client, 1.0)
        mensualite_part = cr.mensualite_client(client)
        mois_restants = None
        cout_restant = None
        if cr.fin_credit is not None:
            delta = cr.fin_credit - aujourd_hui
            mois_restants = max(0, round(delta.days / 30.44))
            if cr.crd is not None:
                cout_restant = round(
                    max(0, mensualite_part * mois_restants - cr.crd * part_client), 2
                )
        detail_credits.append({
            "nom": cr.nom,
            "mensualite": round(mensualite_part, 2),
            "crd": round(cr.crd, 2) if cr.crd is not None else None,
            "taux": cr.taux,
            "fin_credit": cr.fin_credit.strftime("%d/%m/%Y") if cr.fin_credit else None,
            "part": round(part_client * 100, 1),
            "mois_restants": mois_restants,
            "cout_total_restant": cout_restant,
        })

    cout_total_global = sum(
        d["cout_total_restant"] for d in detail_credits if d["cout_total_restant"] is not None
    )

    return {
        "mode": "individuel",
        "revenus_ponderes": revenus_ponderes,
        "detail_revenus_ponderes": detail_revenus,
        "charges_retenues": charges,
        "taux_endettement": round(taux_endettement, 2),
        "seuil_legal": 35.0,
        "alerte": taux_endettement > 35.0,
        "crd_total": round(crd_total, 2),
        "detail_credits": detail_credits,
        "nb_credits": len(client.credits),
        "cout_total_global": round(cout_total_global, 2),
    }


# Endettement foyer 
def stats_endettement_foyer(clients: list) -> dict:
    """
    Taux d'endettement agrégé pour un foyer (plusieurs clients sélectionnés).
    Revenus : somme des revenus pondérés de chaque client.
    Charges : somme des charges bancaires de chaque client (crédits dédupliqués par part).
    """
    total_revenus = 0.0
    detail_revenus = []

    for c in clients:
        rev, det = _revenus_ponderes_mensuels(c)
        total_revenus += rev
        detail_revenus.extend(det)  # client est déjà dans chaque ligne

    # Charges foyer : loyers + impôts + crédits (pondérés par part, dédupliqués)
    total_charges = 0.0
    charges_loyer_impots = 0.0
    charges_credits = 0.0

    # Loyers et impôts : somme directe par client (pas de doublon possible)
    seen_depenses = set()
    for c in clients:
        for d in c.depenses:
            if id(d) not in seen_depenses:
                seen_depenses.add(id(d))
                if d.categorie_depense in ("Loyer", "Impôts et taxes"):
                    charges_loyer_impots += d.montant

    # Crédits : mensualité × part de chaque client sélectionné (dédupliqués)
    seen_credits = set()
    detail_credits = []
    aujourd_hui = datetime.now()
    crd_total = 0.0
    cout_total_global = 0.0

    for c in clients:
        for cr in c.credits:
            if id(cr) in seen_credits:
                continue
            seen_credits.add(id(cr))

            # Mensualité = somme des parts des clients sélectionnés
            m = sum(
                cr.mensualite_client(cl)
                for cl in clients
                if cl in cr.emprunteur
            )
            charges_credits += m

            if cr.crd is not None:
                crd_total += cr.crd

            part_affichee = sum(
                cr.emprunteur.get(cl, 0) for cl in clients if cl in cr.emprunteur
            )
            mois_restants = None
            cout_restant = None
            if cr.fin_credit is not None:
                mois_restants = max(0, round((cr.fin_credit - aujourd_hui).days / 30.44))
                if cr.crd is not None:
                    cout_restant = round(max(0, m * mois_restants - cr.crd * part_affichee), 2)
                    cout_total_global += cout_restant

            detail_credits.append({
                "nom": cr.nom,
                "mensualite": round(m, 2),
                "crd": round(cr.crd, 2) if cr.crd is not None else None,
                "taux": cr.taux,
                "fin_credit": cr.fin_credit.strftime("%d/%m/%Y") if cr.fin_credit else None,
                "part": round(part_affichee * 100, 1),
                "mois_restants": mois_restants,
                "cout_total_restant": cout_restant,
            })

    total_charges = round(charges_loyer_impots + charges_credits, 2)
    taux = (total_charges / total_revenus * 100) if total_revenus > 0 else 0.0

    return {
        "mode": "foyer",
        "noms": [c.nom for c in clients],
        "revenus_ponderes": round(total_revenus, 2),
        "detail_revenus_ponderes": detail_revenus,
        "charges_retenues": total_charges,
        "taux_endettement": round(taux, 2),
        "seuil_legal": 35.0,
        "alerte": taux > 35.0,
        "crd_total": round(crd_total, 2),
        "detail_credits": detail_credits,
        "nb_credits": len(detail_credits),
        "cout_total_global": round(cout_total_global, 2),
    }


# Capacité d'emprunt

def _calculer_capital(mensualite_max: float, taux_annuel: float, nb_ans: int) -> float:
    taux_mensuel = taux_annuel / 100 / 12
    n = nb_ans * 12
    if mensualite_max <= 0:
        return 0.0
    if taux_mensuel == 0:
        return mensualite_max * n
    return mensualite_max * (1 - (1 + taux_mensuel) ** -n) / taux_mensuel


def _resultats_capacite(revenus_ponderes, charges_sans_loyer, charges_avec_loyer, taux_data):
    """Calcule les résultats capacité pour les deux durées et deux scénarios."""
    mensualite_dispo_sans_loyer = round(max(0, revenus_ponderes * 0.35 - charges_sans_loyer), 2)
    mensualite_dispo_avec_loyer = round(max(0, revenus_ponderes * 0.35 - charges_avec_loyer), 2)

    resultats = {}
    for duree_label, nb_ans in [("20_ans", 20), ("25_ans", 25)]:
        info_taux = taux_data[duree_label]
        taux_annuel = info_taux["taux"]
        resultats[duree_label] = {
            "nb_ans": nb_ans,
            "taux": taux_annuel,
            "source_taux": info_taux["source"],
            "mise_a_jour_taux": info_taux["mise_a_jour"],
            "sans_loyer": {
                "mensualite_dispo": mensualite_dispo_sans_loyer,
                "capital_empruntable": round(_calculer_capital(mensualite_dispo_sans_loyer, taux_annuel, nb_ans), 2),
            },
            "avec_loyer": {
                "mensualite_dispo": mensualite_dispo_avec_loyer,
                "capital_empruntable": round(_calculer_capital(mensualite_dispo_avec_loyer, taux_annuel, nb_ans), 2),
            },
        }
    return resultats, mensualite_dispo_sans_loyer, mensualite_dispo_avec_loyer


def stats_capacite_emprunt(client: Client) -> dict:
    from services.taux_manager import get_tous_les_taux
    revenus_ponderes, detail_revenus = _revenus_ponderes_mensuels(client)
    charges_sans_loyer = _charges_capacite(client, inclure_loyer=False)
    charges_avec_loyer = _charges_capacite(client, inclure_loyer=True)
    taux_data = get_tous_les_taux()
    resultats, m_sans, m_avec = _resultats_capacite(
        revenus_ponderes, charges_sans_loyer, charges_avec_loyer, taux_data
    )
    return {
        "mode": "individuel",
        "revenus_ponderes": revenus_ponderes,
        "charges_sans_loyer": charges_sans_loyer,
        "charges_avec_loyer": charges_avec_loyer,
        "resultats": resultats,
    }


def stats_capacite_emprunt_foyer(clients: list) -> dict:
    from services.taux_manager import get_tous_les_taux

    total_revenus = 0.0
    for c in clients:
        r, _ = _revenus_ponderes_mensuels(c)
        total_revenus += r

    total_charges_sans_loyer = 0.0
    total_charges_avec_loyer = 0.0
    seen_depenses = set()
    seen_credits = set()

    for c in clients:
        for d in c.depenses:
            if id(d) in seen_depenses:
                continue
            seen_depenses.add(id(d))
            if d.categorie_depense == "Impôts et taxes":
                total_charges_sans_loyer += d.montant
                total_charges_avec_loyer += d.montant
            if d.categorie_depense in ("Loyer"):
                total_charges_avec_loyer += d.montant

        for cr in c.credits:
            if id(cr) in seen_credits:
                continue
            seen_credits.add(id(cr))
            m = sum(cr.mensualite_client(cl) for cl in clients if cl in cr.emprunteur)
            total_charges_sans_loyer += m
            total_charges_avec_loyer += m

    taux_data = get_tous_les_taux()
    resultats, m_sans, m_avec = _resultats_capacite(
        total_revenus, total_charges_sans_loyer, total_charges_avec_loyer, taux_data
    )
    return {
        "mode": "foyer",
        "noms": [c.nom for c in clients],
        "revenus_ponderes": round(total_revenus, 2),
        "charges_sans_loyer": round(total_charges_sans_loyer, 2),
        "charges_avec_loyer": round(total_charges_avec_loyer, 2),
        "resultats": resultats,
    }


# Épargne

def _interets_composes(solde, versement_mensuel, taux_annuel, nb_mois, versements_ponctuels=None):
    taux_mensuel = taux_annuel / 100 / 12
    s = solde
    mois_debut = datetime.now().month
    for i in range(nb_mois):
        mois_courant = ((mois_debut - 1 + i) % 12) + 1
        vp = 0.0
        if versements_ponctuels:
            vp = sum(v.montant for v in versements_ponctuels if v.mois == mois_courant)
        s = s * (1 + taux_mensuel) + versement_mensuel + vp
    return round(s, 2)


def stats_epargne(client: Client, nb_mois_libre: int | None = None) -> dict:
    encours_total = sum(e.solde for e in client.epargnes)
    versements_total = sum(e.versements_permanents for e in client.epargnes)

    horizons = [(12, "1 an")]
    if nb_mois_libre and nb_mois_libre != 12:
        horizons.append((nb_mois_libre, f"{nb_mois_libre} mois"))

    detail_produits = []
    projections_consolidees = {label: 0.0 for _, label in horizons}

    for e in client.epargnes:
        projections_produit = {}
        for nb_mois, label in horizons:
            valeur = _interets_composes(e.solde, e.versements_permanents, e.taux, nb_mois, e.versements_ponctuels)
            projections_produit[label] = valeur
            projections_consolidees[label] += valeur
        detail_produits.append({
            "nom": e.nom,
            "solde": round(e.solde, 2),
            "versement": round(e.versements_permanents, 2),
            "taux": e.taux,
            "plafond_max": e.plafond_max,
            "projections": projections_produit,
            "nb_versements_ponctuels": len(e.versements_ponctuels),
        })

    projections_consolidees = {k: round(v, 2) for k, v in projections_consolidees.items()}

    familles = {
        "Livrets réglementés": [1, 2, 3, 4, 5, 6],
        "Livrets bancaires": [7, 8],
        "Assurance Vie / Capi": [9, 10],
        "Epargne retraite": [11, 12, 13],
        "Placements financiers": [14, 15, 16],
        "Autre": [17],
    }
    repartition = {}
    for famille, codes in familles.items():
        total = sum(e.solde for e in client.epargnes if e.type_epargne in codes)
        if total > 0:
            repartition[famille] = round(total, 2)

    return {
        "encours_total": round(encours_total, 2),
        "versements_total": round(versements_total, 2),
        "detail_produits": detail_produits,
        "projections_consolidees": projections_consolidees,
        "repartition_familles": repartition,
        "nb_produits": len(client.epargnes),
        "horizon_libre_mois": nb_mois_libre,
    }


# Patrimoine

def stats_patrimoine(client: Client) -> dict:

    brut_total = 0.0
    crd_total = 0.0
    revenus_locatifs_annuels = 0.0
    repartition = {}
    detail = []

    for p in client.patrimoines:
        valeur_detenue = p.valeur_detention

        crd_bien = 0.0
        mensualite_credit = 0.0
        for cr in p.credits:
            part_client = cr.emprunteur.get(client, 1.0)
            if cr.crd is not None:
                crd_bien += cr.crd * part_client
            mensualite_credit += cr.mensualite * part_client

        revenu_annuel = 0.0
        if p.revenu:
            if p.revenu.periodicite == "mensuelle":
                revenu_annuel = p.revenu.montant * 12
            elif p.revenu.periodicite == "annuelle":
                revenu_annuel = p.revenu.montant
        revenus_locatifs_annuels += revenu_annuel

        rendement_brut = (revenu_annuel / valeur_detenue * 100) if valeur_detenue > 0 and revenu_annuel > 0 else 0.0
        effort_immobilier = round(mensualite_credit - revenu_annuel / 12, 2)

        brut_total += valeur_detenue
        crd_total += crd_bien

        famille = _famille_patrimoine(p.type_patrimoine)
        repartition[famille] = repartition.get(famille, 0) + valeur_detenue

        detail.append({
            "nom": p.nom,
            "type": p.type_patrimoine,
            "valeur": round(p.valeur, 2),
            "part": p.part,
            "valeur_detenue": round(valeur_detenue, 2),
            "crd": round(crd_bien, 2),
            "valeur_nette": round(valeur_detenue - crd_bien, 2),
            "revenu_annuel": round(revenu_annuel, 2),
            "rendement_brut": round(rendement_brut, 2),
            "effort_immobilier": effort_immobilier,
            "nb_credits": len(p.credits),
        })

    return {
        "patrimoine_brut": round(brut_total, 2),
        "crd_total": round(crd_total, 2),
        "patrimoine_net": round(brut_total - crd_total, 2),
        "revenus_locatifs_annuels": round(revenus_locatifs_annuels, 2),
        "revenus_locatifs_mensuels": round(revenus_locatifs_annuels / 12, 2),
        "repartition": {k: round(v, 2) for k, v in repartition.items()},
        "detail": detail,
        "nb_biens": len(client.patrimoines),
    }


def _famille_patrimoine(type_patrimoine: str) -> str:
    immobilier = {"Résidence principale", "Résidence secondaire",
                  "Immobilier locatif", "Terrain", "Parking/Garage", "Parts de SCI"}
    if type_patrimoine in immobilier:
        return "Immobilier"
    if type_patrimoine == "Biens d'usage (bijoux, voiture, œuvres d'art)":
        return "Biens d'usage"
    return "Autre"


# Foyer (stats non financières)

def stats_foyer(clients: list) -> dict:
    if not clients:
        return {}

    mois_courant = datetime.now().month

    total_revenus_foyer = 0.0
    revenus_par_client = {}
    for c in clients:
        rev = sum(r.montant for r in c.revenus if r.periodicite == "mensuelle")
        rev += sum(r.montant / 12 for r in c.revenus if r.periodicite == "annuelle")
        revenus_par_client[c.nom] = round(rev, 2)
        total_revenus_foyer += rev

    seen_dep = set()
    total_depenses_foyer = 0.0
    for c in clients:
        for d in c.depenses:
            if id(d) not in seen_dep and d.est_a_appliquer(mois_courant):
                seen_dep.add(id(d))
                total_depenses_foyer += d.montant

    seen_cr = set()
    all_credits = []
    for c in clients:
        for cr in c.credits:
            if id(cr) not in seen_cr:
                seen_cr.add(id(cr))
                all_credits.append(cr)

    # Mensualités foyer = somme pondérée par les parts des clients sélectionnés
    total_mensualites_foyer = sum(
        sum(cr.mensualite_client(c) for c in clients if c in cr.emprunteur)
        for cr in all_credits
    )
    # CRD total
    crd_foyer = sum(cr.crd for cr in all_credits if cr.crd is not None)

    taux_endettement_foyer = (
        (total_mensualites_foyer / total_revenus_foyer * 100)
        if total_revenus_foyer > 0 else 0.0
    )

    seen_ep = set()
    encours_epargne_foyer = 0.0
    for c in clients:
        for e in c.epargnes:
            if id(e) not in seen_ep:
                seen_ep.add(id(e))
                encours_epargne_foyer += e.solde

    seen_pat = set()
    patrimoine_brut_foyer = 0.0
    for c in clients:
        for p in c.patrimoines:
            if id(p) not in seen_pat:
                seen_pat.add(id(p))
                patrimoine_brut_foyer += p.valeur_detention

    contributions = {}
    for cr in all_credits:
        for client, part in cr.emprunteur.items():
            if client in clients:
                contributions[client.nom] = contributions.get(client.nom, 0) + cr.mensualite * part

    solde_foyer = total_revenus_foyer - total_depenses_foyer - total_mensualites_foyer

    return {
        "nb_clients": len(clients),
        "noms": [c.nom for c in clients],
        "total_revenus_foyer": round(total_revenus_foyer, 2),
        "revenus_par_client": revenus_par_client,
        "total_depenses_foyer": round(total_depenses_foyer, 2),
        "total_mensualites_foyer": round(total_mensualites_foyer, 2),
        "crd_foyer": round(crd_foyer, 2),
        "taux_endettement_foyer": round(taux_endettement_foyer, 2),
        "alerte_endettement": taux_endettement_foyer > 35.0,
        "solde_foyer": round(solde_foyer, 2),
        "encours_epargne_foyer": round(encours_epargne_foyer, 2),
        "patrimoine_brut_foyer": round(patrimoine_brut_foyer, 2),
        "contributions_credits": {k: round(v, 2) for k, v in contributions.items()},
    }


# Façade complète

def synthese_complete(
    clients: list,
    comptes_dict: dict,
    mois: int | None = None,
    annee: int | None = None,
    nb_mois_epargne_libre: int | None = None
) -> dict:
    now = datetime.now()
    mois = mois or now.month
    annee = annee or now.year
    client_principal = clients[0] if clients else None

    # Endettement et capacité : foyer si plusieurs clients, individuel sinon
    if len(clients) > 1:
        endettement = stats_endettement_foyer(clients)
        capacite = stats_capacite_emprunt_foyer(clients)
    else:
        endettement = stats_endettement(client_principal) if client_principal else {}
        capacite = stats_capacite_emprunt(client_principal) if client_principal else {}

    compte_ids = []
    seen = set()
    for c in clients:
        for cpt in c.comptes:
            cpt_id = next((cid for cid, obj in comptes_dict.items() if obj is cpt), None)
            if cpt_id is not None and cpt_id not in seen:
                seen.add(cpt_id)
                compte_ids.append(cpt_id)

    return {
        "noms_clients": [c.nom for c in clients],
        "date_calcul": now.strftime("%d/%m/%Y %H:%M"),
        "budget": stats_budget(clients, mois, annee),
        "comptes": stats_comptes(clients, comptes_dict, compte_ids),
        "endettement": endettement,
        "capacite_emprunt": capacite,
        "epargne": stats_epargne(client_principal, nb_mois_epargne_libre) if client_principal else {},
        "patrimoine": stats_patrimoine(client_principal) if client_principal else {},
        "foyer": stats_foyer(clients) if len(clients) > 1 else None,
    }