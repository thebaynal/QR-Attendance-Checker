# weather_service.py
"""Weather API service layer."""

import httpx
from typing import Dict, Optional
from mod6_labs.config import Config


# --- Custom Exceptions defined for specific error handling in main.py ---

class WeatherServiceError(Exception):
    """Base exception for issues communicating with the weather API."""
    pass

class CityNotFoundError(WeatherServiceError):
    """Raised when the API returns a 404 (city not found)."""
    pass

class NetworkError(WeatherServiceError):
    """Raised for network issues, timeouts, or connection errors."""
    pass

# -----------------------------------------------------------------------


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""
    
    def __init__(self):
        self.api_key = Config.API_KEY
        self.base_url = Config.BASE_URL
        self.timeout = Config.TIMEOUT
    
    async def get_weather(self, city: str) -> Dict:
        """
        Fetch weather data for a given city.
        
        Raises:
            CityNotFoundError: 404 response.
            NetworkError: Timeout or connection failure.
            WeatherServiceError: Other API/HTTP errors (401, 5xx, etc.).
        """
        # User Input Validation (already present but now unnecessary due to main.py validation)
        if not city:
            raise WeatherServiceError("City name cannot be empty")
        
        # Build request parameters
        params = {
            "q": city,
            "appid": self.api_key,
            "units": Config.UNITS,
        }
        
        try:
            # Make async HTTP request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                
                # --- Check for HTTP errors and raise specific exceptions ---
                
                if response.status_code == 404:
                    # Specific error for city not found
                    raise CityNotFoundError(
                        f"City '{city}' not found."
                    )
                elif response.status_code == 401:
                    # Use base WeatherServiceError for API key issues
                    raise WeatherServiceError(
                        "Invalid API key. Please check your configuration."
                    )
                elif response.status_code >= 500:
                    # Use base WeatherServiceError for server issues
                    raise WeatherServiceError(
                        f"Weather service is currently unavailable (Status {response.status_code})."
                    )
                elif response.status_code != 200:
                    # Catch other unhandled 4xx errors (e.g., 400 Bad Request)
                    raise WeatherServiceError(
                        f"Error fetching weather data: Status {response.status_code}"
                    )
                
                # Parse JSON response
                data = response.json()
                return data
                
        # --- Check for Network/Connection errors and raise specific exceptions ---

        except httpx.TimeoutException:
            # Raise NetworkError for timeouts
            raise NetworkError(
                "Request timed out. Please check your internet connection."
            )
        except httpx.NetworkError:
            # Raise NetworkError for general connection failures
            raise NetworkError(
                "Network error. Could not connect to the weather service."
            )
        except httpx.HTTPError as e:
            # Catch other httpx errors not covered above
            raise WeatherServiceError(f"HTTP error occurred: {str(e)}")
        except Exception as e:
            # Catch all remaining unexpected errors
            raise WeatherServiceError(f"An unexpected error occurred: {type(e).__name__}: {str(e)}")
    
    
    async def get_weather_by_coordinates(
        self, 
        lat: float, 
        lon: float
    ) -> Dict:
        """
        Fetch weather data by coordinates (Not used by main.py but updated for consistency).
        """
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": Config.UNITS,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                
                # Use raise_for_status for simplified error checking on this route
                response.raise_for_status() 
                
                return response.json()
                
        except httpx.NetworkError:
             raise NetworkError("Network error. Could not connect to the weather service.")
        except httpx.TimeoutException:
            raise NetworkError("Request timed out.")
        except httpx.HTTPStatusError as e:
             # Convert HTTP status errors into the base WeatherServiceError
             if e.response.status_code == 404:
                 raise CityNotFoundError("Coordinates not found.")
             raise WeatherServiceError(f"Error fetching weather data: Status {e.response.status_code}")
        except Exception as e:
            raise WeatherServiceError(f"An unexpected error occurred: {str(e)}")