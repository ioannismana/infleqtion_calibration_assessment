"""
Gaussian curve fitting module.

This module handles fitting a Gaussian curve to measurement data and
determining the optimal angle from the fitted parameters.
"""

from dataclasses import dataclass
import numpy as np
from scipy.optimize import curve_fit
from typing import Tuple
from config import Config


@dataclass
class GaussianParams:
    """Parameters for a Gaussian curve."""
    mu: float  # Mean (center of peak)
    sigma: float  # Standard deviation (width)
    baseline: float  # Baseline offset
    amplitude: float  # Peak amplitude
    
    def __str__(self) -> str:
        return (f"GaussianParams(mu={self.mu:.2f}, sigma={self.sigma:.2f}, "
                f"baseline={self.baseline:.2f}, amplitude={self.amplitude:.2f})")


class GaussianFitter:
    """Fits Gaussian curves to measurement data."""
    
    @staticmethod
    def gaussian_function(x: np.ndarray, mu: float, sigma: float, 
                         baseline: float, amplitude: float) -> np.ndarray:
        """
        Gaussian function for curve fitting.
        
        Args:
            x: Input values (angles)
            mu: Mean (center)
            sigma: Standard deviation (width)
            baseline: Baseline value
            amplitude: Peak amplitude
            
        Returns:
            Gaussian function values
        """
        exponent = -((x - mu) ** 2) / (2 * sigma ** 2)
        return baseline + (amplitude - baseline) * np.exp(exponent)
    
    def fit(self, angles: np.ndarray, measurements: np.ndarray) -> GaussianParams:
        """
        Fit a Gaussian curve to the measurement data.
        
        Args:
            angles: Array of angles
            measurements: Array of corresponding measurements
            
        Returns:
            Fitted Gaussian parameters
            
        Raises:
            ValueError: If fitting fails or insufficient data
        """
        if len(angles) < Config.MIN_DATA_POINTS_FOR_FIT:
            raise ValueError(
                f"Insufficient data points for fitting. "
                f"Need at least {Config.MIN_DATA_POINTS_FOR_FIT}, got {len(angles)}"
            )
        
        # Initial parameter guesses
        max_idx = np.argmax(measurements)
        mu_guess = angles[max_idx]
        amplitude_guess = np.max(measurements)
        baseline_guess = np.min(measurements)
        sigma_guess = Config.INITIAL_SIGMA_GUESS
        
        initial_guess = [mu_guess, sigma_guess, baseline_guess, amplitude_guess]
        
        # Set bounds for parameters
        bounds = (
            [Config.MIN_ANGLE, 1.0, 0.0, 0.0],  # Lower bounds
            [Config.MAX_ANGLE, 50.0, 50.0, 110.0]  # Upper bounds
        )
        
        try:
            # Perform curve fitting
            params, _ = curve_fit(
                self.gaussian_function,
                angles,
                measurements,
                p0=initial_guess,
                bounds=bounds,
                maxfev=10000
            )
            
            mu, sigma, baseline, amplitude = params
            
            # Normalize mu to be within [0, 360]
            mu = mu % 360.0
            
            return GaussianParams(
                mu=mu,
                sigma=abs(sigma),  # Ensure positive sigma
                baseline=baseline,
                amplitude=amplitude
            )
        except Exception as e:
            raise ValueError(f"Curve fitting failed: {e}")
    
    def predict(self, angle: float, params: GaussianParams) -> float:
        """
        Predict the measurement value at a given angle using fitted parameters.
        
        Args:
            angle: Angle to predict at
            params: Fitted Gaussian parameters
            
        Returns:
            Predicted measurement value
        """
        return self.gaussian_function(
            np.array([angle]),
            params.mu,
            params.sigma,
            params.baseline,
            params.amplitude
        )[0]
    
    def find_peak(self, params: GaussianParams) -> float:
        """
        Find the angle that produces the maximum response.
        
        For a Gaussian, this is simply the mu parameter.
        
        Args:
            params: Fitted Gaussian parameters
            
        Returns:
            Optimal angle (rounded to required precision)
        """
        optimal_angle = params.mu
        # Round to required precision
        optimal_angle = round(optimal_angle / Config.ANGLE_PRECISION) * Config.ANGLE_PRECISION
        return optimal_angle
    
    def generate_curve(self, params: GaussianParams, 
                      num_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate points along the fitted Gaussian curve for plotting.
        
        Args:
            params: Fitted Gaussian parameters
            num_points: Number of points to generate
            
        Returns:
            Tuple of (angles, predicted_values)
        """
        angles = np.linspace(Config.MIN_ANGLE, Config.MAX_ANGLE, num_points)
        values = self.gaussian_function(
            angles,
            params.mu,
            params.sigma,
            params.baseline,
            params.amplitude
        )
        return angles, values
