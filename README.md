Calibration Optimization Assessment
=======

## Overview
This assignment is designed to evaluate your software engineering skills, approach to problem-solving, and ability to work with scientific programming concepts. The task involves interacting with a REST API server to determine the optimal input for a measurement endpoint. Your solution will serve as the core of our technical interview.

We are interested in the solution you produce, but we are more interested in how you approach the problem, how you decompose tasks, how you validate your solution, and how you think about the maintainability of the code you produce.

### File structure:
- `server.py` - this contains a FastAPI server that simulates a device requiring calibration. You will interact with this server to complete the task. *Do not modify this file*.
- `requirements.txt` - this contains the dependencies needed to run `server.py`.
- `pyproject.toml` - contains the same dependencies needed to run `server.py` for use with `uv`

### Server Endpoints

The provided server implements a small REST API with the following endpoints:

- **Root endpoint**: `/`
  - Returns a JSON object: `{"status": "up"}`. This can be used to validate that the server is running.

- **Measurement endpoint**: `/measure?angle`
  - Accepts a query parameter `angle` with numeric values between `0.0` and `360.0`.
  - Returns a measured "response" as a numeric value between `0.0` and `100.0`. This value represents a simulated voltage from a photodetector. The server adds noise to the output, but the underlying behavior is static.

The server is implemented in `server.py`. You should review the file to understand its behavior and ensure there is no malicious code. The code is intentionally not well-documented to simulate working with third-party code that you do not control.

### Goal
Your task is to create a Python module that determines the angle (input to the `/measure` endpoint) that results in the maximum output from the device (output from `/measure`). This process should:

1. **Reliably** find the optimal value in as few measurements as possible using the `/measure` endpoint.
2. Fit the data to a Gaussian curve and use that information to determine the optimal angle.

Your code can assume the `/measure` endpoint will return data with a similar shape. In other words, there will always be one peak, however the peak may shift and the width of the peak will change.


In review, we will run your code against versions of the server with different configuration and evaluate how well it performs.

While this is a toy example, we will use this to assess your ability to write modular, robust, maintainable, production code. Please ensure your code is representative of how you would handle this problem while working at Infleqtion.

### Requirements
Your implementation should produce the following outputs:

1. Print to stdout:
   - The angle that produces the optimal response.
   - The measured voltage for that angle.
   - The expected value for that angle as determined by the fitted Gaussian curve.
   - The total number of measurements taken.

2. Produce a scatter plot of the measured points:
   - The x-axis should represent the angles.
   - The y-axis should represent the measured voltages.
   - The scatter plot should include the fitted Gaussian curve.

3. Create a READEME file that explains how to use your implementation.
4. Your code should run without any modifications to `server.py`


### Constraints
- Your code should not require any additional third-party packages beyond those already listed in `requirements.txt`. If you choose to add additional packages, please explain why they are necessary.
- Your solution should be well-structured, maintainable, and easy to understand. Be sure to include appropriate unit tests.

### Getting Started
1. Create a virtual environment and install the dependencies, then activate the virtual environment.
2. Start the server by running `server.py`. You can use the following command:
   ```bash
   python server.py
   ```
   By default, the server will run on localhost:8000.

3. Verify that the server is running by testing the root endpoint (/). You can do this using a browser or curl:

    - Using a browser:
        - Open your browser and navigate to `http://localhost:8000/`. You should see a JSON response: `{"status": "up"}`.
    - Using curl:
        - Run the following command in your terminal:
        ```bash
        curl http://localhost:8000/
        ```
        - This should return the same JSON response: `{"status": "up"}`.
4. Navigate to `http://localhost:8000/docs` and play around with the end point.
5. Once you have confirmed the server is running, proceed to create your Python module to interact with the `/measure` endpoint and complete the assignment.

# FAQs

- How should we expect the underlying signal in the server to change?
   - Your code should be robust to the location of the peak, in this example the center of the distribution could be 0, 90, 180, etc. The mean and std dev might change slightly but the overall shape should be similar. There will only ever be one peak.
- Will the output range change?
   - No. The output range will always be 0.0 to 100.0. In other words, the `n` value for `binom.rvs` will not change.
- How many decimal places should we return?
   - The optimal angle should be specific to a tenth of a degree (0.1)
- What does reliable mean in this context?
   - Your solution should find the optimal angle in at least 9 out of 10 runs
- What version of Python should we use?
   - You may use any version of Python between `3.9` and `3.13`. The code server code was written using version `3.13`
- What operating system should we use?
   - You may use Windows, Mac, or Ubuntu. The server was tested on Ubuntu x86 but should run any common OS.
- Should we produce a package or wheel file?
   - You do not need to create a package or wheel file. If you would like to show your knowledge of this area, please add a few sentences as comments in your solution describing how you would approach creating a package.
- Am I allowed to use AI?
  - You are allowed to use AI. From above, "We are interested in the solution you produce, but we are more interested in how you approach the problem, how you decompose tasks, how you validate your solution, and how you think about the maintainability of the code you produce." Thus, please only use AI as a consultant. We would like for the approach and architecture to reflect your design philosophy.