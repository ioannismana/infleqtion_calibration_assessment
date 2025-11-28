"""
Configuration constants for the calibration system.

This module centralizes all configuration values to avoid magic numbers
and make the system easy to tune.
"""


class Config:
    """Configuration constants for calibration."""
    
    # Server settings
    SERVER_URL: str = "http://localhost:8000"
    SERVER_TIMEOUT: int = 10  # seconds
    
    # Angle constraints
    MIN_ANGLE: float = 0.0
    MAX_ANGLE: float = 360.0
    ANGLE_PRECISION: float = 0.1  # Required precision (tenths of a degree)
    
    # Search strategy parameters
    COARSE_SCAN_STEP: float = 20.0  # Initial wide scan step size
    MEDIUM_SCAN_STEP: float = 4.0   # Medium resolution scan
    FINE_SCAN_STEP: float = 1.0     # Fine scan around peak
    REFINEMENT_STEP: float = 0.1    # Final refinement step
    
    # Search window sizes
    MEDIUM_WINDOW: float = 30.0  # Degrees around coarse peak
    FINE_WINDOW: float = 10.0    # Degrees around medium peak
    REFINEMENT_WINDOW: float = 2.0  # Degrees around fine peak
    
    # Measurement settings
    MEASUREMENTS_PER_ANGLE: int = 1  # Repeat measurements for averaging
    
    # Curve fitting
    INITIAL_SIGMA_GUESS: float = 15.0  # Initial guess for Gaussian width
    INITIAL_BASELINE_GUESS: float = 2.0  # Initial guess for baseline
    INITIAL_AMPLITUDE_GUESS: float = 100.0  # Initial guess for amplitude
    
    # Reliability
    MIN_DATA_POINTS_FOR_FIT: int = 10  # Minimum points needed for curve fitting
    
    # Visualization
    PLOT_FILE_BASE_NAME: str = "calibration_results"
    PLOT_OUTPUT_DIR: str = "results"
    PLOT_DPI: int = 300
    FIGURE_SIZE: tuple[int, int] = (10, 6)
