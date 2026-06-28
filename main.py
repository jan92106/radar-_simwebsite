from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import numpy as np
import requests

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def serve_home():
    return FileResponse("index.html")

@app.get("/style.css")
def serve_css():
    return FileResponse("style.css")

class RadarRequest(BaseModel):
    lat: float
    lon: float
    radius: int

@app.post("/scan")
def get_radar_scan(req: RadarRequest):
    # Fetch real terrain from Open-Elevation API
    grid_size = 30
    # Create a 30x30 grid centered on input lat/lon
    lats = np.linspace(req.lat - 0.2, req.lat + 0.2, grid_size)
    lons = np.linspace(req.lon - 0.2, req.lon + 0.2, grid_size)
    locations = [{"latitude": lat, "longitude": lon} for lat in lats for lon in lons]
    
    try:
        response = requests.post("https://api.open-elevation.com/api/v1/lookup", json={"locations": locations})
        results = response.json()["results"]
        elevations = np.array([item["elevation"] for item in results]).reshape((grid_size, grid_size))
    except:
        elevations = np.zeros((grid_size, grid_size))

    # Basic Radar Visibility Physics
    radar_height = elevations[grid_size//2, grid_size//2] + 100 
    visibility = np.where(elevations > radar_height, 0, 1)
    
    return {"mask": visibility.tolist()}
