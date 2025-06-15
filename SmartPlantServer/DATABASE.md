## MongoDB structure
MongoDB (https://www.mongodb.com/) is the database service that manage all the data about the registered users, 
the existing Nodes and the associated plants.
The MongoDB service use the localhost address with the port 27017.
```
smartplant
├── plants
├── pot_data
├── pots
└── users
```
1) **pots**: this collection contains a whitelist of admitted smart pot.  
It contains:  
    - *pot_id* that identify a Node;  
    - *used* to know if that pot is currently used by a user;  
    - *user_id* that identify the user_id that are using that pot.  

   These fields are modified when a user register or unregister a plant.
Currently, we have ten pots (from pot_0 to pot_9).


2) **users**: this collection contains the registered user and their credentials.
    - *chat_id* it's the ID connected to the user telegram account, and it's needed to identify the session;
    - *username* the username chosen by the user during the registration phase;
    - *password_hash* the hashed password that the user inserted during the registration phase;
    - *salt* the random value associated to the hashed password.
  
   Even if we trace the session and the user through the chat_id, a registration phase is required and carried out through the Telegram bot.
The reason is that in this way we can implement a future web application and the user should be able to log in through their credentials.


3) **plants**: this collection contains the plants registered by the users.
    - ???


4) **pot_data**: this collection contains the measurements carried out by the smart pots for each plant.
    - ???
    - the timestamp can be imprecise, but we don't care since smart plant service doesn't require strictly high precision.
