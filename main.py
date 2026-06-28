from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np
import requests

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def serve_home(): return FileResponse("index.html")

@app.get("/style.css")
def serve_css(): return FileResponse("style.css")

class RadarRequest(BaseModel):
    lat: float
    lon: float

@app.post("/scan")
def get_radar_scan(req: RadarRequest):
    # 400km is approx 3.6 degrees
    span = 3.6 
    grid_size = 200 
    lats = np.linspace(req.lat - span, req.lat + span, grid_size)
    lons = np.linspace(req.lon - span, req.lon + span, grid_size)
    locations = [{"latitude": lat, "longitude": lon} for lat in lats for lon in lons]
    
    try:
        response = requests.post("https://api.open-elevation.com/api/v1/lookup", json={"locations": locations})
        elevations = np.array([item["elevation"] for item in response.json()["results"]]).reshape((grid_size, grid_size))
    except:
        elevations = np.zeros((grid_size, grid_size))

    radar_height = elevations[grid_size//2, grid_size//2] + 100 
    visibility = np.where(elevations > radar_height, 0, 1)
    return {"mask": visibility.tolist()}
