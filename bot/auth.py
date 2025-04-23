import bcrypt
from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI) # connessione al Server MongoDB
db = client.smartplant # Estrae il database 'smartplant'
users = db.users # estrae i dati contenuti nella categoria 'users'

# Questo file gestisce l'aspetto di autenticazione relativo al database, quindi non considera lo stato attuale della sessione.
# La sessione viene gestita da handlers.py

def register_user(username, password, chat_id): # incaricato di registrare lo user
    if users.find_one({"chat_id": chat_id}): # se l'account esiste già non registrarlo
        return False, "❌ Hai già un account registrato."

    if users.find_one({"username": username}): # se lo username esiste già non registrarlo
        return False, "❌ Username già in uso."

    salt = bcrypt.gensalt() # genera un salt da usare per la password durante l'operazione di hash
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt) # applica l'algoritmo di hashing bcrypt (che è ottimo per le password)

    user_data = { # dati da salvare nel database
        "chat_id": chat_id,
        "username": username,
        "password_hash": hashed_pw,
        "salt": salt
    }

    users.insert_one(user_data) # salva i dati nel database
    return True, "✅ Registrazione completata con successo."


def authenticate_user(username, password, chat_id): # incaricato del login
    user = users.find_one({"username": username})
    if not user: # controlla se lo user esiste nel database
        return False

    if user.get("chat_id") != chat_id: # evita di fare il login da account telegram diversi
        return False # Nota: non metto un messaggio di errore personalizzato per evitare di rilasciare troppe informazioni.

    hashed_input = bcrypt.hashpw(password.encode('utf-8'), user['salt']) # calcola l'hash della password inviata
    if hashed_input != user['password_hash']: # controlla se la password è coerente con quella salvata nel database
        return False

    return True
