"""
Unit tests for the GaussianFitter.
"""

import unittest
import numpy as np
from src.curve_fitting import GaussianFitter, GaussianParams
from config import Config


class TestGaussianFitter(unittest.TestCase):
    """Test cases for GaussianFitter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fitter = GaussianFitter()
    
    def test_gaussian_function(self):
        """Test the Gaussian function calculation."""
        x = np.array([50.0])
        result = self.fitter.gaussian_function(x, mu=50, sigma=10, baseline=0, amplitude=100)
        
        # At the peak (x=mu), should return amplitude
        self.assertAlmostEqual(result[0], 100.0, places=5)
    
    def test_gaussian_function_at_baseline(self):
        """Test Gaussian function far from peak."""
        x = np.array([0.0])
        result = self.fitter.gaussian_function(x, mu=50, sigma=10, baseline=5, amplitude=100)
        
        # Far from peak, should be close to baseline
        self.assertLess(result[0], 10.0)
    
    def test_fit_perfect_data(self):
        """Test fitting with perfect (noiseless) Gaussian data."""
        # Generate perfect Gaussian data
        angles = np.linspace(0, 360, 100)
        true_params = GaussianParams(mu=180, sigma=20, baseline=5, amplitude=100)
        measurements = self.fitter.gaussian_function(
            angles, true_params.mu, true_params.sigma,
            true_params.baseline, true_params.amplitude
        )
        
        # Fit the data
        fitted_params = self.fitter.fit(angles, measurements)
        
        # Check that fitted parameters are close to true parameters
        self.assertAlmostEqual(fitted_params.mu, true_params.mu, delta=5.0)
        self.assertAlmostEqual(fitted_params.sigma, true_params.sigma, delta=5.0)
        self.assertAlmostEqual(fitted_params.baseline, true_params.baseline, delta=5.0)
        self.assertAlmostEqual(fitted_params.amplitude, true_params.amplitude, delta=5.0)
    
    def test_fit_insufficient_data(self):
        """Test fitting with insufficient data points."""
        angles = np.array([10, 20, 30])
        measurements = np.array([50, 60, 55])
        
        with self.assertRaises(ValueError):
            self.fitter.fit(angles, measurements)
    
    def test_predict(self):
        """Test prediction using fitted parameters."""
        params = GaussianParams(mu=50, sigma=10, baseline=5, amplitude=100)
        
        # Predict at the peak
        prediction = self.fitter.predict(50.0, params)
        self.assertAlmostEqual(prediction, 100.0, places=5)
        
        # Predict away from peak
        prediction = self.fitter.predict(0.0, params)
        self.assertLess(prediction, 20.0)
    
    def test_find_peak(self):
        """Test finding the peak from parameters."""
        params = GaussianParams(mu=123.456, sigma=10, baseline=5, amplitude=100)
        
        optimal_angle = self.fitter.find_peak(params)
        
        # Should round to required precision
        self.assertEqual(optimal_angle, 123.5)
    
    def test_find_peak_rounding(self):
        """Test peak finding with various rounding cases."""
        test_cases = [
            (50.04, 50.0),
            (50.07, 50.1), 
            (50.14, 50.1),
            (50.16, 50.2),
        ]
        
        for input_mu, expected_angle in test_cases:
            params = GaussianParams(mu=input_mu, sigma=10, baseline=5, amplitude=100)
            optimal_angle = self.fitter.find_peak(params)
            self.assertEqual(optimal_angle, expected_angle, 
                           f"Failed for input {input_mu}: expected {expected_angle}, got {optimal_angle}")
    
    def test_generate_curve(self):
        """Test generating curve points for plotting."""
        params = GaussianParams(mu=50, sigma=10, baseline=5, amplitude=100)
        
        angles, values = self.fitter.generate_curve(params, num_points=100)
        
        self.assertEqual(len(angles), 100)
        self.assertEqual(len(values), 100)
        self.assertAlmostEqual(angles[0], Config.MIN_ANGLE)
        self.assertAlmostEqual(angles[-1], Config.MAX_ANGLE)
    
    def test_fit_with_noisy_data(self):
        """Test fitting with noisy data."""
        # Generate Gaussian data with noise
        np.random.seed(42)
        angles = np.linspace(20, 80, 50)
        true_mu = 50.0
        measurements = self.fitter.gaussian_function(
            angles, mu=true_mu, sigma=10, baseline=5, amplitude=100
        )
        # Add noise
        measurements += np.random.normal(0, 5, size=measurements.shape)
        
        # Fit the noisy data
        fitted_params = self.fitter.fit(angles, measurements)
        
        # Peak should still be close to true value
        self.assertAlmostEqual(fitted_params.mu, true_mu, delta=10.0)


if __name__ == '__main__':
    unittest.main()
