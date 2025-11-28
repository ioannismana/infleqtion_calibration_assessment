# Infleqtion Calibration Assessment

A Python-based calibration system that determines the optimal input angle for a measurement device by interacting with a REST API, collecting measurement data, fitting a Gaussian curve, and identifying the angle that produces the maximum response.

## Overview

This system uses a **wide-to-narrow search strategy** combined with **Gaussian curve fitting** to efficiently and reliably find the optimal angle for a measurement device. The solution is designed to be modular, maintainable, and production-ready.

## Features

- ✅ Efficient multi-phase search strategy (wide → fine → refinement)
- ✅ Robust Gaussian curve fitting using scipy
- ✅ Clean, modular architecture with clear separation of concerns
- ✅ Comprehensive unit tests for all components
- ✅ Detailed visualization of results with fitted curve
- ✅ Configurable parameters via centralized config
- ✅ Error handling and validation
- ✅ Type hints throughout for better code quality

## Project Structure

```
infleqtion_calibration_assessment/
├── src/
│   ├── __init__.py
│   ├── api_client.py          # HTTP communication with measurement server
│   ├── search_strategy.py     # Search algorithms to locate peak
│   ├── curve_fitting.py       # Gaussian curve fitting logic
│   ├── calibration.py         # Main orchestrator
│   └── scatter_plot.py       # Plotting and visualization
├── tests/
│   ├── __init__.py
│   ├── test_api_client.py
│   ├── test_curve_fitting.py
│   └── test_search_strategy.py
├── config.py                   # Configuration constants
├── main.py                     # Entry point
├── server.py                   # Measurement server (provided)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. **Unzip roject**

2. **Create a virtual environment**

   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**

   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Step 1: Start the Measurement Server

In one terminal, start the measurement server:

```bash
python server.py
```

The server will start on `http://localhost:8000` by default.

You can verify it's running by visiting `http://localhost:8000/` in your browser or using curl:

```bash
curl http://localhost:8000/
```

You should see: `{"status":"up"}`

### Step 2: Run the Calibration

In another terminal (with the virtual environment activated), run:

```bash
python main.py
```

### Output

The calibration process will:

1. **Check server connectivity**
2. **Execute the search strategy** (you'll see progress through each phase)
3. **Fit a Gaussian curve** to the collected data
4. **Determine the optimal angle** (to 0.1° precision)
5. **Print results to stdout**:
   ```
   Optimal Angle: 50.1°
   Measured Voltage: 98.50
   Expected Voltage: 99.23
   Total Measurements: 87
   ```
6. **Generate a plot** saved as `calibration_results_<date-time-stamp>.png` in `plots` folder.


## Configuration

Key parameters can be adjusted in `config.py`:


## Running Tests

Run all unit tests:

```bash
python -m pytest tests/
```

Or run specific test files:

```bash
python -m pytest tests/test_api_client.py
python -m pytest tests/test_curve_fitting.py
python -m pytest tests/test_search_strategy.py
```

## Architecture

### Component Responsibilities

1. **api_client.py**: Handles all HTTP communication with the measurement server
   - Status checking
   - Single measurements
   - Batch measurements
   - Measurement counting

2. **search_strategy.py**: Implements search algorithms to locate peak
   - Wide-to-narrow multi-phase search
   - Adaptive search (extensible)
   - Returns all measurements and estimated peak

3. **curve_fitting.py**: Gaussian curve fitting and analysis
   - Fits Gaussian to measurement data
   - Predicts values at any angle
   - Finds optimal angle from fitted parameters

4. **calibration.py**: Main orchestrator
   - Coordinates search and fitting
   - Validates results
   - Produces final CalibrationResult

5. **visualization.py**: Creates plots and visualizations
   - Scatter plot of measurements
   - Fitted Gaussian curve overlay
   - Optimal angle marker
