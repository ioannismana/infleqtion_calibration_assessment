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


class CoarseToFineSearch(SearchStrategy):
    """
    Coarse-to-fine search strategy.
    
    This strategy works in multiple phases:
    1. Coarse scan: Wide spacing across full range to locate general peak area
    2. Medium scan: Medium spacing around coarse peak
    3. Fine scan: Fine spacing around medium peak  
    4. Refinement: Very fine spacing around fine peak
    
    This approach minimizes the total number of measurements while reliably
    finding the peak.
    """
    
    def __init__(self):
        """Initialize the coarse-to-fine search strategy."""
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
        Execute the coarse-to-fine search.
        
        Args:
            client: MeasurementClient instance
            
        Returns:
            SearchResult with all measurements and estimated peak
        """
        print("Starting coarse-to-fine search...")
        
        # Phase 1: Coarse scan across full range
        print(f"Phase 1: Coarse scan (step size: {Config.COARSE_SCAN_STEP}°)")
        coarse_results = self._measure_range(
            client,
            Config.MIN_ANGLE,
            Config.MAX_ANGLE,
            Config.COARSE_SCAN_STEP
        )
        coarse_peak = self._find_peak_in_results(coarse_results)
        print(f"  Coarse peak found near: {coarse_peak:.1f}°")
        
        # Phase 2: Medium scan around coarse peak
        print(f"Phase 2: Medium scan (step size: {Config.MEDIUM_SCAN_STEP}°)")
        medium_start = max(Config.MIN_ANGLE, coarse_peak - Config.MEDIUM_WINDOW / 2)
        medium_end = min(Config.MAX_ANGLE, coarse_peak + Config.MEDIUM_WINDOW / 2)
        medium_results = self._measure_range(
            client,
            medium_start,
            medium_end,
            Config.MEDIUM_SCAN_STEP
        )
        medium_peak = self._find_peak_in_results(medium_results)
        print(f"  Medium peak found near: {medium_peak:.1f}°")
        
        # Phase 3: Fine scan around medium peak
        print(f"Phase 3: Fine scan (step size: {Config.FINE_SCAN_STEP}°)")
        fine_start = max(Config.MIN_ANGLE, medium_peak - Config.FINE_WINDOW / 2)
        fine_end = min(Config.MAX_ANGLE, medium_peak + Config.FINE_WINDOW / 2)
        fine_results = self._measure_range(
            client,
            fine_start,
            fine_end,
            Config.FINE_SCAN_STEP
        )
        fine_peak = self._find_peak_in_results(fine_results)
        print(f"  Fine peak found near: {fine_peak:.1f}°")
        
        # Phase 4: Refinement scan for final precision
        print(f"Phase 4: Refinement scan (step size: {Config.REFINEMENT_STEP}°)")
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


class AdaptiveSearch(SearchStrategy):
    """
    Adaptive search strategy using golden section search.
    
    This is an alternative strategy that adapts based on measurements.
    It can be more efficient in some cases but may be less robust with noisy data.
    """
    
    def __init__(self):
        """Initialize the adaptive search strategy."""
        self.angles: List[float] = []
        self.measurements: List[float] = []
    
    def search(self, client) -> SearchResult:
        """
        Execute adaptive search.
        
        This is a placeholder for an alternative search strategy.
        Can be implemented if the coarse-to-fine approach needs improvement.
        
        Args:
            client: MeasurementClient instance
            
        Returns:
            SearchResult
        """
        # For now, fall back to coarse-to-fine
        # This could be implemented as a more sophisticated adaptive algorithm
        fallback = CoarseToFineSearch()
        return fallback.search(client)
