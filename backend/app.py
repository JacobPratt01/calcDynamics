from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import base64
from io import BytesIO
import json
import fem_solver_2d
from mesh_generator_enhanced import generate_mesh_with_options
from fem_solver_2d import solve_heat_equation_2d
from burgers_solver import simulate_burgers
import sys
import os
import io

app = Flask(__name__)
# Enable CORS with specific configuration
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/api/health", methods=["GET"])
def health_check():
    try:
        # Check if all required modules are available
        import numpy
        import scipy
        import matplotlib
        import fem_solver_2d
        import burgers_solver
        
        # Return detailed health information
        return jsonify({
            'status': 'healthy',
            'message': 'API is running and all required modules are available',
            'modules': {
                'numpy': numpy.__version__,
                'scipy': scipy.__version__,
                'matplotlib': matplotlib.__version__
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': f'API health check failed: {str(e)}'
        }), 500

def solve_heat_equation(length, time, num_x, num_t, diffusivity, initial_temp, boundary_type='fixed', left_value=0, right_value=0):
    """
    Solve the 1D heat equation using finite differences
    u_t = alpha * u_xx
    
    boundary_type options:
    - 'fixed': Dirichlet boundary conditions (fixed values)
    - 'neumann': Neumann boundary conditions (fixed derivatives)
    - 'periodic': Periodic boundary conditions
    """
    # Spatial grid
    x = np.linspace(0, length, num_x)
    dx = x[1] - x[0]
    
    # Time grid
    t = np.linspace(0, time, num_t)
    dt = t[1] - t[0]
    
    # Initialize solution array
    u = np.zeros((num_t, num_x))
    
    # Set initial condition
    u[0, :] = initial_temp
    
    # Set boundary conditions
    if boundary_type == 'fixed':
        # Dirichlet boundary conditions (fixed values)
        u[:, 0] = left_value
        u[:, -1] = right_value
    elif boundary_type == 'neumann':
        # Neumann boundary conditions will be handled in the solver loop
        pass
    elif boundary_type == 'periodic':
        # Periodic boundary conditions will be handled in the solver loop
        pass
    else:
        return {"error": f"Unknown boundary type: {boundary_type}"}
    
    # Stability criterion
    alpha = diffusivity
    stability = alpha * dt / (dx * dx)
    
    if stability > 0.5:
        return {"error": f"Stability criterion not met. Please reduce dt or increase dx. Current value: {stability}, should be <= 0.5"}
    
    # Solve using explicit finite differences
    for n in range(0, num_t - 1):
        # Interior points
        for i in range(1, num_x - 1):
            u[n + 1, i] = u[n, i] + alpha * dt / (dx * dx) * (u[n, i + 1] - 2 * u[n, i] + u[n, i - 1])
        
        # Handle boundary conditions
        if boundary_type == 'fixed':
            # Already set above
            pass
        elif boundary_type == 'neumann':
            # Left boundary (du/dx = left_value)
            u[n + 1, 0] = u[n + 1, 1] - left_value * dx
            # Right boundary (du/dx = right_value)
            u[n + 1, -1] = u[n + 1, -2] + right_value * dx
        elif boundary_type == 'periodic':
            # Copy the second point to the last point and the second-to-last point to the first
            u[n + 1, 0] = u[n + 1, -2]
            u[n + 1, -1] = u[n + 1, 1]
    
    return {
        "x": x.tolist(),
        "t": t.tolist(),
        "u": u.tolist(),
        "boundary_type": boundary_type,
        "left_value": left_value,
        "right_value": right_value
    }

def solve_wave_equation(length, time, num_x, num_t, wave_speed, initial_displacement, initial_velocity, boundary_type='fixed', left_value=0, right_value=0):
    """
    Solve the 1D wave equation using finite differences
    u_tt = c^2 * u_xx
    
    boundary_type options:
    - 'fixed': Dirichlet boundary conditions (fixed values)
    - 'neumann': Neumann boundary conditions (fixed derivatives)
    - 'periodic': Periodic boundary conditions
    """
    # Spatial grid
    x = np.linspace(0, length, num_x)
    dx = x[1] - x[0]
    
    # Time grid
    t = np.linspace(0, time, num_t)
    dt = t[1] - t[0]
    
    # Initialize solution array
    u = np.zeros((num_t, num_x))
    
    # Set initial displacement
    u[0, :] = initial_displacement
    
    # Set boundary conditions
    if boundary_type == 'fixed':
        # Dirichlet boundary conditions (fixed values)
        u[:, 0] = left_value
        u[:, -1] = right_value
    elif boundary_type == 'neumann':
        # Neumann boundary conditions will be handled in the solver loop
        pass
    elif boundary_type == 'periodic':
        # Periodic boundary conditions will be handled in the solver loop
        pass
    else:
        return {"error": f"Unknown boundary type: {boundary_type}"}
    
    # Stability criterion
    c = wave_speed
    stability = c * dt / dx
    
    if stability > 1.0:
        return {"error": f"Stability criterion not met. Please reduce dt or increase dx. Current value: {stability}, should be <= 1.0"}
    
    # Set up second time step using initial velocity
    for i in range(1, num_x - 1):
        u[1, i] = u[0, i] + initial_velocity[i] * dt + 0.5 * c * c * dt * dt / (dx * dx) * (u[0, i + 1] - 2 * u[0, i] + u[0, i - 1])
    
    # Handle boundary conditions for the second time step
    if boundary_type == 'fixed':
        # Already set above
        pass
    elif boundary_type == 'neumann':
        # Left boundary (du/dx = left_value)
        u[1, 0] = u[1, 1] - left_value * dx
        # Right boundary (du/dx = right_value)
        u[1, -1] = u[1, -2] + right_value * dx
    elif boundary_type == 'periodic':
        # Copy the second point to the last point and the second-to-last point to the first
        u[1, 0] = u[1, -2]
        u[1, -1] = u[1, 1]
    
    # Solve using explicit finite differences
    for n in range(1, num_t - 1):
        # Interior points
        for i in range(1, num_x - 1):
            u[n + 1, i] = 2 * u[n, i] - u[n - 1, i] + c * c * dt * dt / (dx * dx) * (u[n, i + 1] - 2 * u[n, i] + u[n, i - 1])
        
        # Handle boundary conditions
        if boundary_type == 'fixed':
            # Already set above
            pass
        elif boundary_type == 'neumann':
            # Left boundary (du/dx = left_value)
            u[n + 1, 0] = u[n + 1, 1] - left_value * dx
            # Right boundary (du/dx = right_value)
            u[n + 1, -1] = u[n + 1, -2] + right_value * dx
        elif boundary_type == 'periodic':
            # Copy the second point to the last point and the second-to-last point to the first
            u[n + 1, 0] = u[n + 1, -2]
            u[n + 1, -1] = u[n + 1, 1]
    
    return {
        "x": x.tolist(),
        "t": t.tolist(),
        "u": u.tolist(),
        "boundary_type": boundary_type,
        "left_value": left_value,
        "right_value": right_value
    }

def generate_plot(x, u, t, time_indices, title):
    plt.figure(figsize=(12, 8))
    
    # Plot each selected time step with a different color and add to legend
    for idx in time_indices:
        plt.plot(x, u[idx], label=f"t = {t[idx]:.3f}")
    
    plt.title(title)
    plt.xlabel('Position (x)')
    plt.ylabel('Value (u)')
    plt.grid(True)
    plt.legend(loc='best')
    
    # Save plot to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def generate_individual_plots(x, u, t, time_indices, equation_type):
    plots = []
    
    for idx in time_indices:
        plot_data = generate_single_plot(
            x, 
            u[idx], 
            f"{equation_type.capitalize()} Equation Solution at t = {t[idx]:.3f}"
        )
        plots.append({
            "time": t[idx],
            "plot": plot_data
        })
    
    return plots

def generate_single_plot(x, u_at_time, title):
    plt.figure(figsize=(10, 6))
    plt.plot(x, u_at_time)
    plt.title(title)
    plt.xlabel('Position (x)')
    plt.ylabel('Value (u)')
    plt.grid(True)
    
    # Save plot to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

@app.route('/api/heat-equation', methods=['POST'])
def heat_equation_endpoint():
    data = request.json
    
    # Extract parameters with defaults
    length = data.get('length', 1.0)
    time = data.get('time', 0.5)
    num_x = data.get('num_x', 50)
    num_t = data.get('num_t', 1000)
    diffusivity = data.get('diffusivity', 0.01)
    
    # Extract boundary condition parameters
    boundary_type = data.get('boundary_type', 'fixed')
    left_value = data.get('left_value', 0)
    right_value = data.get('right_value', 0)
    
    # Get selected time steps or use defaults
    selected_times = data.get('selected_times', None)
    
    # Initial temperature is 0 everywhere
    initial_temp_values = np.zeros(num_x)
    
    result = solve_heat_equation(
        length, 
        time, 
        num_x, 
        num_t, 
        diffusivity, 
        initial_temp_values,
        boundary_type,
        left_value,
        right_value
    )
    
    if "error" in result:
        return jsonify(result), 400
    
    # Default time indices if none provided
    if selected_times is None:
        time_indices = [0, num_t // 4, num_t // 2, 3 * num_t // 4, num_t - 1]
    else:
        # Convert selected times to nearest indices
        time_array = np.array(result["t"])
        time_indices = [np.abs(time_array - t).argmin() for t in selected_times]
    
    # Generate individual plots
    individual_plots = generate_individual_plots(
        result["x"], 
        result["u"], 
        result["t"], 
        time_indices,
        "heat"
    )
    
    # Generate combined plot
    combined_plot = generate_plot(
        result["x"], 
        result["u"], 
        result["t"], 
        time_indices,
        "Heat Equation Solution - Multiple Time Steps"
    )
    
    # Format the response to match what the frontend expects
    return jsonify({
        "data": result,
        "plots": {
            "individual": combined_plot,  # Use combined_plot for individual view
            "animation": individual_plots[0]["plot"] if individual_plots else None  # Use first plot for animation
        },
        "selected_times": [result["t"][idx] for idx in time_indices]
    })

@app.route('/api/wave-equation', methods=['POST'])
def wave_equation_endpoint():
    data = request.json
    
    # Extract parameters with defaults
    length = data.get('length', 1.0)
    time = data.get('time', 1.0)
    num_x = data.get('num_x', 100)
    num_t = data.get('num_t', 500)
    wave_speed = data.get('wave_speed', 1.0)
    
    # Extract boundary condition parameters
    boundary_type = data.get('boundary_type', 'fixed')
    left_value = data.get('left_value', 0)
    right_value = data.get('right_value', 0)
    
    # Get selected time steps or use defaults
    selected_times = data.get('selected_times', None)
    
    # Initial displacement (sine wave)
    initial_displacement = data.get('initial_displacement', None)
    if initial_displacement is None:
        initial_displacement = np.sin(np.pi * np.linspace(0, length, num_x) / length)
    
    # Initial velocity (zero everywhere)
    initial_velocity = data.get('initial_velocity', None)
    if initial_velocity is None:
        initial_velocity = np.zeros(num_x)
    
    result = solve_wave_equation(
        length, 
        time, 
        num_x, 
        num_t, 
        wave_speed, 
        initial_displacement,
        initial_velocity,
        boundary_type,
        left_value,
        right_value
    )
    
    if "error" in result:
        return jsonify(result), 400
    
    # Default time indices if none provided
    if selected_times is None:
        time_indices = [0, num_t // 4, num_t // 2, 3 * num_t // 4, num_t - 1]
    else:
        # Convert selected times to nearest indices
        time_array = np.array(result["t"])
        time_indices = [np.abs(time_array - t).argmin() for t in selected_times]
    
    # Generate individual plots
    individual_plots = generate_individual_plots(
        result["x"], 
        result["u"], 
        result["t"], 
        time_indices,
        "wave"
    )
    
    # Generate combined plot
    combined_plot = generate_plot(
        result["x"], 
        result["u"], 
        result["t"], 
        time_indices,
        "Wave Equation Solution - Multiple Time Steps"
    )
    
    # Format the response to match what the frontend expects
    return jsonify({
        "data": result,
        "plots": {
            "individual": combined_plot,  # Use combined_plot for individual view
            "animation": individual_plots[0]["plot"] if individual_plots else None  # Use first plot for animation
        },
        "selected_times": [result["t"][idx] for idx in time_indices]
    })

@app.route('/api/heat-equation-2d', methods=['POST'])
def heat_equation_2d_endpoint():
    data = request.json
    print("Received 2D heat equation request with data:", data)
    
    # Extract parameters with defaults
    width = float(data.get('width', 10.0))
    height = float(data.get('height', 10.0))
    mesh_density = float(data.get('mesh_density', 0.01))
    mesh_quality = float(data.get('mesh_quality', 30))
    
    # Extract hole parameters
    with_holes = bool(data.get('with_holes', False))
    hole_rows = int(data.get('hole_rows', 1))
    hole_cols = int(data.get('hole_cols', 1))
    hole_radius = float(data.get('hole_radius', 0.1))
    
    print(f"Hole parameters: with_holes={with_holes}, hole_rows={hole_rows}, hole_cols={hole_cols}, hole_radius={hole_radius}")
    
    # Validate parameters
    if mesh_density <= 0:
        return jsonify({"error": "Mesh density must be positive"}), 400
    if mesh_quality <= 0:
        return jsonify({"error": "Mesh quality must be positive"}), 400
    if with_holes and (hole_rows <= 0 or hole_cols <= 0):
        return jsonify({"error": "Hole rows and columns must be positive"}), 400
    if with_holes and hole_radius <= 0:
        return jsonify({"error": "Hole radius must be positive"}), 400
    
    # Check if holes would overlap or extend beyond domain
    if with_holes:
        x_spacing = width / (hole_cols + 1)
        y_spacing = height / (hole_rows + 1)
        min_spacing = min(x_spacing, y_spacing)
        
        if hole_radius * 2 >= min_spacing:
            return jsonify({"error": f"Hole radius too large for the given domain and number of holes. Maximum radius: {min_spacing/2:.4f}"}), 400
    
    # Extract boundary condition values
    bc_values = {
        1: float(data.get('bottom_value', 0)),  # Bottom edge (y = 0)
        2: float(data.get('left_value', 0)),    # Left edge (x = 0)
        3: float(data.get('top_value', 1)),     # Top edge (y = height)
        4: float(data.get('right_value', 1)),   # Right edge (x = width)
        5: float(data.get('hole_value', 1))     # Hole boundary (if with_holes=True)
    }
    
    # Solve the 2D heat equation
    try:
        result = fem_solver_2d.solve_heat_equation_2d(
            width=width,
            height=height,
            mesh_density=mesh_density,
            mesh_quality=mesh_quality,
            bc_values=bc_values,
            with_holes=with_holes,
            hole_rows=hole_rows,
            hole_cols=hole_cols,
            hole_radius=hole_radius
        )
        return jsonify(result)
    except Exception as e:
        import traceback
        error_msg = f"Error in 2D heat equation solver: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({"error": error_msg}), 400

@app.route('/api/burgers-equation', methods=['POST'])
def burgers_equation():
    try:
        data = request.json
        print("Received Burgers equation request with data:", data)
        
        # Validate required parameters
        required_params = ['dt', 'T', 'nu', 'n_newton_iter', 'num_points', 'x_min', 'x_max', 'left_value', 'right_value', 'ic_type']
        missing_params = [param for param in required_params if param not in data]
        if missing_params:
            error_msg = f'Missing required parameters: {", ".join(missing_params)}'
            print(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Validate parameter types and values
        try:
            dt = float(data['dt'])
            T = float(data['T'])
            nu = float(data['nu'])
            n_newton_iter = int(data['n_newton_iter'])
            num_points = int(data['num_points'])
            x_min = float(data['x_min'])
            x_max = float(data['x_max'])
            left_value = float(data['left_value'])
            right_value = float(data['right_value'])
            ic_type = str(data['ic_type'])
            
            # Check for valid ranges
            if dt <= 0:
                return jsonify({'error': 'Time step (dt) must be positive'}), 400
            if T <= 0:
                return jsonify({'error': 'Final time (T) must be positive'}), 400
            if nu <= 0:
                return jsonify({'error': 'Viscosity (nu) must be positive'}), 400
            if n_newton_iter < 1:
                return jsonify({'error': 'Number of Newton iterations must be at least 1'}), 400
            if num_points < 10:
                return jsonify({'error': 'Number of points must be at least 10'}), 400
            if x_max <= x_min:
                return jsonify({'error': 'x_max must be greater than x_min'}), 400
            if ic_type not in ['step', 'sine']:
                return jsonify({'error': 'Initial condition type must be either "step" or "sine"'}), 400
                
        except ValueError as e:
            return jsonify({'error': f'Invalid parameter value: {str(e)}'}), 400
        
        # Run the simulation
        result = simulate_burgers(data)
        
        # Validate the result structure
        if not result or not isinstance(result, dict):
            return jsonify({'error': 'Simulation failed to produce valid results'}), 500
            
        if 'plots' not in result or not result['plots']:
            return jsonify({'error': 'Simulation failed to generate plots'}), 500
            
        # Return the result
        return jsonify(result)
    
    except Exception as e:
        import traceback
        error_msg = f"Error in Burgers equation solver: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 