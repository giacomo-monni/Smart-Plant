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

