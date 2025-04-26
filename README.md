# Smart-Plant
Smart Plant IoT Project

## Database
MongoDB

database name: smartplant

collections: 
* plants
* pots
* users

It's not necessary to create plants and users, since it creates them automatically.
The pot must be created manually since it contains the list of admissible pot IDs.


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

NB: "_id" are automatically created by MongoDB.

## ngrok
Download ngrok, use "Deploy Static Domain" within the "Setup and Installation" tab. 
In this way a public domain is always available

To start the public server:

_ngrok http --url=<STATIC_DOMAIN_URL> \<PORT>_

Example of public server, already created:
https://mutt-growing-emu.ngrok-free.app/

\<PORT> is the same as the one used with Flask (Flask default port is 5000)

To create the webhook between ngrok and Telegram:

curl -X POST "https://api.telegram.org/botTELEGRAM_TOKEN/setWebhook" -d "url=URL_STATICO/webhook_name"

The name of the webhook must coincide with the server's one in the Python code.

## Bot telegram
Bot name: SmartPlantIoT

botname: @smartplantiotbot

## Summary

* Create the database and the pots collection.
* curl -X POST "https://api.telegram.org/botTELEGRAM_TOKEN/setWebhook" -d "url=https://mutt-growing-emu.ngrok-free.app/webhook" (the TOKEN can be taken from .env file)
* ngrok http --url=mutt-growing-emu.ngrok-free.app 5000 , uso la porta 5000 pure su flask
* Start the server

Last two points are related to the functioning of the server and the bot; the first two points are related just for the setup.

## Various information
The bot identifies each user by means of the chat_id.
The 'chat_id' is an unique identifier, i.e. it's different for each user; furthermore, even if the user uninstalls 
Telegram, changes his/her phone, deletes the chat, stops the bot, the 'chat_id' is linked to the account.
It can be used to trace users' sessions (logged-in users and not).
The user can not connect to other accounts because the server always verifies the 'chat_id' of the received message. 

Even if 'chat_id' would be sufficient, considering a possible expansion of the application as a _future work_, 
a web application, accessible from a website, can be added; for such application, it is required the insertion 
of a username and a password, in order to have a binding system between accounts of the website and the Telegram account
(in this case the Telegram bot can be also used as a MultiFactor Authentication method because it can send OTP codes).

The server allows to register a single profile per Telegram account.
This is because the 'chat_id' is unique and the insertion of username and password in a web application is just a future
implementation. If a user wants to remove his/her account or he/she wants to overcome some issues, 
it can contact the user support, which is, also, implementable in the future.

## Code structure
* app.py: starts the server and handles the webhook
* config.py: initialized environment variables (static URL, database's URI, BOT token)
* .env: contains environment variables 
* requirements.txt: it contains package dependencies
  * if using PyCharm, the IDE recognizes this file and downloads every required package.
  * if you're not using an IDE, please install the requirements with the following command:

    `pip install -r requirements.txt`


* bot/auth.py: manages the authentication on the database side
* bot/commands.py: contains the list of all the bot commands and their description
* bot/handler.py: manages the received messages from the user and sends a proper response back to the user 
* bot/plant_manager.py: manages the plants on the database side
* bot/pot_manager.py: manages the pots on the database side
* state_manager.py: contains the useful functions to trace users' session


* /bot/handlers/utils.py: contains common functions used by several files

From now on, the code is divided into three sections (auth, base, plant) depending on what the server needs to handle 
Each section has a commands.py file (responsible for recognizing and managing the command sent by the bot) 
and a states.py file (responsible for managing the user's session and the actions to be taken if a given command occurs).

* auth: responsible for user registration and login phases 
* base: responsible for base commands and how to show bot information 
* plant: responsible for managing everything related to plants

