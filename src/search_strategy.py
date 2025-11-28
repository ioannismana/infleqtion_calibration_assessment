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
        Execute the wide-to-narrow search.
        
        Args:
            client: MeasurementClient instance
            
        Returns:
            SearchResult with all measurements and estimated peak
        """
        print("Starting wide-to-narrow search...")
        
        # Phase 1: Wide scan across full range
        print(f"Phase 1: wide scan (step size: {Config.WIDE_SCAN_STEP}°)")
        wide_results = self._measure_range(
            client,
            Config.MIN_ANGLE,
            Config.MAX_ANGLE,
            Config.WIDE_SCAN_STEP
        )
        wide_peak = self._find_peak_in_results(wide_results)
        print(f"  Wide peak found near: {wide_peak:.1f}°")
        
        # Phase 2: Narrow scan around wide peak
        print(f"Phase 2: Narrow scan (step size: {Config.NARROW_SCAN_STEP}°)")
        narrow_start = max(Config.MIN_ANGLE, wide_peak - Config.FINE_WINDOW / 2)
        narrow_end = min(Config.MAX_ANGLE, wide_peak + Config.FINE_WINDOW / 2)
        narrow_results = self._measure_range(
            client,
            narrow_start,
            narrow_end,
            Config.NARROW_SCAN_STEP
        )
        fine_peak = self._find_peak_in_results(narrow_results)
        print(f"  Narrow peak found near: {fine_peak:.1f}°")
        
        # Phase 3: Refinement scan for final precision
        print(f"Phase 3: Refinement scan (step size: {Config.REFINEMENT_STEP}°)")
        refine_start = max(Config.MIN_ANGLE, fine_peak - Config.REFINEMENT_WINDOW / 2)
        refine_end = min(Config.MAX_ANGLE, fine_peak + Config.REFINEMENT_WINDOW / 2)
        refine_results = self._measure_range(
            client,
            refine_start,
            refine_end,
            Config.REFINEMENT_STEP
        )
        final_peak = self._find_peak_in_results(refine_results)
        print(f"  Final peak estimate: {final_peak:.1f}°")
        
        return SearchResult(
            angles=self.angles,
            measurements=self.measurements,
            estimated_peak_angle=final_peak,
            total_measurements=len(self.angles)
        )

