
# Installation guide
This guide is only for Windows OS.

## 1 - MongoDB
Install MongoDB (https://www.mongodb.com/) and create the following database and collections:  
- database: *smartplant*  
- collections: *pots*, *users*, *pot_data*, *plants_profile*, *digital_replicas*. 

Inside *pots*, you should create new entries following this schema (these are whitelisted pots):
```
    {
    "id": {...}
    "pot_id": "pot_i",
    "used": false,
    "chat_id": null
    }
```
Where "id" is automatically assign by the database from each new entry and for "pot_i" you should replace i with a number (e.g. pot_0).

## 2 - Mosquitto
Install Mosquitto (https://mosquitto.org/) to implement a local MQTT service.
After the installation, go to the installation folder and modify the configuration file:  
*C:\Program Files\mosquitto\mosquitto.conf*  
Now add at the end of the file:  
```
listener 1883  
allow_anonymous true
```

Then using powershell (in administrator mode) use this command to add a rule in the firewall:  
```
New-NetFirewallRule -DisplayName "MQTT Port 1883" -Direction Inbound -Protocol TCP -LocalPort 1883 -Action Allow
```

Restart mosquitto:  
```
net stop mosquitto
net start mosquitto
```

## 3 - Telegram
Register to telegram (https://web.telegram.org/) and create a new bot using the BotFather service. Take notes of the bot name and its token.

## 4 - Ngrok
Register and log in Ngrok webhook (https://ngrok.com/), then download the executable file.
Then choose a static domain and use this command from a terminal to link your static domain and your telegram bot:  
```
curl -F "url=YOUR_STATIC_DOMAIN/webhook" https://api.telegram.org/bot<TUO_BOT_TOKEN>/setWebhook
```

## 5 - PyCharm
Install PyCharm (https://www.jetbrains.com/pycharm/), download this project and import it.
Create a **.env** FILE and configurate it with your setup following this schema:
```
BOT_TOKEN = YOUR_TELEGRAM_TOKEN
WEBHOOK_URL = YOUR_STATIC_NGROK_URL
MONGO_URI = mongodb://localhost:27017
MQTT_URI = IP_ADDRESS_MOSQUITTO
```

# Run instructions
1) Run Mosquitto in a terminal:  
```mosquitto -v```
2) Run Ngrok in a terminal remaining in the same path of the executable file:
```ngrok http --url=YOUR_STATIC_DOMAIN FLASK_PORT```
3) Run this project with PyCharm using the green arrow at the top-right side of the screen.
4) Open Telegram from your computer or smartphone and start using your bot.

# Mosquitto guide
To simulate a sub:  
```
mosquitto_sub -h IP_HOST -t "topic"
```
 
To simulate a pub:  
```
mosquitto_pub -h IP_HOST -t "topic" -m "{\"key_name\": VALUE}"
```

For example, to simulate a 'ready' to the server:
```
mosquitto_pub -h localhost -t "smartplant/pot_0/ready" -m ""
```

To simulate a 'data' to the server:
```
mosquitto_pub -h localhost -t "smartplant/pot_0/data" -m "{\"soil_moisture_value\": 10, \"temperature_value\": 20, \"humidity_value\": 30, \"need_water\": true, \"is_irrigated\": false,  \"water_excess\": false}"
```

To simulate a 'cmd' to the node:
```
mosquitto_pub -h localhost -t "smartplant/pot_0/cmd" -m "{\"action\": 'save_parameters', \"will_rain\": false, \"soil_threshold\": 10, \"soil_max\": 20, \"temperature_range\": [20,30], \"humidity_threshold\": 30 }"
```


