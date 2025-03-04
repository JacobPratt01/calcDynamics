import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import base64
from io import BytesIO

# --------------------------------------------------
# Thomas Algorithm for a tridiagonal system
# --------------------------------------------------
def thomas_solver(a, b, c, d):
    """
    Solve a tridiagonal system A*x = d using the Thomas algorithm.
    a, b, c are the lower, main, and upper diagonals, respectively.
    d is the right-hand side vector.
    (Note: a[0] and c[-1] are not used.)
    """
    n = len(d)
    cp = np.zeros(n)  # modified upper diagonal
    dp = np.zeros(n)  # modified RHS
    cp[0] = c[0] / b[0]
    dp[0] = d[0] / b[0]
    for i in range(1, n):
        denom = b[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / denom if i < n - 1 else 0.0
        dp[i] = (d[i] - a[i] * dp[i - 1]) / denom
    x = np.zeros(n)
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x

# --------------------------------------------------
# One Newton Solve for the Implicit Time Step
# (Matching the equation: J Δu = -F, then u <- u + Δu)
# --------------------------------------------------
def newton_step(u_old, dt, dx, nu, left_value, right_value, n_iter=7):
    """
    Given u_old (the solution at time level n) and time step dt,
    perform a fixed number (n_iter) of Newton iterations to solve:
       u - u_old + dt * [(u^2/2)_x - nu * u_xx] = 0
    using centered differences in space.

    The update here matches the equation:
       [a_{i} Δu_{i-1} + b_{i} Δu_i + c_{i} Δu_{i+1}] = -F_i,
    so we solve J Δu = -F and then update u <- u + Δu.

    Returns:
      u              : updated solution at the new time level
      diag_history   : list of (||F||, ||Δu||) for each Newton iteration
      n_iter         : number of Newton iterations performed
    """
    u = u_old.copy()  # initial guess
    N = len(u)
    diag_history = []

    for it in range(n_iter):
        # Build the residual F(u)
        F = np.zeros(N)
        for i in range(1, N - 1):
            flux_diff = (u[i + 1]**2 - u[i - 1]**2) / (4 * dx)
            diff_term = (u[i + 1] - 2*u[i] + u[i - 1]) / (dx**2)
            F[i] = (u[i] - u_old[i]) + dt * flux_diff - dt * nu * diff_term

        # Compute the residual norm on the interior nodes
        F_int = F[1:N-1]
        normF = np.linalg.norm(F_int, 2)

        # Build the tridiagonal Jacobian (for interior nodes)
        n_int = N - 2
        a = np.zeros(n_int)      # sub-diagonal
        b_diag = np.zeros(n_int) # main diagonal
        c = np.zeros(n_int)      # super-diagonal

        # i = 1 (first interior node)
        i = 1
        b_diag[0] = 1 + 2 * nu * dt / (dx**2)
        c[0] = dt * (u[i+1] / (2 * dx)) - nu * dt / (dx**2)

        # i = 2,...,N-3 (middle interior nodes)
        for k in range(1, n_int-1):
            i = k + 1
            a[k] = -dt * (u[i-1] / (2 * dx)) - nu * dt / (dx**2)
            b_diag[k] = 1 + 2 * nu * dt / (dx**2)
            c[k] = dt * (u[i+1] / (2 * dx)) - nu * dt / (dx**2)

        # i = N-2 (last interior node)
        i = N - 2
        a[-1] = -dt * (u[i-1] / (2 * dx)) - nu * dt / (dx**2)
        b_diag[-1] = 1 + 2 * nu * dt / (dx**2)

        # Solve J Δu = -F_int using the Thomas algorithm
        delta = thomas_solver(a, b_diag, c, -F_int)
        norm_delta = np.linalg.norm(delta, 2)
        diag_history.append((normF, norm_delta))

        # Update: u <- u + delta (on interior nodes only)
        u[1:N-1] += delta

    return u, diag_history, n_iter

# --------------------------------------------------
# Time Integration Function
# --------------------------------------------------
def simulate_burgers(params):
    """
    Simulate the viscous Burgers equation from t=0 to t=T using
    an implicit backward-Euler time step and a fixed number of
    Newton iterations per time step.
    
    Parameters:
    - params: Dictionary containing simulation parameters
        - dt: time step
        - T: final time
        - nu: viscosity coefficient
        - n_newton_iter: number of Newton iterations per time step
        - x_min: left boundary of domain
        - x_max: right boundary of domain
        - num_points: number of grid points
        - left_value: Dirichlet BC at left boundary
        - right_value: Dirichlet BC at right boundary
        - ic_type: initial condition type ('step' or 'sine')
    
    Returns:
      Dictionary with simulation results and plots
    """
    # Extract parameters
    dt = float(params.get('dt', 0.5))
    T = float(params.get('T', 20.0))
    nu = float(params.get('nu', 0.1))
    n_newton_iter = int(params.get('n_newton_iter', 7))
    x_min = float(params.get('x_min', -10))
    x_max = float(params.get('x_max', 30))
    num_points = int(params.get('num_points', 501))
    left_value = float(params.get('left_value', 1.0))
    right_value = float(params.get('right_value', 0.0))
    ic_type = params.get('ic_type', 'step')
    
    # Set up spatial grid
    x = np.linspace(x_min, x_max, num_points)
    dx = x[1] - x[0]

    # Initial condition
    if ic_type == 'step':
        u = np.where(x <= 0, left_value, right_value)
    elif ic_type == 'sine':
        u = 0.5 * (left_value + right_value) + 0.5 * (left_value - right_value) * np.sin(np.pi * (x - x_min) / (x_max - x_min))
    else:  # Default to step
        u = np.where(x <= 0, left_value, right_value)
    
    u_all = [u.copy()]
    times = [0.0]

    n_steps = int(T / dt)
    t = 0.0
    newton_history_all = []

    # Store solutions at specific time points for visualization
    save_times = [0.0, T/4, T/2, 3*T/4, T]
    save_indices = [0]
    next_save_idx = 1

    for n in range(n_steps):
        u_old = u.copy()
        # Enforce Dirichlet BCs
        u_old[0] = left_value
        u_old[-1] = right_value

        # Perform Newton iterations for this time step
        u, newton_history, n_newton = newton_step(
            u_old, dt, dx, nu, left_value, right_value, n_iter=n_newton_iter
        )
        
        # Re-apply boundary conditions
        u[0] = left_value
        u[-1] = right_value

        t += dt
        times.append(t)
        
        if n == 0:
            newton_history_all = newton_history

        # Save solution at specific times
        if next_save_idx < len(save_times) and t >= save_times[next_save_idx]:
            save_indices.append(len(u_all))
            next_save_idx += 1
            
        u_all.append(u.copy())

    # Calculate exact solution for comparison (if using standard parameters)
    if left_value == 1.0 and right_value == 0.0:
        u_exact = 0.5 - 0.5 * np.tanh((x - 0.5 * T) / (4 * nu))
    else:
        # For custom BCs, we don't have a simple exact solution
        u_exact = None

    # Generate plots
    plots = {}
    
    # Plot final solution
    plt.figure(figsize=(10, 6))
    plt.plot(x, u, 'b-', linewidth=2, label='Numerical')
    if u_exact is not None:
        plt.plot(x, u_exact, 'r--', linewidth=2, label='Exact')
    plt.xlabel('x')
    plt.ylabel('u')
    plt.title(f'Viscous Burgers Equation at T = {T}')
    plt.legend()
    plt.grid(True)
    plt.minorticks_on()
    plt.tight_layout()
    
    # Save to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plots['final_solution'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # Plot solution at different times
    plt.figure(figsize=(10, 6))
    for idx, save_idx in enumerate(save_indices):
        t_val = times[save_idx]
        plt.plot(x, u_all[save_idx], label=f't = {t_val:.2f}')
    plt.xlabel('x')
    plt.ylabel('u')
    plt.title('Solution Evolution Over Time')
    plt.legend()
    plt.grid(True)
    plt.minorticks_on()
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plots['time_evolution'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # Plot Newton convergence history (||F||)
    plt.figure(figsize=(10, 6))
    if newton_history_all:
        iters = np.arange(1, len(newton_history_all)+1)
        norms_F = [item[0] for item in newton_history_all]
        plt.semilogy(iters, norms_F, marker='o', color='blue', label='Residual Norm')
    plt.xlabel('Newton iteration')
    plt.ylabel('Residual Norm')
    plt.title('Newton Convergence (Residual Norm)')
    plt.legend()
    plt.grid(True)
    plt.minorticks_on()
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plots['residual_norm'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # Plot Newton convergence history (||Δu||)
    plt.figure(figsize=(10, 6))
    if newton_history_all:
        iters = np.arange(1, len(newton_history_all)+1)
        norms_du = [item[1] for item in newton_history_all]
        plt.semilogy(iters, norms_du, marker='s', color='red', label='Update Norm')
    plt.xlabel('Newton iteration')
    plt.ylabel('Update Norm')
    plt.title('Newton Convergence (Update Norm)')
    plt.legend()
    plt.grid(True)
    plt.minorticks_on()
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plots['update_norm'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    # Return results
    return {
        'plots': {
            'waterfall': plots.get('time_evolution', ''),
            'animation': plots.get('final_solution', ''),
            'individual': plots.get('time_evolution', '')
        },
        'parameters': {
            'dt': dt,
            'T': T,
            'nu': nu,
            'n_newton_iter': n_newton_iter,
            'dx': dx,
            'num_points': num_points,
            'left_value': left_value,
            'right_value': right_value
        },
        'statistics': {
            'max_residual': max([item[0] for item in newton_history_all]) if newton_history_all else None,
            'min_residual': min([item[0] for item in newton_history_all]) if newton_history_all else None,
            'newton_iterations': n_newton_iter,
            'time_steps': n_steps
        }
    } 