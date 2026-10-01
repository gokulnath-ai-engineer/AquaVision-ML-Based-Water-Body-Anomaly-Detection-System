"""Dataset catalogue and small clients for public environmental APIs."""

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DATASETS = [
    {
        "id": "sentinel-2-sr",
        "name": "Sentinel-2 Surface Reflectance",
        "provider": "Copernicus / Google Earth Engine",
        "kind": "multispectral satellite imagery",
        "resolution_m": 10,
        "access": "Earth Engine authentication required",
        "use": "Water indices, turbidity and algal bloom screening",
    },
    {
        "id": "landsat-8-9-l2",
        "name": "Landsat 8/9 Collection 2 Level-2",
        "provider": "USGS / Google Earth Engine",
        "kind": "thermal and multispectral satellite imagery",
        "resolution_m": 30,
        "access": "Earth Engine authentication required",
        "use": "Thermal anomaly screening and long-term trends",
    },
    {
        "id": "sentinel-1-grd",
        "name": "Sentinel-1 GRD",
        "provider": "Copernicus / Google Earth Engine",
        "kind": "C-band SAR imagery",
        "resolution_m": 10,
        "access": "Earth Engine authentication required",
        "use": "Cloud-independent water extent and flood context",
    },
    {
        "id": "jrc-global-surface-water",
        "name": "JRC Global Surface Water v1.4",
        "provider": "European Commission JRC / Google Earth Engine",
        "kind": "water occurrence and seasonality",
        "resolution_m": 30,
        "access": "Earth Engine authentication required",
        "use": "Historical water extent baseline",
    },
    {
        "id": "cpcb-nwdp",
        "name": "India water quality monitoring measurements",
        "provider": "CPCB / National Water Data Portal",
        "kind": "in-situ measurements",
        "resolution_m": None,
        "access": "Available through /api/measurements",
        "use": "Ground observations for validation and context",
    },
]


def get_open_meteo_weather(latitude: float, longitude: float) -> dict:
    """Fetch current weather context from Open-Meteo (no API key required)."""
    query = urlencode({
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "timezone": "UTC",
    })
    request = Request(
        f"https://api.open-meteo.com/v1/forecast?{query}",
        headers={"User-Agent": "AquaVision/1.0"},
    )
    with urlopen(request, timeout=15) as response:
        payload = json.load(response)
    return {
        "provider": "Open-Meteo",
        "latitude": payload.get("latitude"),
        "longitude": payload.get("longitude"),
        "timezone": payload.get("timezone"),
        "current": payload.get("current", {}),
        "units": payload.get("current_units", {}),
    }
