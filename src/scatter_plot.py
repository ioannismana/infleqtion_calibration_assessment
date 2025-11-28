"""
Module for creating a scatter-plot of the calibration data points
and the fitted Gaussian curve.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional
from config import Config


class ResultsPlotter:
    """Creates plot of calibration results."""
    
    @staticmethod
    def plot_results(
        result,
        filename: str = Config.PLOT_FILENAME,
        show_plot: bool = False
    ) -> None:
        """
        Generate and save a scatter plot of calibration results.
        
        Args:
            result: CalibrationResult object with measurement data
            filename: Output filename for the plot
            show_plot: If True, display the plot interactively
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize=Config.FIGURE_SIZE)
        
        # Plot measured data points as scatter
        ax.scatter(
            result.all_angles,
            result.all_measurements,
            alpha=0.6,
            s=50,
            color='blue',
            label='Measured Data',
            zorder=3
        )
        
        # Generate and plot fitted Gaussian curve
        from src.curve_fitting import GaussianFitter
        fitter = GaussianFitter()
        curve_angles, curve_values = fitter.generate_curve(result.fitted_params)
        
        ax.plot(
            curve_angles,
            curve_values,
            color='magenta',
            linewidth=2,
            label='Fitted Gaussian Curve',
            zorder=2
        )
        
        # Mark the optimal angle
        ax.axvline(
            result.optimal_angle,
            color='green',
            linestyle='--',
            linewidth=2,
            label=f'Optimal Angle: {result.optimal_angle:.1f}°',
            zorder=1
        )
        
        # Add marker at optimal point
        ax.plot(
            result.optimal_angle,
            result.measured_voltage,
            marker='*',
            markersize=20,
            color='gold',
            markeredgecolor='black',
            markeredgewidth=1.5,
            label=f'Measured: {result.measured_voltage:.2f}V',
            zorder=4
        )
        
        # Labels and title
        ax.set_xlabel('Angle (degrees)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Measured voltage', fontsize=12, fontweight='bold')
        ax.set_title(
            'Calibration Results: Measured Data and Fitted Gaussian Curve',
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Legend
        ax.legend(loc='best', fontsize=10, framealpha=0.9)
        
        # Set axis limits
        ax.set_xlim(Config.MIN_ANGLE, Config.MAX_ANGLE)
        ax.set_ylim(-5, 105)
        
        # Add text box with key statistics
        textstr = '\n'.join([
            f'Total Measurements: {result.total_measurements}',
            f'Peak Position (μ): {result.fitted_params.mu:.2f}°',
            f'Peak Width (σ): {result.fitted_params.sigma:.2f}°',
            f'Baseline: {result.fitted_params.baseline:.2f}',
            f'Amplitude: {result.fitted_params.amplitude:.2f}'
        ])
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.3)
        ax.text(
            0.02, 0.98,
            textstr,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment='top',
            bbox=props
        )
        
        # Tight layout
        plt.tight_layout()
        
        # Save the figure
        plt.savefig(filename, dpi=Config.PLOT_DPI, bbox_inches='tight')
        print(f"\n✓ Plot saved to: {filename}")
        
        # Show plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
    