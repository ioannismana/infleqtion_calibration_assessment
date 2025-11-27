"""
Main calibration engine that orchestrates the entire calibration process.

This module coordinates the search strategy, curve fitting, and result generation.
"""

from dataclasses import dataclass
import numpy as np
from typing import List
from src.api_client import MeasurementClient
from src.search_strategy import SearchStrategy, CoarseToFineSearch
from src.curve_fitting import GaussianFitter, GaussianParams
from config import Config


@dataclass
class CalibrationResult:
    """Complete results from a calibration run."""
    optimal_angle: float  # Angle that produces maximum response
    measured_voltage: float  # Actual measured voltage at optimal angle
    expected_voltage: float  # Expected voltage from fitted curve
    total_measurements: int  # Total number of measurements taken
    all_angles: np.ndarray  # All angles measured during calibration
    all_measurements: np.ndarray  # All measurements taken
    fitted_params: GaussianParams  # Fitted Gaussian parameters
    search_result: object  # Raw search result for reference
    
    def __str__(self) -> str:
        """String representation of calibration results."""
        return (
            f"Calibration Results:\n"
            f"  Optimal Angle: {self.optimal_angle:.1f}°\n"
            f"  Measured Voltage: {self.measured_voltage:.2f}\n"
            f"  Expected Voltage: {self.expected_voltage:.2f}\n"
            f"  Total Measurements: {self.total_measurements}\n"
            f"  Fitted Parameters: {self.fitted_params}"
        )


class CalibrationEngine:
    """
    Main calibration engine.
    
    Performs calibration process:
    1. Uses search strategy to collect measurements
    2. Fits Gaussian curve to data
    3. Determines optimal angle
    4. Validates results
    """
    
    def __init__(
        self,
        client: MeasurementClient,
        strategy: SearchStrategy = None,
        fitter: GaussianFitter = None
    ):
        """
        Initialize the calibration engine.
        
        Args:
            client: MeasurementClient for taking measurements
            strategy: Search strategy (defaults to CoarseToFineSearch)
            fitter: Gaussian fitter (defaults to GaussianFitter)
        """
        self.client = client
        self.strategy = strategy or CoarseToFineSearch()
        self.fitter = fitter or GaussianFitter()
    
    def calibrate(self) -> CalibrationResult:
        """
        Execute the calibration process.
        
        Returns:
            CalibrationResult with all calibration data and results
            
        Raises:
            RuntimeError: If calibration fails
        """
        print("Starting calibration ...")
        
        # Check server connectivity
        print("\nCheck server connectivity...")
        server_up: bool = self.client.check_server_status()
        if not server_up:
            raise RuntimeError("* Server is not responding")
        print("Server is running")
        
        # Execute search strategy to collect measurements
        print("\nExecute search strategy...")
        self.client.reset_count()
        search_result = self.strategy.search(self.client)
        print(f"Search complete: {search_result.total_measurements} measurements taken")
        
        # Convert to numpy arrays for fitting
        angles = np.array(search_result.angles)
        measurements = np.array(search_result.measurements)
        
        # Step 4: Fit Gaussian curve to the data
        print("\nFit Gaussian curve to data...")
        try:
            fitted_params = self.fitter.fit(angles, measurements)
            print(f"Curve fitting successful")
            print(f"{fitted_params}")
        except Exception as e:
            raise RuntimeError(f"* Curve fitting failed: {e}")
        
        # Determine optimal angle from fitted curve
        print("\nDetermining optimal angle...")
        optimal_angle = self.fitter.find_peak(fitted_params)
        print(f"Optimal angle: {optimal_angle:.1f}°")
        
        # Take actual measurement at optimal angle for verification
        print("\nStep 5: Verifying optimal angle...")
        measured_voltage = self.client.measure(optimal_angle)
        expected_voltage = self.fitter.predict(optimal_angle, fitted_params)
        print(f"Measured voltage: {measured_voltage:.2f}")
        print(f"Expected voltage: {expected_voltage:.2f}")
        print(f"Difference: {abs(measured_voltage - expected_voltage):.2f}")
        
        # Create result object
        total_measurements = self.client.total_measurements
        
        result = CalibrationResult(
            optimal_angle=optimal_angle,
            measured_voltage=measured_voltage,
            expected_voltage=expected_voltage,
            total_measurements=total_measurements,
            all_angles=angles,
            all_measurements=measurements,
            fitted_params=fitted_params,
            search_result=search_result
        )
        print("CALIBRATION DONE\n")
        
        return result
    
    def validate_result(self, result: CalibrationResult, tolerance: float = 10.0) -> bool:
        """
        Validate that the calibration result is reasonable.
        
        Args:
            result: CalibrationResult to validate
            tolerance: Maximum acceptable difference between measured and expected
            
        Returns:
            True if result is valid, False otherwise
        """
        # Check if measured and expected voltages are close
        voltage_diff = abs(result.measured_voltage - result.expected_voltage)
        
        if voltage_diff > tolerance:
            print(f"Warning: Large difference between measured ({result.measured_voltage:.2f}) "
                  f"and expected ({result.expected_voltage:.2f}) voltage")
            return False
        
        # Check if optimal angle is within valid range
        if not (Config.MIN_ANGLE <= result.optimal_angle <= Config.MAX_ANGLE):
            print(f"Warning: Optimal angle {result.optimal_angle:.1f}° is out of range")
            return False
        
        # Check if we have reasonable signal strength
        if result.measured_voltage < 50.0:
            print(f"Warning: Low signal strength at optimal angle: {result.measured_voltage:.2f}")
            return False
        
        return True
