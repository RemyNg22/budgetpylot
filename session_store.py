import uuid
from flask import session

# Stockage en mémoire serveur (temporaire)
SESSION_STORE = {}


class SessionData:
    def __init__(self):
        self.clients = {}
        self.comptes = {}
        self.next_client_id = 0
        self.next_compte_id = 0
        self.next_item_id = 0

    def next_id(self):
        self.next_item_id += 1
        return self.next_item_id

    def reset(self):
        self.clients = {}
        self.comptes = {}
        self.next_client_id = 0
        self.next_compte_id = 0
        self.next_item_id = 0


def get_session_data():
    user_id = session.get("user_id")

    if not user_id:
        user_id = str(uuid.uuid4())
        session["user_id"] = user_id

    if user_id not in SESSION_STORE:
        SESSION_STORE[user_id] = SessionData()

    return SESSION_STORE[user_id]