import requests
from tabulate import tabulate

# ----------------- API MAP -----------------
API_MAP = {
    "temperature": "http://127.0.0.1:5005/temperature",
    "ppfd": "http://127.0.0.1:5005/ppfd",
    "volts": "http://127.0.0.1:5005/volts"
}

# ----------------- Insight Generator -----------------
def generate_insight(sensor_type, topic, field, value):
    if value is None:
        return f"{topic}: No data available for {field} {sensor_type}."
    
    value_str = f"{value:.2f}" if isinstance(value, float) else str(value)
    
    if sensor_type == "temperature":
        if field == "max":
            return f"{topic} recorded the highest temperature of {value_str}°C in the last 30 days — does this correlate with peak production hours?"
        elif field == "min":
            return f"{topic} observed a minimum temperature of {value_str}°C — are devices operating safely at this lower limit?"
        else:  # latest
            return f"The current temperature on {topic} is {value_str}°C — is this within the optimal range for production?"
    
    elif sensor_type == "volts":
        if field == "max":
            return f"{topic} recorded a peak voltage of {value_str}V — is this within the safe operating range?"
        elif field == "min":
            return f"Voltage dropped to a minimum of {value_str}V on {topic} — should we check the power supply stability?"
        else:  # latest
            return f"Current voltage reading on {topic} is {value_str}V — is the system stable under current load?"
    
    elif sensor_type == "ppfd":
        if field == "max":
            return f"{topic} recorded the highest PPFD of {value_str} µmol/m²/s — does this match the expected light intensity for optimal growth?"
        elif field == "min":
            return f"The lowest PPFD was {value_str} µmol/m²/s on {topic} — could this affect plant productivity?"
        else:  # latest
            return f"Latest PPFD reading is {value_str} µmol/m²/s on {topic} — is it within expected range?"
    
    else:
        return f"{topic} {field} {sensor_type}: {value_str}"

# ----------------- Main Agent Loop -----------------
print("🔹 Factory Monitoring Agent (type 'exit' to quit)")

while True:
    user_input = input("You: ").lower().strip()

    if user_input in ["exit", "quit"]:
        print("Agent: Goodbye!")
        break

    # Determine sensor type
    sensor_type = None
    for key in API_MAP.keys():
        if key in user_input:
            sensor_type = key
            break

    if not sensor_type:
        print("Agent: I can answer temperature, ppfd, or volts questions only.")
        continue

    # Determine field
    if "min" in user_input or "lowest" in user_input:
        field = "min"
        header = f"Min {sensor_type.title()}"
    elif "max" in user_input or "highest" in user_input:
        field = "max"
        header = f"Max {sensor_type.title()}"
    else:
        field = "latest"
        header = f"Latest {sensor_type.title()}"

    # Fetch data from API
    try:
        response = requests.get(API_MAP[sensor_type])
        data = response.json()
        if isinstance(data, dict) and "error" in data:
            print("Agent:", data["error"])
            continue
    except Exception as e:
        print("Agent: Could not fetch data:", e)
        continue

    # Build table
    rows = []
    for d in data:
        topic = d.get("topic", "Unknown")
        value = d.get(field)
        if isinstance(value, float):
            value = round(value, 2)
        elif value is None:
            value = "N/A"
        rows.append([topic, value])

    # Print table
    if rows:
        print(tabulate(rows, headers=["Sensor", header]))
    else:
        print(f"Agent: No {sensor_type} data available.")

    # Print discussion-style insights
    for d in data:
        topic = d.get("topic", "Unknown")
        value = d.get(field)
        print("🔹", generate_insight(sensor_type, topic, field, value))
