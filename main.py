from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from scipy.ndimage import zoom

app = FastAPI()

# Enable CORS for your frontend
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class RadarRequest(BaseModel):
    lat: float
    lon: float
    radius: int

@app.post("/scan")
def get_radar_scan(req: RadarRequest):
    # Simulate a 100x100 grid terrain matrix
    size = 100
    grid = np.linspace(-5, 5, size)
    X, Y = np.meshgrid(grid, grid)
    matrix = (np.sin(X) * np.cos(Y) * 500) + 500 
    
    # Radar Physics: Simple visibility calculation
    visibility = np.where(matrix > 600, 1, 0)
    
    return {"mask": visibility.tolist()}

# Add a simple health check for Render
@app.get("/")
def read_root():
    return {"status": "Radar API is running"}
