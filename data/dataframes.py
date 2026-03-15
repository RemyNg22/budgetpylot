import pandas as pd

df_clients = pd.DataFrame(columns=["id", "nom"])
df_compte_clients = pd.DataFrame(columns=["id_compte", "id_client", "part"])
df_comptes = pd.DataFrame(columns=["id", "nom_compte", "id_compte"])
df_revenus = pd.DataFrame(columns=["id", "type", "montant", "periodicite", "jour", "mois", "id_compte"])
df_depenses = pd.DataFrame(columns=["id", "type", "montant", "periodicite", "jour", "mois", "id_compte"])
df_epargnes = pd.DataFrame(columns=["id", "type", "solde", "versement_mensuel", "taux", "id_compte"])
df_credits = pd.DataFrame(columns=["id", "type", "capital_emprunté", "crd", "taux", "duree_initiale", "mensualite", "fin_credit", "id_compte"])