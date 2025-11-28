"""
Entry point for the calibration application.
"""

import sys
from src.api_client import MeasurementClient
from src.calibration import CalibrationEngine, CalibrationResult
from src.search_strategy import CoarseToFineSearch
from src.curve_fitting import GaussianFitter
from src.scatter_plot import ResultsPlotter
from config import Config


def print_results(result: CalibrationResult) -> None:
    """
    Print calibration results to stdout.
    
    Args:
        result: CalibrationResult object
    """
    output_label = "CALIBRATION RESULTS"
    print("=" * len(output_label))  
    print(output_label)
    print("=" * len(output_label))  
    print(f"Optimal response angle: {result.optimal_angle:.1f}°")
    print(f"Measured voltage at optimal angle: {result.measured_voltage:.2f}")
    print(f"Expected voltage at optimal angle: {result.expected_voltage:.2f}")
    print(f"Total number of measurements: {result.total_measurements}")


def main() -> int:
    """
    Execute calibration steps
    
    Returns:
        Exit code (0 - success, 1 - failure)
    """
    try:
        # Initialize components
        print("Starting calibration ...")
        client = MeasurementClient(base_url=Config.SERVER_URL)
        strategy = CoarseToFineSearch()
        fitter = GaussianFitter()
        engine = CalibrationEngine(client, strategy, fitter)
        
        # Run calibration
        result: CalibrationResult = engine.calibrate()
        
        # Validate results
        if not engine.validate_result(result):
            print("\nWarning: Calibration results be unreliable.")
        
        # Print results to stdout
        print_results(result)
        
        # Generate visualization
        print("\nGenerating visualization ...")
        plotter = ResultsPlotter()
        plotter.plot_results(result, filename=Config.PLOT_FILENAME)
        
        print("\n✓ Calibration completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\nCalibration interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n✗ Error during calibration: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
5