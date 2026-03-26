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

    # Capacité d'épargne mensuelle = reste à vivre - dépenses variables
    capacite_epargne_mensuelle = round(reste_a_vivre - total_variables, 2)

    segments: dict[str, float] = {
        "Loyer": 0.0,
        "Assurances": 0.0,
        "Energie": 0.0,
        "Numérique": 0.0,
        "Impôts": 0.0,
        "Dépenses courantes": 0.0,
        "Transport": 0.0,
        "Santé": 0.0,
        "Loisirs": 0.0,
        "Autre": 0.0,
        "Epargne": round(total_epargne_mois, 2),
        "Crédits": round(total_mensualites, 2),
    }
    for cat, montant in depenses_par_categorie.items():
        segment = SEGMENTS_CAMEMBERT.get(cat, "Autre")
        segments[segment] = round(segments[segment] + montant, 2)

    segments_camembert = {k: v for k, v in segments.items() if v > 0}

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
        "segments_camembert": segments_camembert,
    }


# Comptes et projections

def stats_comptes(clients: list, comptes_dict: dict, compte_ids: list) -> dict:
    """
    Soldes actuels, projections fin de mois / prochain salaire,
    et évolution du solde sur 12 mois pour chaque compte.
    compte_ids : liste des ids de comptes appartenant aux clients sélectionnés.
    """
    aujourd_hui = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    detail_comptes = []

    for compte_id in compte_ids:
        compte = comptes_dict.get(compte_id)
        if not compte:
            continue

        proprietaires = [c for c in clients if compte_id in [
            cpt_id for cpt_id, cpt in comptes_dict.items()
            if cpt is compte and compte_id in cpt.client_ids
        ]]
        # Récupération directe des propriétaires via client_ids du compte
        from models.client import Client as ClientModel
        proprietaires_compte = []
        for c in clients:
            if compte_id in compte.client_ids and c in [
                clients[i] if i < len(clients) else None
                for i in range(len(clients))
            ]:
                proprietaires_compte.append(c)

        # On prend tous les clients dont l'id est dans compte.client_ids
        # mais on ne dispose que des objets clients passés en paramètre
        proprietaires_compte = clients  # simplifié : tous les clients sélectionnés

        fin_mois = ClientModel.solde_fin_de_mois(
            compte, compte_id, proprietaires_compte, aujourd_hui
        )

        solde_sal, rev_principal, date_sal = ClientModel.solde_prochain_salaire(
            compte, compte_id, proprietaires_compte, aujourd_hui
        )

        # Évolution sur 12 mois : solde projeté fin de chaque mois
        evolution_12_mois = []
        for i in range(12):
            date_fin = aujourd_hui + relativedelta(months=i + 1)
            date_fin = date_fin.replace(
                day=1
            ) + relativedelta(months=1) - relativedelta(days=1)
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
    "salaire":                  1.00,
    "prime fixe":               0.50,
    "bonus":                    0.00,
    "revenu non salarié":       1.00,
    "allocations chômage":      0.00,
    "pension d'invalidité":     0.00,
    "retraite":                 1.00,
    "RSA":                      0.00,
    "APL":                      0.00,
    "allocations familiales":   0.50,
    "prime d'activité":         0.00,
    "bourse étudiante":         0.00,
    "loyer":                    0.70,
    "revenu SCPI":              0.70,
    "intérêt d'épargne":        0.50,
    "coupon obligataire":       0.00,
    "héritage":                 0.00,
    "donation":                 0.00,
    "gain exceptionnel":        0.00,
    "vente d'actifs":           0.00,
    "indemnité":                0.00,
    "virement reçu":            0.00,
    "remboursement":            0.00,
    "autre":                    0.00,
}

def _revenus_ponderes_mensuels(client: Client) -> tuple[float, list]:
    """
    Calcule les revenus mensuels pondérés selon la grille bancaire.
    Retourne (total_pondere, detail_par_revenu).
    """
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
            continue  # revenus uniques non pris en compte
        montant_pondere = montant_mensuel * coeff
        total += montant_pondere
        detail.append({
            "type": r.type_de_revenu,
            "montant_brut": round(montant_mensuel, 2),
            "coefficient": coeff,
            "montant_pondere": round(montant_pondere, 2),
        })
    return round(total, 2), detail


