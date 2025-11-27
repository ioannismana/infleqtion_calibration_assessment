"""
Unit tests for the MeasurementClient.
"""

import unittest
from unittest.mock import Mock, patch
import requests
from src.api_client import MeasurementClient
from config import Config


class TestMeasurementClient(unittest.TestCase):
    """Test cases for MeasurementClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = MeasurementClient()
    
    def test_initialization(self):
        """Test client initialization."""
        self.assertEqual(self.client.base_url, Config.SERVER_URL.rstrip('/'))
        self.assertEqual(self.client.timeout, Config.SERVER_TIMEOUT)
        self.assertEqual(self.client.total_measurements, 0)
    
    @patch('src.api_client.requests.get')
    def test_check_status_success(self, mock_get):
        """Test successful status check."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "up"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = self.client.check_server_status()
        
        self.assertTrue(result)
        mock_get.assert_called_once()
    
    @patch('src.api_client.requests.get')
    def test_check_status_failure(self, mock_get):
        """Test status check when server is down."""
        mock_get.side_effect = requests.RequestException("Connection failed")
        
        result = self.client.check_server_status()
        
        self.assertFalse(result)
    
    @patch('src.api_client.requests.get')
    def test_measure_success(self, mock_get):
        """Test successful measurement."""
        mock_response = Mock()
        mock_response.json.return_value = 75.5
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        measurement = self.client.measure(45.0)
        
        self.assertEqual(measurement, 75.5)
        self.assertEqual(self.client.total_measurements, 1)
    
    def test_measure_invalid_angle_low(self):
        """Test measurement with angle below valid range."""
        with self.assertRaises(ValueError):
            self.client.measure(-10.0)
    
    def test_measure_invalid_angle_high(self):
        """Test measurement with angle above valid range."""
        with self.assertRaises(ValueError):
            self.client.measure(400.0)
    
    def test_reset_count(self):
        """Test resetting measurement counter."""
        self.client._measurement_count = 10
        self.client.reset_count()
        self.assertEqual(self.client.total_measurements, 0)


if __name__ == '__main__':
    unittest.main()
