## Telegram Bot

### Commands
```
/help: "Shows the list of available commands"
/info: "Information about the Smart Plant project"
/assistance: "Contact support in case of issues"
/login: "Log in with username and password"
/register: "Create a new account"
/add_plant: "Add a new plant to your smart pot"
/remove_plant: "Remove an existing plant"
/modify_plant: "Edit plant parameters (name, soil, temperature, humidity)"
/info_plant: "Returns the saved plant's information"
/get_data_now: "Returns the current measurements of the plant at this exact moment"
/stat_plant: "Displays the plant's statistics for the past 7 days"
```

#### Commands available before the log in
```
/help
/info
/login
/register
/assistance
```

#### Commands available after the log in
```
/help
/info
/assistance
/add_plant
/remove_plant
/modify_plant
/info_plant
/stat_plant
/get_data_now
```

### Commands explaination

*/start* is automatically called when a user starts the bot. It simply show a welcome message and the list of possible commands.

*/help* shows the list of possible commands when the user is logged out or logged in.

*/info* shows a simple message explaining this an IoT project.

*/assistance* simply provide a contact to request help. At the moment this is not implemented and works as a placeholder.

*/register* asks the user to insert a username and a password. The credential are then stored to the database in the *users* collection.

*/login*  asks the user to insert a username e verify their existence before log them in.

*/add_plant* asks the user to insert the Smart Pot ID, the plant name, the soil moisture threshold, the temperature range, humidity threshold, and saves this data in the *plants* collection.

*/remove_plant* asks the user to insert the plant name, and it removes it from the database.

*/modify_plant* asks the user to insert the old plant name, the new plant name, the soil moisture threshold, the temperature range, humidity threshold, and modify this data in the *plants* collection.

*/info_plant* asks the user to insert the plant name, and it returns the plant thresholds.

*/stat_plant* asks the user to insert the plant name and returns the weekly statistic for that plant.

*/get_data_now* asks the user to insert the plant name to send the measurement command to.  
Measurements received using the command */get_data_now*:
```plaintext
🌱 Data received for pot {pot_id}:
🌱 Associated plant: {plant_name}
📅 Date: {timestamp_str}
📡 Light: {light_value} lux ({light_map})
💧 Air Humidity: {humidity_value}%
🌡️ Temperature: {temperature_value}°C
🌍 Soil Moisture: {soil_moisture_value}%
❓ Needed irrigation? {need_water}
✅ Was it irrigated? {is_irrigated}
``` 