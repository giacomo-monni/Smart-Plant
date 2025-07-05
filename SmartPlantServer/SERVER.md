# Smart Plant - Server Side

## Server structure
```plaintext
SmartPlantServer/
├── app.py
├── db.py
├── config.py
├── .env
├── mqtt_client.py
├── logs/
├── services/
│   └── service.py
└── bot/
    ├── auth.py
    ├── utils.py
    ├── commands.py
    ├── main_handler.py
    ├── managers/
    │   ├── digital_replica_manager.py
    │   ├── plant_manager.py
    │   ├── pot_manager.py
    │   └── state_manager.py
    └── handlers/
        ├── auth/
        │   ├── commands.py
        │   └── states.py
        ├── base/
        │   └── commands.py
        └── plant/
            ├── commands.py
            └── states.py
```
**.env**  
Contains the Bot Token, the webhook URL, the MongoDB URI and the MQTT URI. 
1) The Bot Token is the token provided by Telegram to manage a bot. The bot provides the user interface
necessary for the user to interact with their Nodes (that are associated to the plants).  
Telegram bot: SmartPlant-IoTProject (@projiotSmartPlant_bot)

2) The Webook has been made with Ngrok (https://ngrok.com/) using a free public static URL
so that Telegram can reach and send updates to the Telegram bot.

3) MongoDB (https://www.mongodb.com/) is the database service that manage all the data about the registered users, 
the existing Nodes and the associated plants.
The MongoDB service use the localhost address with the port 27017.

4) MQTT is the communication protocol used for the communication between the users and their Nodes. 
To implement an MQTT service we installed Mosquitto (https://mosquitto.org/) and we used the localhost address to manage this service.

**config.py**  
The file is responsible for loading environment variables such as the Telegram bot token,
the webhook URL, and the MongoDB connection URI.

**mqtt_client.py**  
Creates an MQTT client instance that will be used to connect and interact with the MQTT broker.

**app.py**  
This starts a Flask server to manage bidirectional communication between a Telegram bot and IoT devices using MQTT.

**db.py**  
This creates a MongoDB connection and makes the various collections available.

**logs/**  
This is the folder that contains all the log files. The logging is useful to trace every operation carried out by 
the server.

**services/**  
This folder contains service files that are functions offered to the users.

- **services/service.py**
This contains all the services offered to the user for the management of their plants.

**bot/**  
This folder contains all the files for the management of the Telegram bot and its interaction with the user, 
the server and the database.

- **bot/commands.py**  
It contains the list of all commands the bot can execute, which are shown when using the /help command, 
followed by their description.

- **bot/main_handler.py**  
It acts as the central core for managing states and commands when a message is received by the bot.
It recognizes the user and decides how to handle the received information and what to return to the user.

- **/bot/utils.py**  
It contains utility functions that support other, more central functions used by the handlers.

- **bot/auth.py**  
It handles the authentication aspect related to the database and also to register and authenticate a user.

**bot/managers/**  
This folder contains all the files that manage the various aspects of the interaction with the bot.

- **bot/managers/digital_replica_manager.py**  
Manages the functions that create and update the digital replica.

- **bot/managers/pot_manager.py**  
It contains some utility functions for managing pots, such as checking if a pot has a valid ID,
if a pot has already been used, and for marking a pot as used or making it available again.

- **bot/managers/state_manager.py**  
It implements a state machine to manage bot actions and keeps track of user sessions 
through their chat_id.

- **bot/managers/plant_manager.py**  
It handles plant management on the database side, such as inserting a plant into the database, deleting it, and modifying the parameters of the plants owned by a user.

**/bot/handlers/**
This folder contains the handlers to manage the different tasks carried out by the bot.

- **/bot/handlers/auth/**  
This folder contains the files that handle authentication commands and its process.

    - **/bot/handlers/auth/commands.py**  
It handles commands related to user registration and login.

    - **/bot/handlers/auth/states.py**  
This module manages the finite state machine transitions for user authentication processes.

- **/bot/handlers/base/**  
This folder contains the files that handle non-authentication-related commands.

    - **/bot/handlers/base/commands.py**  
This module handles the basic, non-authentication-related commands like showing all the possible commands.

- **/bot/handlers/plant/**  
This folder contains the files that handle plants management commands and their processing.

    - **/bot/handlers/plant/commands.py**  
This module handles all plant-related commands so that users can interact with their registered smart pots and manage their plants.

    - **/bot/handlers/plant/states.py**  
This module manages the states related to the plants so that the user can interact with their registration, deletion in
the database or also asks statistical data.