def _charges_endettement(client: Client) -> float:
    """
    Charges retenues pour le taux d'endettement bancaire :
    loyers payés + impôts + mensualités crédits en cours.
    """
    charges = 0.0
    # Loyers payés
    for d in client.depenses:
        if d.categorie_depense in ("Loyer", "Charge immobilière (hors crédit)"):
            charges += d.montant
    # Impôts
    for d in client.depenses:
        if d.categorie_depense == "Impôts et taxes":
            charges += d.montant
    # Crédits
    for cr in client.credits:
        charges += cr.mensualite_client(client)
    return round(charges, 2)

def _charges_capacite(client: Client, inclure_loyer: bool) -> float:
    """
    Charges retenues pour la capacité d'emprunt :
    - Ligne 1 (inclure_loyer=False) : impôts + crédits uniquement
    - Ligne 2 (inclure_loyer=True)  : impôts + crédits + loyer
    """
    charges = 0.0
    # Impôts
    for d in client.depenses:
        if d.categorie_depense == "Impôts et taxes":
            charges += d.montant
    # Crédits
    for cr in client.credits:
        charges += cr.mensualite_client(client)
    # Loyer (optionnel)
    if inclure_loyer:
        for d in client.depenses:
            if d.categorie_depense in ("Loyer", "Charge immobilière (hors crédit)"):
                charges += d.montant
    return round(charges, 2)


# Taux d'endettement
def stats_endettement(client: Client) -> dict:
    """
    Taux d'endettement bancaire réel.
    Revenus pondérés selon grille bancaire.
    Charges = loyers + impôts + crédits.
    Seuil HCSF : 35%.
    """
    revenus_ponderes, detail_revenus = _revenus_ponderes_mensuels(client)
    charges = _charges_endettement(client)

    taux_endettement = (
        (charges / revenus_ponderes * 100)
        if revenus_ponderes > 0 else 0.0)

    crd_total = sum(cr.crd for cr in client.credits)
    crd_par_type: dict[str, float] = {}
    for cr in client.credits:
        crd_par_type[cr.nom] = crd_par_type.get(cr.nom, 0) + cr.crd

    aujourd_hui = datetime.now()
    detail_credits = []
    for cr in client.credits:
        delta = cr.fin_credit - aujourd_hui
        mois_restants = max(0, round(delta.days / 30.44))
        part_client = cr.emprunteur.get(client, 1.0)
        mensualite_part = cr.mensualite_client(client)
        cout_restant = round(
            max(0, mensualite_part * mois_restants - cr.crd * part_client), 2
        )
        detail_credits.append({
            "nom": cr.nom,
            "mensualite": round(mensualite_part, 2),
            "crd": round(cr.crd, 2),
            "taux": cr.taux,
            "fin_credit": cr.fin_credit.strftime("%d/%m/%Y"),
            "part": round(part_client * 100, 1),
            "mois_restants": mois_restants,
            "cout_total_restant": cout_restant,
        })

    cout_total_global = sum(d["cout_total_restant"] for d in detail_credits)

    return {
        "revenus_ponderes": revenus_ponderes,
        "detail_revenus_ponderes": detail_revenus,
        "charges_retenues": charges,
        "taux_endettement": round(taux_endettement, 2),
        "seuil_legal": 35.0,
        "alerte": taux_endettement > 35.0,
        "crd_total": round(crd_total, 2),
        "crd_par_type": {k: round(v, 2) for k, v in crd_par_type.items()},
        "detail_credits": detail_credits,
        "nb_credits": len(client.credits),
        "cout_total_global": round(cout_total_global, 2),
    }


# Capacité d'emprunt
def _calculer_capital(mensualite_max: float, taux_annuel: float, nb_ans: int) -> float:
    """Capital empruntable via formule d'amortissement."""
    taux_mensuel = taux_annuel / 100 / 12
    n = nb_ans * 12
    if mensualite_max <= 0:
        return 0.0
    if taux_mensuel == 0:
        return mensualite_max * n
    return mensualite_max * (1 - (1 + taux_mensuel) ** -n) / taux_mensuel


