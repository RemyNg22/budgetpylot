# BudgetPylot : Simulateur Bancaire Personnel

BudgetPylot est un simulateur bancaire personnel développé en **Python** avec une interface web en **HTML/Flask**. Il permet de suivre son budget, ses crédits, ses épargnes et de faire des prévisions financières sur plusieurs mois. Il permet aussi d'avoir des statistiques personnalisées et bancaires telles que votre taux d'endettement, votre capacité d'emprunt sur 20 et 25 ans, et bien d'autres choses.

**Le lien du site web BudgetPylot** : [https://budgetpylot.com/](https://bugetpylot.com)
---

## Fonctionnalités

- Saisie du solde initial, des revenus et des dépenses (fixes et variables)
- Gestion de plusieurs crédits (capital, taux, durée, mensualité)
- Gestion de plusieurs épargnes (montant initial, versements, taux)
- Calcul automatique du reste à vivre
- Calcul du taux d’endettement
- Simulation de capacité d’emprunt
- Simulation de capacité d’épargne
- Prévisions sur N mois (solde, épargne, amortissement des crédits)
- Visualisation de statistiques et graphiques financiers
- Import / export des données via CSV

---

## Architecture du projet

```text
finance_app/

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