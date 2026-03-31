# BudgetPylot : Simulateur Bancaire Personnel

BudgetPylot est un simulateur bancaire personnel développé en **Python** avec une interface web en **HTML/Flask**. Il permet de suivre son budget, ses crédits, ses épargnes et de faire des prévisions financières sur plusieurs mois. Il permet aussi d'avoir des statistiques personnalisées et bancaires telles que votre taux d'endettement, votre capacité d'emprunt sur 20 et 25 ans, et bien d'autres choses.

**Le lien du site web BudgetPylot**

[https://budgetpylot.com/](https://budgetpylot.com)


Lien vers le notebook : [https://github.com/RemyNg22/budgetpylot/blob/main/notebook/notebook_budgetpylot.ipynb](https://github.com/RemyNg22/budgetpylot/blob/main/notebook/notebook_budgetpylot.ipynb)


---

## Objectif

Fournir une vision claire et complète de la situation financière d’un utilisateur ou d’un foyer :

- Analyse des revenus et dépenses
- Suivi des crédits et de l’endettement
- Pilotage de l’épargne
- Évaluation du patrimoine
- Simulations financières avancées

---

## Fonctionnalités

**Analyse des revenus et dépenses**

Pour chaque personne sélectionnée :

- Revenus totaux mensuels
- Revenu mensuel moyen
- Revenu annuel
- Dépenses mensuelles :
    - fixes
    - variables
    - uniques
- Répartition des dépenses par catégorie
- Solde mensuel (revenus - dépenses - crédits)
- Taux d’épargne
- Reste à vivre

**Suivi des comptes et trésorerie**

- Solde actuel par compte
- Solde estimé en fin de mois
- Solde estimé au prochain salaire
- Solde estimé à une date personnalisée
- Projection d’évolution du solde sur 12 mois (courbe)

**Analyse des crédits**

- Taux d’endettement global (avec seuil réglementaire de 35%)
- Capacité d’emprunt :
    - sur 25 ans
    - sur 20 ans
- Capital restant dû (CRD) total
- Coût total restant (intérêts)
- Durée restante par crédit

**Gestion de l'épargne**

- Encours total d’épargne
- Projection d’épargne :
    - à 1 an
    - à durée personnalisée
- Capacité d’épargne mensuelle
- Répartition par type de produit

**Analyse du patrimoine**

- Patrimoine brut total
- Patrimoine net (brut - dettes)
- Rendement locatif brut
- Effort d’épargne immobilier

**Outils complémentaires**

- Visualisation graphique des données financières
- Simulations et projections sur plusieurs périodes
- Import / export des données (CSV)

---

## Architecture du projet

```text
budgetpylot/

├── app.py                    # point d'entrée appli, routes flask
├── config.py                 # paramètres globaux (notamment gestion de taux de crédit)
├── session_store.py          # Stockage en mémoire serveur (temporaire)
├── README.md                 # Description projet
├── requirements.txt          # à installer
├── .gitignore                # à masquer

├── models/                   # structures de données
│   ├── client.py
│   ├── compte.py
│   ├── credit.py
│   ├── depense.py
│   ├── revenu.py
│   ├── patrimoine.py
│   └── epargne.py

├── services/                 # calculs métier
│   ├── taux_manager.py
│   └── statistiques.py

├── data/                     # sauvegarde des données
│   └── csv_manager.py
|
├── templates/                # HTML
│   ├── base.html
│   ├── saisie_budget.html (backup)
│   ├── projection.html
│   ├── stats.html
│   ├── etape_accueil.html
│   ├── etape_clients_comptes.html
│   ├── etape_credits.html
│   ├── etape_depenses.html
│   ├── etape_epargne.html
│   ├── etape_patrimoine.html
│   ├── etape_revenus.html
│   └── etape_synthese.html
|
|
├── notebook/                     # notebook explicatif POO
│   └── notebook_budgetpylot.ipynb
|
└── static/                   # visuel
    ├── css
    │   └── style.css
    └── img
        └── logobudgetpylot.png

```

---

## Lancement du projet

**1. Installation**

```
pip install -r requirements.txt
```

**2. Lancement de l'application**

```
python app.py
```

## Logique métier

L’application repose sur une séparation claire :

- models/ : structure des données
- services/ : calculs financiers et règles métier
- templates/ : rendu utilisateur
- data/ : import export csv (CSV)
