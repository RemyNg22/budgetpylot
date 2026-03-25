"""
Paramètres globaux de l'application.

Les taux immobiliers de ce script sont utilisés quand l'API
Banque de France est indisponible. Ils seront mis à jour régulièrement
Dernière mise à jour manuelle : mars 2026
"""

TAUX_FALLBACK = {
    "20_ans": 3.50,   # taux moyen crédit immobilier 20 ans
    "25_ans": 3.70,   # taux moyen crédit immobilier 25 ans
}

# Durée de validité du cache API en secondes (24h)
CACHE_DUREE_SECONDES = 86400

# Séries Banque de france Webstat (API Opendatasoft publique)
BDF_API_BASE = "https://webstat.banque-france.fr/api/explore/v2.1/catalog/datasets"
BDF_SERIES = {
    "20_ans": "mir1-q-fr-r-a22frx-y-r-a-2250fr-eur-n",
    "25_ans": "mir1-q-fr-r-a22frx-y-r-a-2254fr-eur-n",
}