def stats_capacite_emprunt(client: Client) -> dict:
    """
    Capacité d'emprunt sur 20 et 25 ans, deux scénarios :
    - Sans loyer : charges = impôts + crédits
    - Avec loyer : charges = impôts + crédits + loyer (cas investissement locatif)
    Revenus pondérés selon grille bancaire.
    Taux depuis API BdF ou fallback config.py.
    """
    from services.taux_manager import get_tous_les_taux

    revenus_ponderes, detail_revenus = _revenus_ponderes_mensuels(client)
    charges_sans_loyer = _charges_capacite(client, inclure_loyer=False)
    charges_avec_loyer = _charges_capacite(client, inclure_loyer=True)

    mensualite_dispo_sans_loyer = round(
        max(0, revenus_ponderes * 0.35 - charges_sans_loyer), 2
    )
    mensualite_dispo_avec_loyer = round(
        max(0, revenus_ponderes * 0.35 - charges_avec_loyer), 2
    )

    taux_data = get_tous_les_taux()
    resultats = {}

    for duree_label, nb_ans in [("20_ans", 20), ("25_ans", 25)]:
        info_taux = taux_data[duree_label]
        taux_annuel = info_taux["taux"]

        capital_sans_loyer = _calculer_capital(
            mensualite_dispo_sans_loyer, taux_annuel, nb_ans
        )
        capital_avec_loyer = _calculer_capital(
            mensualite_dispo_avec_loyer, taux_annuel, nb_ans
        )

        resultats[duree_label] = {
            "nb_ans": nb_ans,
            "taux": taux_annuel,
            "source_taux": info_taux["source"],
            "mise_a_jour_taux": info_taux["mise_a_jour"],
            # Scénario 1 : sans loyer (résidence principale, primo-accédant)
            "sans_loyer": {
                "mensualite_dispo": mensualite_dispo_sans_loyer,
                "capital_empruntable": round(max(0, capital_sans_loyer), 2),
            },
            # Scénario 2 : avec loyer (investissement locatif, reste locataire)
            "avec_loyer": {
                "mensualite_dispo": mensualite_dispo_avec_loyer,
                "capital_empruntable": round(max(0, capital_avec_loyer), 2),
            },
        }

    return {
        "revenus_ponderes": revenus_ponderes,
        "detail_revenus_ponderes": detail_revenus,
        "charges_sans_loyer": charges_sans_loyer,
        "charges_avec_loyer": charges_avec_loyer,
        "resultats": resultats,
    }


# Epargne et projections

def _interets_composes(
    solde: float,
    versement_mensuel: float,
    taux_annuel: float,
    nb_mois: int,
    versements_ponctuels: list | None = None
) -> float:
    """
    Intérêts composés mensuels avec versements permanents et ponctuels.
    versements_ponctuels : liste de VersementPonctuel.
    """
    taux_mensuel = taux_annuel / 100 / 12
    s = solde
    mois_debut = datetime.now().month
    annee_debut = datetime.now().year

    for i in range(nb_mois):
        mois_courant = ((mois_debut - 1 + i) % 12) + 1
        vp_mois = 0.0
        if versements_ponctuels:
            vp_mois = sum(
                vp.montant for vp in versements_ponctuels
                if vp.mois == mois_courant
            )
        s = s * (1 + taux_mensuel) + versement_mensuel + vp_mois

    return round(s, 2)


