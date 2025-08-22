
"""
bot/handlers/plant/states.py
This module manages the states related to the plants so that the user can interact with their registration, deletion in
the database or also asks statistical data.
"""

from bot.managers.plant_manager import add_plant, remove_plant, get_user_plants
from services.service import modify_plant, info_plant, get_plant_statistics, format_plant_status_report, format_plant_statistics_report
from bot.managers.state_manager import set_state, clear_state
from bot.utils import send
from bot.managers.digital_replica_manager import get_digital_replica, modify_digital_replica


def handle_state(state, text, chat_id):  # manages the states related to the plants.
    # Adds the plant in the database, more precisely in the plants_profile collection.
    if state == "add_plant_pot":
        if len(get_user_plants(chat_id)) >= 3:
            clear_state(chat_id)
            return send(chat_id, "❌ You have already reached the maximum number of plants (3).")
        set_state(chat_id, {"step": "add_plant_name", "pot_id": text})
        return send(chat_id, "🌱 Enter the name of the plant to associate:") # Plant name

    elif isinstance(state, dict) and state.get("step") == "add_plant_name":
        state["step"] = "is_indoor"
        state["plant_name"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter: indoor or outdoor") # Indoor/outdoor choice

    elif isinstance(state, dict) and state.get("step") == "is_indoor":
        state["step"] = "add_plant_moisture"
        state["is_indoor"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the minimum soil moisture value. (e.g. 10 = 10%):") # Soil moisture threshold

    elif isinstance(state, dict) and state.get("step") == "add_plant_moisture":
        state["step"] = "add_moisture_max"
        state["soil_threshold"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the maximum soil moisture value. (e.g. 10 = 10%):") # Soil moisture max

    elif isinstance(state, dict) and state.get("step") == "add_moisture_max":
        state["step"] = "add_plant_tempmin"
        state["soil_max"] = text
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
        success, msg = add_plant(chat_id, state["pot_id"], state["plant_name"], state["is_indoor"],
                                 state["soil_threshold"], state["soil_max"], temperature_range, text)
        clear_state(chat_id)
        return send(chat_id, msg)

    # Removes the plant from the database
    elif state == "remove_plant_select":
        success = remove_plant(chat_id, text)
        clear_state(chat_id)
        return send(chat_id, "🗑️ Plant successfully removed." if success else "⚠️ Plant not found.")

    # Modifies the information related to a plant inserted during the registration phase.
    elif state == "modify_plant_select":
        plant_list = get_user_plants(chat_id)
        names = [p["plant_name"] for p in plant_list]
        if text not in names:
            clear_state(chat_id)
            return send(chat_id, "❌ The plant name is not valid.")
        set_state(chat_id, {"step": "modify_plant_name", "old_name": text}) # next state
        return send(chat_id, "✏️ Enter the new name of the plant:")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_name":
        state["step"] = "modify_plant_indoor" # next state
        state["new_name"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter: indoor or outdoor:")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_indoor":
        state["step"] = "modify_plant_moisture" # next state
        state["new_indoor"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the minimum soil moisture value. (e.g. 10 = 10%):")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_moisture":
        state["step"] = "modify_soil_max" # next state
        state["soil_threshold"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the maximum soil moisture value. (e.g. 10 = 10%):")

    elif isinstance(state, dict) and state.get("step") == "modify_soil_max":
        state["step"] = "modify_plant_tempmin" # next state
        state["soil_new_max"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the minimum temperature value. (e.g. 10 = 10°C):")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_tempmin":
        state["step"] = "modify_plant_tempmax" # next state
        state["min_temperature"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the maximum temperature value. (e.g. 10 = 10°C):")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_tempmax":
        state["step"] = "modify_plant_humidity" # next state
        state["max_temperature"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Enter the air humidity value. (e.g. 10 = 10%):")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_humidity":
        temperature_range = [state["min_temperature"], state["max_temperature"]]
        success, msg = modify_plant(chat_id, state["old_name"], state["new_name"], state["new_indoor"],
                                    state["soil_threshold"], state["soil_new_max"], temperature_range, text)

        if success: # only if plant modification OK
            modify_digital_replica(chat_id, state["old_name"], state["new_name"], state["new_indoor"],
                                   state["soil_threshold"], state["soil_new_max"], temperature_range, text)

        clear_state(chat_id)
        return send(chat_id, msg)

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

            week_report = format_plant_statistics_report(text, stats)

            return send(chat_id, week_report, markdown=True)

        except Exception as e:
            return send(chat_id, f"❌ An error occurred while retrieving the statistics: {str(e)}")

    # Returns the digital replica current data
    elif state == "status_plant_select":
        plant_list = get_user_plants(chat_id)
        names = [p["plant_name"] for p in plant_list]
        clear_state(chat_id)
        if text not in names:
            return send(chat_id, "❌ The plant name is not valid.")

        # Queries the database in order to retrieve the digital replica
        replica = get_digital_replica(chat_id, text)

        if replica is None:
            return send(chat_id, "❌ No data are available for this plant.\n"+info_plant(chat_id, text))

        # Sends the data to the user
        msg = format_plant_status_report(replica)

        return send(chat_id, msg, markdown=True)