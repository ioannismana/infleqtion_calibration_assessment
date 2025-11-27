"""
Unit tests for search strategies.
"""

import unittest
from unittest.mock import Mock
from src.search_strategy import CoarseToFineSearch, SearchResult


class TestCoarseToFineSearch(unittest.TestCase):
    """Test cases for CoarseToFineSearch."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.strategy = CoarseToFineSearch()
    
    def test_find_peak_in_results(self):
        """Test finding peak in measurement results."""
        results = [
            (10.0, 20.0),
            (20.0, 50.0),
            (30.0, 80.0),  # Peak
            (40.0, 60.0),
            (50.0, 30.0),
        ]
        
        peak_angle = self.strategy._find_peak_in_results(results)
        
        self.assertEqual(peak_angle, 30.0)
    
    def test_find_peak_empty_results(self):
        """Test finding peak with no results."""
        results = []
        
        peak_angle = self.strategy._find_peak_in_results(results)
        
        # Should return default middle value
        self.assertEqual(peak_angle, 180.0)
    
    def test_search_returns_search_result(self):
        """Test that search returns proper SearchResult."""
        # Create mock client
        mock_client = Mock()
        mock_client.measure.return_value = 50.0
        
        result = self.strategy.search(mock_client)
        
        self.assertIsInstance(result, SearchResult)
        self.assertIsInstance(result.angles, list)
        self.assertIsInstance(result.measurements, list)
        self.assertIsInstance(result.estimated_peak_angle, float)
        self.assertIsInstance(result.total_measurements, int)
    
    def test_search_collects_measurements(self):
        """Test that search actually collects measurements."""
        # Create mock client that returns increasing values near angle 50
        def mock_measure(angle):
            # Simulate a peak near 50 degrees
            distance_from_peak = abs(angle - 50)
            return max(10, 100 - distance_from_peak * 2)
        
        mock_client = Mock()
        mock_client.measure.side_effect = mock_measure
        
        result = self.strategy.search(mock_client)
        
        # Should have collected measurements
        self.assertGreater(len(result.angles), 0)
        self.assertEqual(len(result.angles), len(result.measurements))
        self.assertEqual(result.total_measurements, len(result.angles))
    
    def test_search_finds_approximate_peak(self):
        """Test that search finds a peak in the right area."""
        # Create mock client with known peak at 100 degrees
        def mock_measure(angle):
            distance_from_peak = abs(angle - 100)
            return max(5, 100 - distance_from_peak)
        
        mock_client = Mock()
        mock_client.measure.side_effect = mock_measure
        
        result = self.strategy.search(mock_client)
        
        # Should find peak near 100 degrees (within 5 degrees)
        self.assertAlmostEqual(result.estimated_peak_angle, 100.0, delta=5.0)


class TestSearchResult(unittest.TestCase):
    """Test cases for SearchResult dataclass."""
    
    def test_search_result_creation(self):
        """Test creating a SearchResult."""
        result = SearchResult(
            angles=[10.0, 20.0, 30.0],
            measurements=[50.0, 75.0, 60.0],
            estimated_peak_angle=20.0,
            total_measurements=3
        )
        
        self.assertEqual(len(result.angles), 3)
        self.assertEqual(len(result.measurements), 3)
        self.assertEqual(result.estimated_peak_angle, 20.0)
        self.assertEqual(result.total_measurements, 3)


if __name__ == '__main__':
    unittest.main()
