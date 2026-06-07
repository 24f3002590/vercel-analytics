from fastapi import FastAPI, Response
import json
import os
import numpy as np

app = FastAPI()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}

# Load telemetry data
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "q-vercel-latency.json")

with open(DATA_FILE, "r") as f:
    telemetry = json.load(f)


@app.options("/{path:path}")
def options_handler(path: str):
    response = Response(status_code=200)
    for k, v in CORS_HEADERS.items():
        response.headers[k] = v
    return response


@app.get("/")
def home(response: Response):
    for k, v in CORS_HEADERS.items():
        response.headers[k] = v
    return {"message": "Analytics API Running"}


@app.post("/")
def analytics(payload: dict, response: Response):

    for k, v in CORS_HEADERS.items():
        response.headers[k] = v

    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)

    region_metrics = {}

    for region in regions:
        rows = [r for r in telemetry if r["region"] == region]

        if not rows:
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        region_metrics[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 3),
            "breaches": sum(1 for x in latencies if x > threshold)
        }

    return {
        "regions": region_metrics
    }
