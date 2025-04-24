user_states = {} # viene popolato dagli stati degli user con le entry "user_id:state"
user_sessions = {} # viene popolato dagli user loggati con le entry "chat_id:username"

# State machine per gestire le azioni del bot e tiene traccia delle sessioni degli user tramite il loro chat_id
# gli chat_id sono unici per account telegram
# Nota: lo user_id è la chat_id


def set_state(user_id, state): # imposta lo stato attuale di uno user (loggato o non)
    user_states[user_id] = state


def get_state(user_id): # restituisce lo stato attuale di uno user (loggato o non)
    return user_states.get(user_id)


def clear_state(user_id): # rimuove lo stato di uno user
    user_states.pop(user_id, None)


def login_user(user_id, username): # gestisce il login dello user inserendo lo user dalla lista di utenti loggati
    user_sessions[user_id] = username


def logout_user(user_id): # gestisce il logout dello user rimuovendo lo user dalla lista di utenti loggati
    user_sessions.pop(user_id, None)


def is_logged_in(user_id): # controlla se uno user è attualmente loggato
    return user_id in user_sessions # se lo user è nella lista di user loggati restitusce True


def get_logged_username(user_id): # restituisce lo username associato al chat_id dell'utente loggato
    return user_sessions.get(user_id)
