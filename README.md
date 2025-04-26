# Smart-Plant
Smart Plant IoT Project

## Database
MongoDB

database name: smartplant

collections: 
* plants
* pots
* users

plants e users non serve crearli, li crea in automatico.
pots va creato a mano in quanto contiene la lista dei pot id ammissibili.

Entry in pots:
{ 
    "id": ... , 
    "pot_id": "pot_0", 
    "used": false, 
    "user_id": null 
}

Entry in plants:
{ 
    "id": ..., 
    "user_id": xxxxx, 
    "pot_id": "pot_5", 
    "plant_name": "Rosmarino" 
}

Entry in users:
{ 
    "_id": ..., 
    "chat_id": xxxxx, 
    "username": "Test", 
    "password_hash": {
        "$binary": {
            "base64": "xxxxx",
            "subType": "00"
        }
    },
    "salt": {
        "$binary": {
            "base64": "xxxxx",
             "subType": "00"
        }
    }
}

NB: gli "_id" sono creati in automatico da MongoDB.

## ngrok
Scaricare ngrok, nella tab Setup and Installation usare deploy static domain. In questo modo si ha un dominio pubblico sempre disponibile.

Per avviare il server pubblico:

_ngrok http --url=URL_DOMINIO_STATICO PORT_

Server pubblico che ho già creato:
https://mutt-growing-emu.ngrok-free.app/

PORT sarà quella che usi su Flask. Flask di default usa la porta 5000 se non la cambi.

Per creare il webhook tra ngrok e telegram:

curl -X POST "https://api.telegram.org/botTELEGRAM_TOKEN/setWebhook" -d "url=URL_STATICO/webhook_name"

Il webhook name deve coincidere con quello del server nel codice python.

## Bot telegram
Nome bot: SmartPlantIoT

botname: @smartplantiotbot

## Summary

* Crea il database e la collection pots.
* curl -X POST "https://api.telegram.org/botTELEGRAM_TOKEN/setWebhook" -d "url=https://mutt-growing-emu.ngrok-free.app/webhook" , il TOKEN lo puoi prendere dal file .env
* ngrok http --url=mutt-growing-emu.ngrok-free.app 5000 , uso la porta 5000 pure su flask
* Avvio il server con pycharm

Per eseguire e rendere funzionante il server e il bot basta seguire sempre gli ultimi due punti. 
I primi punti sono solo per il setup.

## Info varie
Il bot identifica ogni user che lo utilizza tramite il chat_id.
Il chat_id è un identificatore unico, cioè ogni utente che usa il bot ce l'ha diverso, inoltre
non importa che telegram venga disinstallato, cambi smartphone, cancelli la chat, blocchi il bot o cambi numero di telefono,
il chat_id è legato all'account, per cui a meno che non cancelli l'account di telegram, resterà sempre lo stesso.
Per cui può essere usato per tenere traccia delle sessioni degli user (utenti loggati e non).
Lo user quindi non può connettersi ad altri account perché il server verifica sempre il chat_id del messaggio che ha ricevuto.

Anche se basterebbe la chat_id, nell'ipotetico caso di espansione dell'applicazione, si potrebbe aggiungere una web app accessibile
tramite sito web, per cui è comunque richiesto l'inserimento di uno username e password, in modo da avere un sistema di binding
tra account del sito web e account telegram (inoltre in questo caso il bot telegram può fungere da meccanismo di autenticazione multifattore
perché può mandare codici OTP).

Il server permette di registrare un solo profilo per account telegram.
Questo perché il chat_id è unico e l'inserimento di username e password al momento è solo per future implementazioni.
Nel caso lo user volesse rimuovere l'account o per altri problemi, può contattare l'assistenza, anche questo implementabile in futuro.

## Struttura codice
* app.py: avvia il server e gestisce il webhook
* config.py: inizializza le variabili d'ambiente (URL statico, URI database, BOT token)
* .env: contiene le variabili d'ambiente
* requirements.txt: contiene le dipendenze, pycharm riconosce questo file e le scarica da solo


* bot/auth.py: gestisce l'autenticazione lato database
* bot/commands.py: contiene la lista di tutti i comandi del bot e una loro descrizione
* bot/handler.py: gestisce i messaggi che riceve dall'utente e manda all'utente
* bot/plant_manager.py: si coccupa della gestione delle piante lato database
* bot/plant_manager.py: si occupa della gestione dei pot lato database
* state_manager.py: contiene le funzioni utili per tenere traccia della sessione degli utenti


* /bot/handlers/utils.py: contiene funzioni che vengono usate da altri file

Da qui in poi il codice è suddiviso in 3 sezioni (auth, base, plant) in base a cosa deve gestire il server.
Ogni sezione ha un file commands.py (incaricato di riconoscere e gestire il comando mandato dal bot) 
e un file states.py (incaricato di gestire la sessione dell'utente e le azioni da fare se avviene un dato comando).

* auth: incaricato della fase di registrazione e login dello user
* base: incaricato dei comandi base come mostare le info del bot
* plant: incaricato della gestione di tutto ciò che riguarda le piante
