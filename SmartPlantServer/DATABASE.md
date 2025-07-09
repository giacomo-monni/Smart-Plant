## MongoDB structure
MongoDB (https://www.mongodb.com/) is the database service that manage all the data about the registered users, 
the existing Nodes and the associated plants.
The MongoDB service use the localhost address with the port 27017.
```
smartplant
├── digital_replicas
├── plants_profile
├── pot_data
├── pots
└── users
```
1) **pots**: this collection contains a whitelist of admitted smart pot.  
It contains:  
    - *pot_id* that identify a Node;  
    - *used* to know if that pot is currently used by a user;  
    - *chat_id* that identify the telegram user_id that is using that pot.  

   These fields are modified when a user register or unregister a plant.
Currently, we have ten pots (from pot_0 to pot_9).


2) **users**: this collection contains the registered user and their credentials.
    - *chat_id* it's the ID connected to the user telegram account, and it's needed to identify the session;
    - *username* the username chosen by the user during the registration phase;
    - *password_hash* the hashed password that the user inserted during the registration phase;
    - *salt* the random value associated to the hashed password.
  
   Even if we trace the session and the user through the chat_id, a registration phase is required and carried out through the Telegram bot.
The reason is that in this way we can implement a future web application and the user should be able to log in through their credentials.


3) **plants_profile**: this collection contains the profile of plants registered by the users.
    - *chat_id* identifies the telegram account
    - *pot_id* identifies the node
    - *plant_name* is the plant name (must be unique for each plant of a user)
    - *soil_threshold* is the threshold of soil moisture decided by the user for their plant
    - *temperature_range* is the range of temperature decided by the user for their plant
      - *min* indicates the minimum temperature of the range
      - *max* indicates the maximum temperature of the range
    - *humidity_threshold* is the threshold of humidity decided by the user for their plant


4) **pot_data**: this collection contains the measurements carried out by the smart pots for each plant.
   - *timestamp* represents the moment when the data is inserted into the database.
   - *pot_id* identifies the node
   - *chat_id* identifies the telegram account
   - *plant_name* is the plant name
   - *humidity_value* is the humidity measurement carried out by the humidity sensor
   - *temperature_value* is the temperature measurement carried out by the temperature sensor
   - *soil_moisture_value* is the soil moisture measurement carried out by the soil moisture sensor
   - *need_water* indicates if the plant needed water after the measurements


5) **digital_replicas**: this collection contains the plant profile combined with the last measurements for a given plant. It represents the actual state of a plant.
   - *chat_id* identifies the telegram account
   - *plant_name* is the plant name
   - *pot_id* identifies the node
   - *alerts* shows possible problems in the actual plant treatment
   - *humidity_value* is the humidity measurement
   - *need_water* indicates if the plant needed water after the measurements
   - *soil_moisture_value* is the soil moisture measurement
   - *soil_threshold* is the threshold of soil moisture decided by the user for their plant
    - *temperature_range* is the range of temperature decided by the user for their plant
      - *min* indicates the minimum temperature of the range
      - *max* indicates the maximum temperature of the range
    - *humidity_threshold* is the threshold of humidity decided by the user for their plant
   - *status* indicates if the plant requires water, if it's too hot and other environmental status
   - *temperature_value* is the temperature measurement
   - *timestamp* represents the moment when the data is inserted into the database.

Note: the timestamp isn't calculated when the node carries out the measurements but when the server inserts the entry in the database.
This of course can be imprecise, but it doesn't matter since smart plant service doesn't strictly require high time precision.
