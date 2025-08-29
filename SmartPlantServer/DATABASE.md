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
    - *pot_id* that identify a Node (string)
    - *used* to know if that pot is currently used by a user (boolean)  
    - *chat_id* that identify the telegram user_id that is using that pot (integer when assigned, null otherwise) 

   These fields are modified when a user register or unregister a plant.
Currently, we have ten pots (from pot_0 to pot_9).


2) **users**: this collection contains the registered user and their credentials.
    - *chat_id* it's the ID connected to the user telegram account, and it's needed to identify the session (integer)
    - *username* the username chosen by the user during the registration phase (string)
    - *location* is the registered user's city (string)
    - *password_hash* the hashed password that the user inserted during the registration phase (binary object)
    - *salt* the random value associated to the hashed password (binary object)
  
   Even if we trace the session and the user through the chat_id, a registration phase is required and carried out through the Telegram bot.
The reason is that in this way we can implement a future web application and the user should be able to log in through their credentials.


3) **plants_profile**: this collection contains the profile of plants registered by the users.
    - *chat_id* identifies the telegram account (integer)
    - *pot_id* identifies the node (string)
    - *plant_name* is the plant name (must be unique for each plant of a user) (string)
    - *soil_threshold* is the minimum threshold of soil moisture decided by the user for their plant (integer)
    - *soil_max* is the maximum soil moisture threshold, used to figure out the water excess (integer)
    - *temperature_range* is the range of temperature decided by the user for their plant (array of integers)
      - *min* indicates the minimum temperature of the range
      - *max* indicates the maximum temperature of the range
    - *humidity_threshold* is the threshold of humidity decided by the user for their plant ((integer)
    - *is_indoor* tells us if a plant is set indoor or outdoor (boolean)


4) **pot_data**: this collection contains the measurements carried out by the smart pots for each plant.
   - *timestamp* represents the moment when the data is inserted into the database (timestamp)
   - *pot_id* identifies the node (string)
   - *chat_id* identifies the telegram account (integer)
   - *plant_name* is the plant name (string)
   - *humidity_value* is the humidity measurement carried out by the humidity sensor (integer)
   - *temperature_value* is the temperature measurement carried out by the temperature sensor (integer)
   - *soil_moisture_value* is the soil moisture measurement carried out by the soil moisture sensor (integer)
   - *need_water* indicates if the plant needed water after the measurements (boolean)
   - *water_excess* indicates if the soil moisture value is higher than the maximum soil moisture threshold (boolean)
   - *is_irrigated* indicates if the plant was truly irrigated or not (boolean)


5) **digital_replicas**: this collection contains the plant profile combined with the last measurements for a given plant. It represents the actual state of a plant.
   - *chat_id* identifies the telegram account (integer)
   - *plant_name* is the plant name (string)
   - *pot_id* identifies the node (integer)
   - *alerts* shows possible problems in the actual plant treatment (array of strings)
   - *humidity_value* is the humidity measurement (integer)
   - *need_water* indicates if the plant needed water after the measurements (boolean)
   - *soil_moisture_value* is the soil moisture measurement (integer)
   - *soil_threshold* is the threshold of soil moisture decided by the user for their plant (integer)
   - *soil_max* is the maximum soil moisture threshold, used to figure out the water excess (integer)
    - *temperature_range* is the range of temperature decided by the user for their plant (array of integers)
      - *min* indicates the minimum temperature of the range
      - *max* indicates the maximum temperature of the range
    - *humidity_threshold* is the threshold of humidity decided by the user for their plant (integer)
   - *status* indicates if the plant requires water, if it's too hot and other environmental status (string)
   - *temperature_value* is the temperature measurement (integer)
   - *timestamp* represents the moment when the data is inserted into the database. (timestamp)
   - *is_indoor* tells us if a plant is set indoor or outdoor (boolean)
   - *is_irrigated* indicates if the plant was truly irrigated or not (boolean)
   - *location* is the registered user's city (string)
   - *water_excess* indicates if the soil moisture value is higher than the maximum soil moisture threshold (boolean)

Note: the timestamp isn't calculated when the node carries out the measurements but when the server inserts the entry in the database.
This of course can be imprecise, but it doesn't matter since smart plant service doesn't strictly require high time precision.
