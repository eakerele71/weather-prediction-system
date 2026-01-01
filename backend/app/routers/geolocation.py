"""
Router for handling geolocation requests
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from typing import Optional
import os

router = APIRouter(prefix="/api/v1/geolocation", tags=["geolocation"])


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class LocationResponse(BaseModel):
    city: str
    country: str
    state: Optional[str] = None
    latitude: float
    longitude: float


@router.post("/reverse-geocode", response_model=LocationResponse)
async def reverse_geocode(coords: Coordinates):
    """
    Convert coordinates to city name using OpenWeather Geocoding API
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenWeather API key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            # OpenWeather Reverse Geocoding API
            response = await client.get(
                "http://api.openweathermap.org/geo/1.0/reverse",
                params={
                    "lat": coords.latitude,
                    "lon": coords.longitude,
                    "limit": 1,
                    "appid": api_key
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise HTTPException(
                    status_code=404,
                    detail="Could not determine location from coordinates"
                )
            
            location = data[0]
            return LocationResponse(
                city=location.get("name", "Unknown"),
                country=location.get("country", "Unknown"),
                state=location.get("state"),
                latitude=coords.latitude,
                longitude=coords.longitude
            )
    
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reverse geocode: {str(e)}"
        )


@router.get("/coords-to-city/{lat}/{lon}", response_model=LocationResponse)
async def coords_to_city(lat: float, lon: float):
    """
    Convert coordinates to city name (GET version for easier testing)
    """
    coords = Coordinates(latitude=lat, longitude=lon)
    return await reverse_geocode(coords)