"""
Récupération des taux immobiliers depuis l'API Banque de France (Webstat).
En cas d'échec, utilise les taux écrit dans config.py.
Cache en mémoire pour ne pas appeler l'API à chaque requête.
"""
import requests
from datetime import datetime, timedelta
from config import TAUX_FALLBACK, CACHE_DUREE_SECONDES, BDF_API_BASE, BDF_SERIES

# Cache en mémoire
_cache: dict = {}

def _taux_depuis_cache(duree: str) -> float | None:
    """Retourne le taux en cache s'il est encore valide, sinon None."""
    if duree not in _cache:
        return None
    valeur, expiration = _cache[duree]
    if datetime.now() < expiration:
        return valeur
    return None

def _mettre_en_cache(duree: str, valeur: float):
    """Stocke le taux en cache avec une expiration."""
    expiration = datetime.now() + timedelta(seconds=CACHE_DUREE_SECONDES)
    _cache[duree] = (valeur, expiration)


def _recuperer_taux_bdf(duree: str) -> float | None:
    """
    Appelle l'API Webstat BDF pour récupérer le dernier taux disponible.
    Retourne le taux en % ou None en cas d'échec.
    """
    serie_id = BDF_SERIES.get(duree)
    if not serie_id:
        return None


    url = f"{BDF_API_BASE}/{serie_id}/records"
    params = {
        "limit": 1,
        "order_by": "time_period DESC",}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        records = data.get("results", [])
        if not records:
            return None

        valeur = records[0].get("obs_value")
        if valeur is None:
            return None

        return round(float(valeur), 2)

    except Exception:
        return None


def get_taux(duree: str) -> dict:
    """
    Retourne le taux pour la durée demandée ("20_ans" ou "25_ans").
    """
    # 1.Vérifier le cache
    taux_cache = _taux_depuis_cache(duree)
    if taux_cache is not None:
        return {
            "taux": taux_cache,
            "source": "bdf",
            "mise_a_jour": _cache[duree][1].strftime("%d/%m/%Y"),
        }

    # 2. Appel API
    taux_bdf = _recuperer_taux_bdf(duree)
    if taux_bdf is not None:
        _mettre_en_cache(duree, taux_bdf)
        return {
            "taux": taux_bdf,
            "source": "bdf",
            "mise_a_jour": datetime.now().strftime("%d/%m/%Y"),
        }

    # 3. Appel taux défini manuellement dans config.py
    taux_fallback = TAUX_FALLBACK.get(duree, 4.0)
    return {
        "taux": taux_fallback,
        "source": "fallback",
        "mise_a_jour": None,
    }


def get_tous_les_taux() -> dict:
    """
    Retourne les taux pour 20 et 25 ans en un seul appel.
    """
    return {
        "20_ans": get_taux("20_ans"),
        "25_ans": get_taux("25_ans"),
    }


def vider_cache():
    """Force le rechargement depuis l'API au prochain appel."""
    _cache.clear()