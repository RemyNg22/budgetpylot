class Compte:

    def __init__(self, banque: str, nom_compte: str, solde_initial: float):
        self.banque = banque.strip()
        self.nom_compte = nom_compte.strip()
        self.solde_initial = float(solde_initial)
        self.client_ids: list[int] = []

    def ajouter_proprietaire(self, client_id: int):
        if client_id not in self.client_ids:
            self.client_ids.append(client_id)

    def retirer_proprietaire(self, client_id: int):
        self.client_ids = [cid for cid in self.client_ids if cid != client_id]

    @property
    def est_joint(self) -> bool:
        return len(self.client_ids) > 1

    def __repr__(self):
        return (
            f"{self.nom_compte} ({self.banque}) "
            f"- Solde actuel : {self.solde_initial:.2f} EUR "
            f"- Proprietaires : {self.client_ids}"
        )