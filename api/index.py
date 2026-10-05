from __future__ import annotations

from statistics import mean
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

TELEMETRY = [
{"region":"apac","latency_ms":164.4,"uptime_pct":98.304},
{"region":"apac","latency_ms":143.81,"uptime_pct":98.055},
{"region":"apac","latency_ms":110.91,"uptime_pct":98.807},
{"region":"apac","latency_ms":160.65,"uptime_pct":99.17},
{"region":"apac","latency_ms":219.42,"uptime_pct":97.587},
{"region":"apac","latency_ms":161.32,"uptime_pct":98.472},
{"region":"apac","latency_ms":166.26,"uptime_pct":98.372},
{"region":"apac","latency_ms":193.64,"uptime_pct":97.96},
{"region":"apac","latency_ms":162.95,"uptime_pct":97.255},
{"region":"apac","latency_ms":185.17,"uptime_pct":97.894},
{"region":"apac","latency_ms":171.89,"uptime_pct":99.45},
{"region":"apac","latency_ms":143.46,"uptime_pct":97.382},
{"region":"emea","latency_ms":127.82,"uptime_pct":98.341},
{"region":"emea","latency_ms":192.05,"uptime_pct":98.908},
{"region":"emea","latency_ms":124.27,"uptime_pct":97.242},
{"region":"emea","latency_ms":155.25,"uptime_pct":97.809},
{"region":"emea","latency_ms":211.2,"uptime_pct":99.142},
{"region":"emea","latency_ms":206.83,"uptime_pct":98.349},
{"region":"emea","latency_ms":210.54,"uptime_pct":97.268},
{"region":"emea","latency_ms":135.33,"uptime_pct":97.127},
{"region":"emea","latency_ms":122.6,"uptime_pct":98.768},
{"region":"emea","latency_ms":185.58,"uptime_pct":97.929},
{"region":"emea","latency_ms":205.2,"uptime_pct":97.436},
{"region":"emea","latency_ms":190.39,"uptime_pct":99.025},
{"region":"amer","latency_ms":189.4,"uptime_pct":98.816},
{"region":"amer","latency_ms":155.88,"uptime_pct":97.926},
{"region":"amer","latency_ms":143.27,"uptime_pct":98.381},
{"region":"amer","latency_ms":218.26,"uptime_pct":97.12},
{"region":"amer","latency_ms":164.0,"uptime_pct":99.055},
{"region":"amer","latency_ms":222.2,"uptime_pct":99.054},
{"region":"amer","latency_ms":116.45,"uptime_pct":97.634},
{"region":"amer","latency_ms":127.77,"uptime_pct":97.602},
{"region":"amer","latency_ms":186.52,"uptime_pct":98.076},
{"region":"amer","latency_ms":200.17,"uptime_pct":98.914},
{"region":"amer","latency_ms":184.74,"uptime_pct":97.816},
{"region":"amer","latency_ms":211.69,"uptime_pct":98.853},
]

class LatencyRequest(BaseModel):
    regions: list[str] = Field(min_length=1)
    threshold_ms: float

def percentile(values: list[float], p: float) -> float:
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    rank = (len(values) - 1) * p
    lo = int(rank)
    hi = min(lo + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (rank - lo)

app = FastAPI(title="eShopCo Latency API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.post("/")
def latency_metrics(payload: LatencyRequest):
    result = {}
    for region in payload.regions:
        rows = [r for r in TELEMETRY if r["region"] == region]
        if not rows:
            raise HTTPException(404, f"Unknown region: {region}")
        latencies = [float(r["latency_ms"]) for r in rows]
        uptimes = [float(r["uptime_pct"]) for r in rows]
        result[region] = {
            "avg_latency": mean(latencies),
            "p95_latency": percentile(latencies, 0.95),
            "avg_uptime": mean(uptimes),
            "breaches": sum(x > payload.threshold_ms for x in latencies),
        }
    return result
