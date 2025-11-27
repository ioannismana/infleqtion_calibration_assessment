"""
API client for communicating with the measurement server.

This module handles all HTTP communication and provides a clean interface
for making measurements.
"""

import requests
from typing import List
from config import Config


class MeasurementClient:
    """Client for interacting with the measurement server API."""
    
    def __init__(self, base_url: str = Config.SERVER_URL, timeout: int = Config.SERVER_TIMEOUT):
        """
        Initialize the measurement client.
        
        Args:
            base_url: Base URL of the measurement server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._measurement_count = 0
    
    def check_server_status(self) -> bool:
        """
        Check if the server is running and responsive.
        
        Returns:
            True if server is up, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/",
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get("status") == "up"
        except requests.RequestException as e:
            print(f"Error checking server status: {e}")
            return False
    
    def measure(self, angle: float) -> float:
        """
        Take a single measurement at the specified angle.
        
        Args:
            angle: Angle in degrees (0.0 to 360.0)
            
        Returns:
            Measured voltage (0.0 to 100.0)
            
        Raises:
            ValueError: If angle is out of valid range
            requests.RequestException: If the API request fails
        """
        if not Config.MIN_ANGLE <= angle <= Config.MAX_ANGLE:
            raise ValueError(
                f"Angle must be between {Config.MIN_ANGLE} and {Config.MAX_ANGLE} degrees"
            )
        
        try:
            response = requests.get(
                f"{self.base_url}/measure",
                params={"angle": angle},
                timeout=self.timeout
            )
            response.raise_for_status()
            measurement = float(response.json())
            self._measurement_count += 1
            return measurement
        except requests.RequestException as e:
            raise requests.RequestException(f"Error measuring at angle {angle}: {e}")
    
    @property
    def total_measurements(self) -> int:
        """Get the total number of measurements taken."""
        return self._measurement_count
    
    def reset_count(self) -> None:
        """Reset the measurement counter."""
        self._measurement_count = 0
