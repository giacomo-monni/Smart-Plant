from .commands import commands
from .auth import register_user, authenticate_user
from .plant_manager import add_plant, get_user_plants, remove_plant, rename_plant
from .state_manager import (
    set_state, get_state, clear_state,
    login_user, logout_user,
    is_logged_in
)


def handle_update(update): # gestisce i comandi del bot e ciò che risponde l'utente
    message = update.get("message", {}) # messaggio ricevuto da telegram da uno user
    text = message.get("text", "") # estrae il testo del messaggio ricevuto
    chat_id = message.get("chat", {}).get("id") # estrae il chat_id dal messaggio ricevuto dallo user

    state = get_state(chat_id) # ottiene lo stato attuale dello user, serve per gestire le azioni del bot e dello user

    # *** STATE MACHINE ***
    if state == "register_username":
        set_state(chat_id, {"step": "register_password", "username": text})
        return {"method": "sendMessage", "chat_id": chat_id, "text": "🔐 Inserisci una password:"}

    elif isinstance(state, dict) and state.get("step") == "register_password":
        success, msg = register_user(state["username"], text, chat_id)
        clear_state(chat_id)
        return {"method": "sendMessage", "chat_id": chat_id, "text": msg}


    if state == "login_username":
        set_state(chat_id, {"step": "login_password", "username": text})
        return {"method": "sendMessage", "chat_id": chat_id, "text": "🔐 Inserisci la password:"}

    elif isinstance(state, dict) and state.get("step") == "login_password":
        ok = authenticate_user(state["username"], text, chat_id)
        clear_state(chat_id)
        if ok:
            login_user(chat_id, state["username"])
            welcome_text = f"✅ Benvenuto {state['username']}!\n\nEcco i comandi disponibili:\n"
            available = get_available_commands(chat_id)
            welcome_text += "\n".join([f"{cmd}: {commands[cmd]}" for cmd in available])
            return {"method": "sendMessage", "chat_id": chat_id, "text": welcome_text}
        else:
            return {"method": "sendMessage", "chat_id": chat_id, "text": "❌ Username e/o password errati."}

    if state == "add_plant_pot":
        # Verifica che l'utente non abbia già raggiunto il limite di piante
        user_plants = get_user_plants(chat_id)
        if len(user_plants) >= 10:  # Max 3 piante per esempio
            # Informa l'utente del limite raggiunto, ma non cambia lo stato
            clear_state(chat_id)  # Reset dello stato per consentire altri comandi
            return {"method": "sendMessage", "chat_id": chat_id,
                    "text": "❌ Hai già raggiunto il numero massimo di piante (3). Non puoi aggiungerne altre."}

        # Procede normalmente, se non ha raggiunto il limite
        set_state(chat_id, {"step": "add_plant_name", "pot_id": text})
        return {"method": "sendMessage", "chat_id": chat_id, "text": "🌱 Inserisci il nome della pianta da associare:"}

    elif isinstance(state, dict) and state.get("step") == "add_plant_name":
        success, msg = add_plant(chat_id, state["pot_id"], text)
        clear_state(chat_id)
        return {"method": "sendMessage", "chat_id": chat_id, "text": msg}

    if state == "remove_plant_select":
        success = remove_plant(chat_id, text)
        clear_state(chat_id)
        if success:
            return {"method": "sendMessage", "chat_id": chat_id, "text": "🗑️ Pianta rimossa con successo."}
        return {"method": "sendMessage", "chat_id": chat_id, "text": "⚠️ Pianta non trovata."}

    if state == "manage_plant_select":
        plant_list = get_user_plants(chat_id)
        names = [p["plant_name"] for p in plant_list]
        if text not in names:
            return {
                "method": "sendMessage",
                "chat_id": chat_id,
                "text": "❌ Il nome della pianta che hai inserito non è valido. Riprova."
            }
        # Se il nome della pianta è valido, impostiamo lo stato per la modifica
        set_state(chat_id, {"step": "manage_plant_rename", "old_name": text})
        return {"method": "sendMessage", "chat_id": chat_id, "text": "✏️ Inserisci il nuovo nome della pianta:"}

    elif isinstance(state, dict) and state.get("step") == "manage_plant_rename":
        success = rename_plant(chat_id, state["old_name"], text)
        clear_state(chat_id)
        if success:
            return {"method": "sendMessage", "chat_id": chat_id, "text": "✅ Nome modificato con successo."}
        return {"method": "sendMessage", "chat_id": chat_id, "text": "⚠️ Pianta non trovata."}



    # *** COMANDI ***
    if text == "/start":
        welcome_text = "🌱 Benvenuto nel bot Smart Plant!\n\nEcco i comandi disponibili:\n"
        available = get_available_commands(chat_id)
        welcome_text += "\n".join([f"{cmd}: {commands[cmd]}" for cmd in available])
        return {"method": "sendMessage", "chat_id": chat_id, "text": welcome_text}

    elif text == "/help":
        help_text = "📋 Comandi disponibili:\n\n"
        available = get_available_commands(chat_id)
        help_text += "\n".join([f"{cmd}: {commands[cmd]}" for cmd in available])
        return {"method": "sendMessage", "chat_id": chat_id, "text": help_text}

    elif text == "/info":
        info_text = (
            "🌿 *Smart Plant* è un sistema intelligente per monitorare e prendersi cura delle tue piante.\n\n"
            "• Monitora l'umidità del terreno\n"
            "• Ricevi notifiche automatiche\n"
            "• Automatizza l'irrigazione 🌱"
        )
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": info_text,
            "parse_mode": "Markdown"
        }

    elif text == "/assistence":
        return {"method": "sendMessage", "chat_id": chat_id, "text": "📞 Per problemi contatta l'assistenza (WIP)."}

    elif text == "/status_plant":
        return {"method": "sendMessage", "chat_id": chat_id, "text": "Qui verrà restituito lo status della pianta"}

    elif text == "/register":
        if is_logged_in(chat_id):
            return {"method": "sendMessage", "chat_id": chat_id, "text": "🔐 Sei già loggato."}
        set_state(chat_id, "register_username")
        return {"method": "sendMessage", "chat_id": chat_id, "text": "📝 Inserisci uno username per registrarti:"}

    elif text == "/login":
        if is_logged_in(chat_id):
            return {"method": "sendMessage", "chat_id": chat_id, "text": "🔐 Sei già loggato."}
        set_state(chat_id, "login_username")
        return {"method": "sendMessage", "chat_id": chat_id, "text": "🔑 Inserisci il tuo username:"}

    elif text == "/logout":
        if is_logged_in(chat_id):
            logout_user(chat_id)
            return {"method": "sendMessage", "chat_id": chat_id, "text": "🔓 Logout effettuato con successo."}
        return {"method": "sendMessage", "chat_id": chat_id, "text": "ℹ️ Non sei loggato."}

    elif text == "/add_plant":
        if not is_logged_in(chat_id):
            return {"method": "sendMessage", "chat_id": chat_id,
                    "text": "🔒 Devi essere loggato per usare questo comando."}
        set_state(chat_id, "add_plant_pot")
        return {"method": "sendMessage", "chat_id": chat_id, "text": "🔢 Inserisci l'ID dello smart pot:"}

    elif text == "/remove_plant":
        if not is_logged_in(chat_id):
            return {"method": "sendMessage", "chat_id": chat_id,
                    "text": "🔒 Devi essere loggato per usare questo comando."}
        plant_list = get_user_plants(chat_id)
        if not plant_list:
            return {"method": "sendMessage", "chat_id": chat_id, "text": "🌿 Non hai piante registrate."}
        names = [p["plant_name"] for p in plant_list]
        set_state(chat_id, "remove_plant_select")
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": "🗑️ Scegli la pianta da rimuovere:\n" + "\n".join(names)
        }

    elif text == "/manage_plant":
        if not is_logged_in(chat_id):
            return {"method": "sendMessage", "chat_id": chat_id,
                    "text": "🔒 Devi essere loggato per usare questo comando."}
        plant_list = get_user_plants(chat_id)
        if not plant_list:
            return {"method": "sendMessage", "chat_id": chat_id, "text": "🌿 Non hai piante registrate."}
        names = [p["plant_name"] for p in plant_list]
        set_state(chat_id, "manage_plant_select")
        return {
            "method": "sendMessage",
            "chat_id": chat_id,
            "text": "🛠️ Scegli la pianta da rinominare:\n" + "\n".join(names)
        }


def get_available_commands(user_id): # ottieni la lista di comandi disponibili quando usi /help
    if is_logged_in(user_id): # lista di comandi disponibili se lo user è loggato
        return [
            "/help", "/info",
            "/add_plant", "/manage_plant", "/remove_plant",
            "/logout", "/assistence", "/status_plant"
        ]
    else: # lista di comandi disponibili se lo user non è loggato
        return ["/help", "/info", "/login", "/register", "/assistence"]
