from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from typing import Optional
import os
from app.config import settings

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
    Convert coordinates to city name using Google Maps Geocoding API
    """
    api_key = settings.google_maps_api_key
    if not api_key:
        raise HTTPException(status_code=500, detail="Google Maps API key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            # Google Maps Geocoding API
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "latlng": f"{coords.latitude},{coords.longitude}",
                    "key": api_key,
                    "result_type": "locality|political"
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK" or not data.get("results"):
                raise HTTPException(
                    status_code=404, 
                    detail="Could not determine location from coordinates"
                )
            
            # Parse Google Maps response
            result = data["results"][0]
            city = "Unknown"
            country = "Unknown"
            state = None
            
            for component in result.get("address_components", []):
                types = component.get("types", [])
                if "locality" in types:
                    city = component["long_name"]
                elif "country" in types:
                    country = component["long_name"]
                elif "administrative_area_level_1" in types:
                    state = component["long_name"]
            
            return LocationResponse(
                city=city,
                country=country,
                state=state,
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