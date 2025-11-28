"""
Calibration system package.

This package provides tools for calibrating measurement systems by:
- Communicating with measurement APIs
- Executing search strategies to find optimal parameters
- Fitting Gaussian curves to measurement data
- Visualizing results
"""

from src.api_client import MeasurementClient
from src.calibration import CalibrationEngine, CalibrationResult
from src.curve_fitting import GaussianFitter, GaussianParams
from src.search_strategy import SearchStrategy, CoarseToFineSearch, AdaptiveSearch
from src.scatter_plot import ResultsPlotter

__all__ = [
    'MeasurementClient',
    'CalibrationEngine',
    'CalibrationResult',
    'GaussianFitter',
    'GaussianParams',
    'SearchStrategy',
    'CoarseToFineSearch',
    'AdaptiveSearch',
    'ResultsPlotter',
]
