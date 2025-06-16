## MQTT
MQTT is the communication protocol used for the communication between the users and their Nodes. 
To implement an MQTT service we installed Mosquitto (https://mosquitto.org/) and we used the localhost address to manage this service.

### Topics
1) smartplant/pot_id/data (used as smartplant/+/data)  
2) smartplant/pot_id/ready (used as smartplant/+/ready)  
3) smartplant/pot_id/cmd  

Note: with pot_id we indicate an ID associated to a Node (that we call also smart pot)

### Server Subscriber
- smartplant/pot_id/data (used as smartplant/+/data)  
- smartplant/pot_id/ready (used as smartplant/+/ready)  

Note: the + indicates a wildcard, so the server accept messages for any smart pot. 
This is okay since the server checks the validity of the pot after the server receives the message.

### Server Publisher
- smartplant/pot_id/cmd

### Description
1) **smartplant/pot_id/data:** is used by the Node to send the measurement to the server. 
The server then saves this data in the MongoDB database.
2) **smartplant/pot_id/ready:** is used by the Node to alert the server that is ready to receive thresholds information.
The Node requires threshold values in order to make decision about the irrigation.
3) **smartplant/pot_id/cmd:** is used by the server to sand data such as the threshold values required by the Node 
and to give commands to the Node to carry out a task requested by a user.

### Payload received by smartplant/pot_id/data
This data is received after the Node makes its measurements, and so it contains the light, humidity, temperature, 
soil moisture measurments and booleans that tells us if the plant needed to be irrigated and if the irrigation 
was successfully carried out.
```plaintext
{
"light_value": light_value,
"humidity_value": humidity_value,
"temperature_value": temperature_value,
"soil_moisture_value": soil_moisture,
"need_water": need_water, 
"is_irrigated": is_irrigated
}
```

### Payload received by smartplant/pot_id/ready
This topic does not contain any payload, instead it's used as a signal topic by the Node to alert the server that is ready to operate
and wants to receive the threshold values.

### Payload sent with smartplant/pot_id/cmd
Since cmd is used both for sending threshold values and user commands through the bot, we divided the payload using two actions:
*save_parameters* to send the thresholds and *get_data_now* to obtain the measurements.

When the user uses the command /get_data_now from the Telegram bot, the server sends the following payload (in json format):  
```
{
"action": "get_data_now"
}
```

When the server receives a ready message, it should send the following payload (in json format):  
```plaintext
{  
"action": "save_parameters",
"soil_threshold": soil_threshold,  
"temperature_range": temperature_range,  
"humidity_threshold": humidity_threshold  
}
```
Note: *soil_threshold*, *temperature_range* and *humidity_threshold* are data stored in the database after the user 
registers a plant.
