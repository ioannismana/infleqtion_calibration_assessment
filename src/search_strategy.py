"""
Search strategies for finding the optimal angle.

This module implements different search strategies to efficiently locate
the peak in the measurement response.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from typing import List, Tuple
from config import Config


@dataclass
class SearchResult:
    """Results from a search strategy."""
    angles: List[float]  # All angles measured
    measurements: List[float]  # Corresponding measurements
    estimated_peak_angle: float  # Best estimate of peak location
    total_measurements: int  # Total number of measurements taken


class SearchStrategy(ABC):
    """Abstract base class for search strategies."""
    
    @abstractmethod
    def search(self, client) -> SearchResult:
        """
        Execute the search strategy to find the peak.
        
        Args:
            client: MeasurementClient instance
            
        Returns:
            SearchResult with measurements and estimated peak
        """
        pass


class WideToNarrowSearch(SearchStrategy):
    """
    Wide-to-narrow search strategy.
    
    This strategy works in multiple phases:
    1. Wide scan: Wide spacing across full range to locate general peak area
    2. Medium scan: Medium spacing around wide peak
    3. Narrow scan: Fine spacing around medium peak  
    4. Refinement: Very fine spacing around fine peak
    
    This approach minimizes the total number of measurements while reliably
    finding the peak.
    """
    
    def __init__(self):
        """Initialize the wide-to-narrow search strategy."""
        self.angles: List[float] = []
        self.measurements: List[float] = []
    
    def _measure_range(self, client, start: float, end: float, step: float) -> List[Tuple[float, float]]:
        """
        Measure a range of angles with a given step size.
        
        Args:
            client: MeasurementClient instance
            start: Start angle
            end: End angle
            step: Step size between measurements
            
        Returns:
            List of (angle, measurement) tuples
        """
        angles = np.arange(start, end + step, step)
        # Ensure angles are within valid range
        angles = angles[(angles >= Config.MIN_ANGLE) & (angles <= Config.MAX_ANGLE)]
        results = []
        
        for angle in angles:
            try:
                measurement = client.measure(angle)
                results.append((angle, measurement))
                self.angles.append(angle)
                self.measurements.append(measurement)
            except Exception as e:
                print(f"Warning: Failed to measure at {angle}: {e}")
        
        return results
    
    def _find_peak_in_results(self, results: List[Tuple[float, float]]) -> float:
        """
        Find the angle with the maximum measurement in results.
        
        Args:
            results: List of (angle, measurement) tuples
            
        Returns:
            Angle with maximum measurement
        """
        if not results:
            return Config.MAX_ANGLE / 2  # Default to middle if no results
        
        max_angle, max_measurement = max(results, key=lambda x: x[1])
        return max_angle
    
    def search(self, client) -> SearchResult:
        """
        Execute an iterative search that progressively narrows.
        
        Args:
            client: MeasurementClient instance
            
        Returns:
            SearchResult with all measurements and estimated peak
        """
        print("Starting iterative search...")
        
        # Initial search parameters
        current_start = Config.MIN_ANGLE
        current_end = Config.MAX_ANGLE
        current_step = Config.INITIAL_STEP  # e.g., 10
        iteration = 1
        current_peak = None
        
        # Continue until we reach desired precision
        while current_step > Config.ANGLE_PRECISION:
            print(f"Iteration {iteration}: step size {current_step:.2f}°, "
                f"range [{current_start:.1f}°, {current_end:.1f}°]")
            
            # Measure current range
            results = self._measure_range(
                client,
                current_start,
                current_end,
                current_step
            )
            
            # Find peak in current results
            current_peak = self._find_peak_in_results(results)
            print(f"  Peak found at: {current_peak:.1f}°")
            
            # Calculate new window around peak
            window_size = (current_end - current_start) / Config.REDUCTION_FACTOR
            current_start = max(Config.MIN_ANGLE, current_peak - window_size / 2)
            current_end = min(Config.MAX_ANGLE, current_peak + window_size / 2)
            
            # Reduce step size
            current_step = current_step / Config.REDUCTION_FACTOR
            iteration += 1
        
        print(f"Final peak estimate: {current_peak:.1f}°")
        
        return SearchResult(
            angles=self.angles,
            measurements=self.measurements,
            estimated_peak_angle=current_peak,
            total_measurements=len(self.angles)
        )
