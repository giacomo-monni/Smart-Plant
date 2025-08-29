## Telegram Bot

### Commands
```
/help: "Shows the list of available commands"
/login: "Log in with username and password"
/register: "Create a new account"
/add_plant: "Add a new plant to your smart pot"
/remove_plant: "Remove an existing plant"
/modify_plant: "Edit plant parameters (name, soil, temperature, humidity)"
/stat_plant: "Displays the plant's statistics for the past 7 days"
/status: "Displays the plant's current status"
```

#### Commands available before the log in
```
/help
/login
/register
```

#### Commands available after the log in
```
/help
/add_plant
/remove_plant
/modify_plant
/stat_plant
/status
```

### Commands explaination

*/start* is automatically called when a user starts the bot. It simply show a welcome message and the list of possible commands.

*/help* shows the list of possible commands when the user is logged out or logged in.

*/register* asks the user to insert a username and a password. The credential are then stored to the database in the *users* collection.

*/login*  asks the user to insert a username e verify their existence before log them in.

*/add_plant* asks the user to insert the Smart Pot ID, the plant name, the soil moisture threshold, the temperature range, humidity threshold, and saves this data in the *plants_profile* collection. This basically creates the profile.

*/remove_plant* asks the user to insert the plant name, and it removes it from the database.

*/modify_plant* asks the user to insert the old plant name, the new plant name, the soil moisture threshold, the temperature range, humidity threshold, and modify this data in the *plants* collection.

*/stat_plant* asks the user to insert the plant name and returns the weekly statistic for that plant.

*/status* asks the user to insert the plant name in order to give the digital replica current data.  

