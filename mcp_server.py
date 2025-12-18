from fastapi import FastAPI
from fastapi.responses import JSONResponse
from influxdb_client import InfluxDBClient

# ================= CONFIG =================
INFLUX_URL = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN = "K3JKc5W5eLB3JWAtnySYHX3ClZ1P6EWvVOCB79i8SQVcrTJPVQivuYVkPZRluGEE79WnPHF9CnbcMaa1XD3jLg=="
INFLUX_ORG = "e78a1cfd926eaf45"
INFLUX_BUCKET = "Factory"
# ==========================================

app = FastAPI(title="Factory Monitoring Server")

def query_field_stats(field_name: str):
    try:
        with InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG) as client:
            query_api = client.query_api()

            # min, max, latest
            flux_min = f'''
from(bucket:"{INFLUX_BUCKET}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._field == "{field_name}")
  |> group(columns:["topic"])
  |> min()
'''
            flux_max = flux_min.replace("min()", "max()")
            flux_latest = flux_min.replace("min()", "last()")

            result_min = query_api.query(flux_min)
            result_max = query_api.query(flux_max)
            result_latest = query_api.query(flux_latest)

            data = {}
            for table in result_min:
                for record in table.records:
                    topic = record.values.get("topic", "Unknown")
                    data.setdefault(topic, {})["min"] = record.get_value()
            for table in result_max:
                for record in table.records:
                    topic = record.values.get("topic", "Unknown")
                    data.setdefault(topic, {})["max"] = record.get_value()
            for table in result_latest:
                for record in table.records:
                    topic = record.values.get("topic", "Unknown")
                    data.setdefault(topic, {})["latest"] = record.get_value()

            output = []
            for topic, vals in data.items():
                output.append({
                    "topic": topic,
                    "min": vals.get("min"),
                    "max": vals.get("max"),
                    "latest": vals.get("latest")
                })
            return output

    except Exception as e:
        return {"error": str(e)}

# Temperature endpoint (existing)
@app.get("/temperature")
def temperature_stats():
    return JSONResponse(query_field_stats("temperature"))

# PPFD endpoint
@app.get("/ppfd")
def ppfd_stats():
    return JSONResponse(query_field_stats("ppfd"))

# Volts endpoint
@app.get("/volts")
def volts_stats():
    return JSONResponse(query_field_stats("volts"))
