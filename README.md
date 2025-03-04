# CalcDynamics

This repository contains the code for CalcDynamics.com, a numerical solvers project that includes various differential equation solvers.

## Features

- **1D Heat Equation Solver**: Solve the heat equation in one dimension with various boundary conditions
- **1D Wave Equation Solver**: Simulate wave propagation in one dimension
- **1D Viscous Burgers Equation Solver**: Solve the nonlinear Burgers equation with viscosity
- **2D Heat Equation Solver**: Solve the heat equation in two dimensions with custom meshes and holes

## Project Structure

The project is divided into two main components:

1. **Frontend**: A React-based web interface for interacting with the solvers
2. **Backend**: A Flask API that performs the numerical calculations and returns results

### Frontend

The frontend is built with React and provides an intuitive interface for:

- Selecting the equation type (heat, wave, Burgers)
- Setting domain parameters (length, time, etc.)
- Configuring boundary conditions
- Visualizing results with interactive plots

### Backend

The backend is built with Flask and provides API endpoints for:

- Solving the 1D heat equation
- Solving the 1D wave equation
- Solving the 1D viscous Burgers equation
- Solving the 2D heat equation with custom meshes

## Technical Details

### Numerical Methods

- **Finite Difference Method**: Used for 1D heat and wave equations
- **Finite Element Method**: Used for 2D heat equation
- **Implicit Scheme**: Used for the viscous Burgers equation

### Visualization

- **Matplotlib**: Used for generating plots on the backend
- **Base64 Encoding**: Used to transfer plots to the frontend

## Development

### Prerequisites

- Node.js and npm for the frontend
- Python 3.8+ for the backend
- Required Python packages (see requirements.txt)

### Setup

1. Clone the repository
2. Set up the frontend:
   ```
   cd frontend
   npm install
   npm start
   ```
3. Set up the backend:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

## Deployment

The application is deployed using AWS Elastic Beanstalk. See DEPLOYMENT.md for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The numerical methods are based on standard finite difference and finite element techniques
- The visualization is powered by Matplotlib 