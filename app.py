from flask import Flask, request, jsonify
from config import BOT_TOKEN
from bot.handler import handle_update
import requests

app = Flask(__name__)


@app.route("/webhook", methods=["POST"]) # Webhook incaricata della connessione con Telegram
def webhook():
    update = request.get_json() # legge le risposte di telegram (sono in formato json)
    response = handle_update(update) # interpreta la risposta ottenuta eseguendo il metodo dedicato

    if response: # se l'operazione esiste ed è andata a buon fine
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/{response.pop('method')}"
        requests.post(url, json=response) # mandiamo la risposta al bot telegram

    return jsonify(success=True)


@app.route("/", methods=["GET"]) # Se visiti l'URL del server ti mostra se è attivo.
def check_server():
    return "The server is up"


if __name__ == "__main__":
    app.run(debug=True)

