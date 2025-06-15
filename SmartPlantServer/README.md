# Smart Plant - Server Side
A project by Michele Portas and Giacomo Monni for the Internet of Things exam.

## Files description
```plaintext
SmartPlantServer/
├── app.py
├── config.py
├── .env
├── mqtt_client.py
├── logs/
├── bot/
│   ├── auth.py
│   ├── commands.py
│   ├── handler.py
│   ├── plant_manager.py
│   ├── pot_manager.py
│   ├── state_manager.py
│   └── handlers/
│       ├── utils.py
│       ├── auth/
│       │   ├── commands.py
│       │   └── states.py
│       ├── base/
│       │   └── commands.py
│       └── plant/
│           ├── commands.py
│           └── states.py
```
**.env**  
Contains the Bot Token, the webhook URL, the MongoDB URI and the MQTT URI. 
1) The Bot Token is the token provided by Telegram to manage a bot. The bot provides the user interface
necessary for the user to interact with their Nodes (that are associated to the plants).  
Telegram bot: SmartPlantIoT (https://t.me/smartplantiotbot)

2) The Webook has been made with Ngrok (https://ngrok.com/) using a free public static URL
so that Telegram can reach and send updates to the Telegram bot.  
To run Ngrok after the installation, and after you have obtained the URL:  
```ngrok http --url=URL_NGROK.app 5000```

3) MongoDB (https://www.mongodb.com/) is the database service that manage all the data about the registered users, 
the existing Nodes and the associated plants.
The MongoDB service use the localhost address with the port 27017.

4) MQTT is the communication protocol used for the communication between the users and their Nodes. 
To implement an MQTT service we installed Mosquitto (https://mosquitto.org/) and we used the localhost address to manage this service.

**config.py**  
The file is responsible for loading environment variables such as the Telegram bot token,
the webhook URL, and the MongoDB connection URI.

**mqtt_client.py**  
Create an MQTT client instance that will be used to connect and interact with the MQTT broker.

**app.py**  
This starts a Flask server to manage bidirectional communication between a Telegram bot and IoT devices using MQTT.

**logs/**  
This is the folder that contains all the log files. The logging is useful to trace every operation carried out by 
the server.

**bot/**  
This folder contains all the files for the management of the Telegram bot and its interaction with the user, 
the server and the database.



## Run instructions
1) Run the webhook in a terminal:
```ngrok http --url=mutt-growing-emu.ngrok-free.app 5000```
2) Create the MongoDB database *smartplant* and then the following collections: *pots*, *users*, *pot_data*, *plants*. 
Inside *plants*, you should create new entries following this schema (these are whitelisted pots):
    ```
    {
    "id": {...}
    "pot_id": "pot_i",
    "used": false,
    "user_id": null
    }
   ```
    Where "id" is automatically assign by the database from each new entry and for "pot_i" you should replace i with a number (e.g. pot_0)
3) Run this project using the green arrow at the top-right side of the screen.
4) Open Telegram from your computer or smartphone and search *@smartplantiotbot*.