def stats_epargne(client: Client, nb_mois_libre: int | None = None) -> dict:
    """
    Encours total, projections 1 an + durée libre, capacité d'épargne,
    répartition par famille.
    """
    encours_total = sum(e.solde for e in client.epargnes)
    versements_total = sum(e.versements_permanents for e in client.epargnes)

    horizons_fixes = [(12, "1 an")]
    if nb_mois_libre and nb_mois_libre != 12:
        horizons = horizons_fixes + [(nb_mois_libre, f"{nb_mois_libre} mois")]
    else:
        horizons = horizons_fixes

    detail_produits = []
    projections_consolidees = {label: 0.0 for _, label in horizons}

    for e in client.epargnes:
        projections_produit = {}
        for nb_mois, label in horizons:
            valeur = _interets_composes(
                e.solde,
                e.versements_permanents,
                e.taux,
                nb_mois,
                e.versements_ponctuels
            )
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
    repartition: dict[str, float] = {}
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
    repartition: dict[str, float] = {}
    detail = []

    for p in client.patrimoines:
        valeur_detenue = p.valeur_detention

        crd_bien = 0.0
        if p.credit:
            part_client = p.credit.emprunteur.get(client, 1.0)
            crd_bien = p.credit.crd * part_client

        revenu_annuel = 0.0
        if p.revenu:
            if p.revenu.periodicite == "mensuelle":
                revenu_annuel = p.revenu.montant * 12
            elif p.revenu.periodicite == "annuelle":
                revenu_annuel = p.revenu.montant
        revenus_locatifs_annuels += revenu_annuel

        rendement_brut = (
            (revenu_annuel / valeur_detenue * 100)
            if valeur_detenue > 0 and revenu_annuel > 0 else 0.0
        )

        # Effort d'épargne immobilier = mensualité crédit - loyer perçu mensuel
        mensualite_credit = 0.0
        if p.credit:
            part_client = p.credit.emprunteur.get(client, 1.0)
            mensualite_credit = p.credit.mensualite * part_client
        loyer_mensuel = revenu_annuel / 12
        effort_immobilier = round(mensualite_credit - loyer_mensuel, 2)

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
        })

    patrimoine_net = brut_total - crd_total

    return {
        "patrimoine_brut": round(brut_total, 2),
        "crd_total": round(crd_total, 2),
        "patrimoine_net": round(patrimoine_net, 2),
        "revenus_locatifs_annuels": round(revenus_locatifs_annuels, 2),
        "revenus_locatifs_mensuels": round(revenus_locatifs_annuels / 12, 2),
        "repartition": {k: round(v, 2) for k, v in repartition.items()},
        "detail": detail,
        "nb_biens": len(client.patrimoines),
    }


def _famille_patrimoine(type_patrimoine: str) -> str:
    immobilier = {
        "Résidence principale", "Résidence secondaire",
        "Immobilier locatif", "Terrain", "Parking/Garage", "Parts de SCI"
    }
    financier = {
        "Parts de SCI"
    }
    if type_patrimoine in immobilier:
        return "Immobilier"
    if type_patrimoine == "Biens d'usage (bijoux, voiture, oeuvres d'art)":
        return "Biens d'usage"
    return "Autre"


# Foyer / multi-clients

def stats_foyer(clients: list[Client]) -> dict:

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

    total_mensualites_foyer = sum(cr.mensualite for cr in all_credits)
    crd_foyer = sum(cr.crd for cr in all_credits)

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
            nom = client.nom
            contributions[nom] = contributions.get(nom, 0) + cr.mensualite * part

    solde_foyer = total_revenus_foyer - total_depenses_foyer - total_mensualites_foyer

    return {
        "nb_clients": len(clients),
        "noms": [c.nom for c in clients],
        "total_revenus_foyer": round(total_revenus_foyer, 2),
        "revenus_par_client": {k: round(v, 2) for k, v in revenus_par_client.items()},
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

    # Comptes appartenant aux clients sélectionnés
    compte_ids = []
    seen = set()
    for c in clients:
        for cpt in c.comptes:
            cpt_id = next(
                (cid for cid, obj in comptes_dict.items() if obj is cpt), None
            )
            if cpt_id is not None and cpt_id not in seen:
                seen.add(cpt_id)
                compte_ids.append(cpt_id)

    return {
        "noms_clients": [c.nom for c in clients],
        "date_calcul": now.strftime("%d/%m/%Y %H:%M"),
        "budget": stats_budget(clients, mois, annee),
        "comptes": stats_comptes(clients, comptes_dict, compte_ids),
        "endettement": stats_endettement(client_principal) if client_principal else {},
        "capacite_emprunt": stats_capacite_emprunt(client_principal) if client_principal else {},
        "epargne": stats_epargne(client_principal, nb_mois_epargne_libre) if client_principal else {},
        "patrimoine": stats_patrimoine(client_principal) if client_principal else {},
        "foyer": stats_foyer(clients) if len(clients) > 1 else None,
    }