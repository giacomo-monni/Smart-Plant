
"""
bot/handlers/plant/states.py
This module manages the states related to the plants so that the user can interact with their registration, deletion in
the database or also asks statistical data.
"""

from ...plant_manager import add_plant, remove_plant, modify_plant, get_user_plants, info_plant, get_plant_statistics
from ...state_manager import set_state, clear_state
from ..utils import send
from ...digital_twins import format_plant_status_report, get_digital_twin, modify_digital_twin


def handle_state(state, text, chat_id):  # manages the states related to the plants.
    # Adds the plant in the database, more precisely in the plants collection.
    if state == "add_plant_pot":
        if len(get_user_plants(chat_id)) >= 3:
            clear_state(chat_id)
            return send(chat_id, "❌ You have already reached the maximum number of plants (3).")
        set_state(chat_id, {"step": "add_plant_name", "pot_id": text})
        return send(chat_id, "🌱 Enter the name of the plant to associate:") # Plant name

    elif isinstance(state, dict) and state.get("step") == "add_plant_name":
        state["step"] = "add_plant_moisture"
        state["plant_name"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the soil moisture value. (e.g. 10 = 10%):") # Soil moisture threshold

    elif isinstance(state, dict) and state.get("step") == "add_plant_moisture":
        state["step"] = "add_plant_tempmin"
        state["soil_threshold"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the minimum temperature value. (e.g. 10 = 10°C):") # Minimum temperature

    elif isinstance(state, dict) and state.get("step") == "add_plant_tempmin":
        state["step"] = "add_plant_tempmax"
        state["min_temperature"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the maximum temperature value. (e.g. 10 = 10°C):") # Maximum temperature

    elif isinstance(state, dict) and state.get("step") == "add_plant_tempmax":
        state["step"] = "add_plant_humidity"
        state["max_temperature"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the air humidity value. (e.g. 10 = 10%):") # Humidity

    elif isinstance(state, dict) and state.get("step") == "add_plant_humidity":
        temperature_range = [state["min_temperature"], state["max_temperature"]]
        success, msg = add_plant(chat_id, state["pot_id"], state["plant_name"], state["soil_threshold"], temperature_range, text)
        clear_state(chat_id)
        return send(chat_id, msg)


    # Removes the plant from the database
    elif state == "remove_plant_select":
        success = remove_plant(chat_id, text)
        clear_state(chat_id)
        return send(chat_id, "🗑️ Plant successfully removed." if success else "⚠️ Plant not found.")


    # Returns the information related to a plant inserted during the plant registration phase)
    elif state == "info_plant_select":
        plant_list = get_user_plants(chat_id)
        names = [p["plant_name"] for p in plant_list]
        clear_state(chat_id)
        if text not in names:
            return send(chat_id, "❌ The plant name is not valid.")
        return send(chat_id, info_plant(chat_id, text))


    # Modifies the information related to a plant inserted during the registration phase.
    elif state == "modify_plant_select":
        plant_list = get_user_plants(chat_id)
        names = [p["plant_name"] for p in plant_list]
        if text not in names:
            clear_state(chat_id)
            return send(chat_id, "❌ The plant name is not valid.")
        set_state(chat_id, {"step": "modify_plant_name", "old_name": text})
        return send(chat_id, "✏️ Enter the new name of the plant:")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_name":
        state["step"] = "modify_plant_moisture"
        state["new_name"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the soil moisture value. (e.g. 10 = 10%):")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_moisture":
        state["step"] = "modify_plant_tempmin"
        state["soil_threshold"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the minimum temperature value. (e.g. 10 = 10°C):")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_tempmin":
        state["step"] = "modify_plant_tempmax"
        state["min_temperature"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the maximum temperature value. (e.g. 10 = 10°C):")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_tempmax":
        state["step"] = "modify_plant_humidity"
        state["max_temperature"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the air humidity value. (e.g. 10 = 10%):")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_humidity":
        temperature_range = [state["min_temperature"], state["max_temperature"]]
        success, msg = modify_plant(chat_id, state["old_name"], state["new_name"], state["soil_threshold"], temperature_range, text)

        if success:
            modify_digital_twin(chat_id, state["old_name"], state["new_name"], state["soil_threshold"], temperature_range, text)

        clear_state(chat_id)
        return send(chat_id, msg)


    # # Asks the Node to execute measurements and return them to the user
    # elif state == "data_plant_select":
    #     plant_list = get_user_plants(chat_id)
    #     names = [p["plant_name"] for p in plant_list]
    #     clear_state(chat_id)
    #     if text not in names:
    #         return send(chat_id, "❌ The plant name is not valid.")
    #
    #     plant = next(p for p in plant_list if p["plant_name"] == text)
    #     pot_id = plant["pot_id"]
    #
    #     payload = {"action": "get_data_now"}
    #     topic = f"smartplant/{pot_id}/cmd"
    #
    #     if not client.is_connected():  # checks the MQTT connection
    #         return send(chat_id, "❌ There are issues with the servers, please try again later.")
    #
    #     client.publish(topic, json.dumps(payload))  # Publishes the command
    #
    #     return send(chat_id, "✅ Command sent, please wait for the response.")

    # Asks the weekly plant statistics
    elif state == "stat_plant_select":
        plant_list = get_user_plants(chat_id)
        names = [p["plant_name"] for p in plant_list]
        clear_state(chat_id)
        if text not in names:
            return send(chat_id, "❌ The plant name is not valid.")

        # Recovers the plant
        plant = next(p for p in plant_list if p["plant_name"] == text)
        pot_id = plant["pot_id"]

        try:
            stats = get_plant_statistics(pot_id)  # carries out statistic operations and returns them
            if not stats:
                return send(chat_id, "❌ No statistics are available for this plant.")

            # Weekly report formatting
            week_report = (
                f"🌱 Plant *{text}* statistics for the past week:\n\n"
                f"📅 Week from {stats['week_start']} to {stats['week_end']}\n\n"
                f"📊 Average temperature: {stats['avg_temperature']}°C\n"
                f"📈 Maximum temperature: {stats['max_temperature']}°C\n"
                f"📉 Minimum temperature: {stats['min_temperature']}°C\n"
                f"💧 Average humidity: {stats['avg_humidity']}%\n"
                f"🌿 Minimum humidity: {stats['min_humidity']}%\n"
                f"🌾 Average soil moisture: {stats['avg_soil_moisture']}%\n\n"
                f"💧 The plant was watered {stats['irrigations_count']} times in the past 7 days\n"
                f"🚱 {stats['missed_irrigations_percentage']}% of the time the plant needed watering but had no water\n\n"
                f"✅ All plant parameters remained within ideal limits for {stats['ideal_conditions_percentage']}% of the time."
            )

            return send(chat_id, week_report, markdown=True)

        except Exception as e:
            return send(chat_id, f"❌ An error occurred while retrieving the statistics: {str(e)}")


    # Returns the digital twin current data
    elif state == "status_plant_select":
        plant_list = get_user_plants(chat_id)
        names = [p["plant_name"] for p in plant_list]
        clear_state(chat_id)
        if text not in names:
            return send(chat_id, "❌ The plant name is not valid.")

        # Queries the database in order to retrieve the digital twin
        twin = get_digital_twin(chat_id, text)
        
        if twin is None:
            return send(chat_id, "❌ No data are available for this plant.")

        # Sends the data to the user
        msg = format_plant_status_report(twin)

        return send(chat_id, msg, markdown=True)