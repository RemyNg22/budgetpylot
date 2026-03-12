import pandas as pd

df_revenus = pd.DataFrame(columns=["id", "type", "montant", "periodicite", "jour", "mois"])
df_depenses = pd.DataFrame(columns=["id", "type", "montant", "periodicite", "jour", "mois"])
df_epargnes = pd.DataFrame(columns=["id", "type", "solde", "versement_mensuel", "taux"])
df_credits = pd.DataFrame(columns=["id", "type", "capital_emprunté", "crd", "taux", "duree_initiale", "mensualite", "fin_credit"])