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
    
    def check_status(self) -> bool:
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
    
    def measure_batch(self, angles: List[float]) -> List[tuple[float, float]]:
        """
        Take measurements at multiple angles.
        
        Args:
            angles: List of angles to measure
            
        Returns:
            List of (angle, measurement) tuples
        """
        results = []
        for angle in angles:
            try:
                measurement = self.measure(angle)
                results.append((angle, measurement))
            except Exception as e:
                print(f"Warning: Failed to measure at angle {angle}: {e}")
        return results
    
    def measure_with_averaging(self, angle: float, num_samples: int = Config.MEASUREMENTS_PER_ANGLE) -> float:
        """
        Take multiple measurements at an angle and return the average.
        
        This can help reduce noise in the measurements.
        
        Args:
            angle: Angle to measure
            num_samples: Number of measurements to average
            
        Returns:
            Average measurement value
        """
        measurements = []
        for _ in range(num_samples):
            measurements.append(self.measure(angle))
        return sum(measurements) / len(measurements)
    
    @property
    def total_measurements(self) -> int:
        """Get the total number of measurements taken."""
        return self._measurement_count
    
    def reset_count(self) -> None:
        """Reset the measurement counter."""
        self._measurement_count = 0
