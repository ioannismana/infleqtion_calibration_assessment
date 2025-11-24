"""Minimal server to simulate a device which requires calibration.

This file intentionally has no documentation to simulate real life examples
of third party code that we integrate with that have little to no documentation.

I not write code like this for real.
"""

import os

import numpy as np
import uvicorn
from fastapi import FastAPI
from scipy.stats import binom

app = FastAPI()


def gaussian(x: float, mu: int, sigma: int, baseline: float, amplitude: int) -> float:
    exponent = (-(((x - mu) / sigma) ** 2)) / 2
    return baseline + (amplitude - baseline) * np.exp(exponent)


def measure_response(x: float, num_measurements: int = 100) -> float:
    theoretical_signal = gaussian(
        x=x,
        mu=50,
        sigma=10,
        baseline=0.02,
        amplitude=1,
    )

    return binom.rvs(n=num_measurements, p=theoretical_signal)


@app.get("/")
def status() -> dict[str, str]:
    return {"status": "up"}


@app.get("/measure/")
def measure(angle: float = 0) -> float:
    if angle < 0.0 or angle > 360.0:
        raise ValueError("Angle must be between 0 and 360 degrees.")
    return measure_response(angle)


def main():
    port = int(os.environ.get("ASSESSMENT_PORT", 8000))
    host = os.environ.get("ASSESSMENT_HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
