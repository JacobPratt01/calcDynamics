import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import mesh_generator_enhanced as mesh_generator


def lagrange_basis_functions():
    r, s = sp.symbols('r s')
    N1 = 1 - r - s
    N2 = r
    N3 = s
    N1_dr = -1
    N1_ds = -1
    N2_dr = 1
    N2_ds = 0
    N3_dr = 0
    N3_ds = 1
    return (N1, N2, N3), ((N1_dr, N1_ds), (N2_dr, N2_ds), (N3_dr, N3_ds))


def jacobian_matrix(v1, v2, v3, derivatives):
    x1, y1 = v1
    x2, y2 = v2
    x3, y3 = v3

    dN1_dr, dN1_ds = derivatives[0]
    dN2_dr, dN2_ds = derivatives[1]
    dN3_dr, dN3_ds = derivatives[2]

    J11 = x1 * dN1_dr + x2 * dN2_dr + x3 * dN3_dr
    J12 = x1 * dN1_ds + x2 * dN2_ds + x3 * dN3_ds
    J21 = y1 * dN1_dr + y2 * dN2_dr + y3 * dN3_dr
    J22 = y1 * dN1_ds + y2 * dN2_ds + y3 * dN3_ds

    J = np.transpose(np.array([[J11, J12], [J21, J22]]))
    detJ = J11 * J22 - J12 * J21
    abs_detJ = abs(detJ)
    invJ = np.linalg.inv(J)

    return J, invJ, detJ, abs_detJ


def get_quadrature_points_and_weights():
    points = [(1 / 3, 1 / 3)]
    weights = [0.5]
    return points, weights


def lagrange2d(derivatives, r, s, invJ):
    dr, ds = derivatives
    grad_global = np.matmul(invJ, np.array([dr, ds]))
    return grad_global


def comp_stiffness_matrix(basis_functions, derivatives, jacobian_inverse, abs_detJ, points, weights):
    num_points = len(points)
    num_functions = len(basis_functions)
    stiffness_matrix = np.zeros((num_functions, num_functions))
    for k in range(num_points):
        r_k, s_k = points[k]
        w_k = weights[k]
        grad_psi = np.array([lagrange2d(derivatives[i], r_k, s_k, jacobian_inverse) for i in range(num_functions)])
        for i in range(num_functions):
            for j in range(num_functions):
                stiffness_matrix[i, j] += np.dot(grad_psi[i], grad_psi[j]) * abs_detJ * w_k
    return stiffness_matrix


def calculate_everything_for_all_triangles(mesh):
    vertices = mesh['vertices']
    triangles = mesh['triangles']
    all_basis_functions = []
    all_jacobians = []
    all_jacobian_inverses = []
    all_jacobian_det = []
    all_jacobian_absolute_detJ = []
    all_stiffness_matrices = []
    points, weights = get_quadrature_points_and_weights()
    for idx, triangle in enumerate(triangles):
        v1 = vertices[triangle[0]]
        v2 = vertices[triangle[1]]
        v3 = vertices[triangle[2]]
        basis_functions, derivatives = lagrange_basis_functions()
        all_basis_functions.append(basis_functions)
        jacobian, jacobian_inverse, detJ, abs_detJ = jacobian_matrix(v1, v2, v3, derivatives)
        all_jacobians.append(jacobian)
        all_jacobian_inverses.append(jacobian_inverse)
        all_jacobian_det.append(detJ)
        all_jacobian_absolute_detJ.append(abs_detJ)
        stiffness_matrix = comp_stiffness_matrix(basis_functions, derivatives, jacobian_inverse, abs_detJ, points,
                                                 weights)
        all_stiffness_matrices.append(stiffness_matrix)

    return all_basis_functions, derivatives, all_jacobians, all_jacobian_inverses, all_jacobian_det, all_jacobian_absolute_detJ, all_stiffness_matrices


def assemble_global_matrix(vertices, triangles, all_stiffness_matrices):
    num_vertices = len(vertices)
    global_matrix = np.zeros((num_vertices, num_vertices))
    for triangle_idx, triangle in enumerate(triangles):
        local_stiffness = all_stiffness_matrices[triangle_idx]
        for local_i, global_i in enumerate(triangle):
            for local_j, global_j in enumerate(triangle):
                global_matrix[global_i, global_j] += local_stiffness[local_i, local_j]
    return global_matrix


def apply_boundary_conditions(vertices, global_stiffness_matrix, global_load_vector, ibntag, bc_values):
    """
    Apply Dirichlet boundary conditions with customizable values for each edge.
    
    Parameters:
    vertices (array): Mesh vertices
    global_stiffness_matrix (array): Global stiffness matrix
    global_load_vector (array): Global load vector (can be None)
    ibntag (array): Boundary tags for each vertex
    bc_values (dict): Dictionary with boundary values for each edge (keys: 1, 2, 3, 4)
    
    Returns:
    tuple: Updated global stiffness matrix and load vector
    """
    num_vertices = len(vertices)
    if global_load_vector is None:
        global_load_vector = np.zeros(num_vertices)
    
    for idx, vertex in enumerate(vertices):
        tag = ibntag[idx]
        if tag in bc_values:
            global_stiffness_matrix[idx, :] = 0
            global_stiffness_matrix[idx, idx] = 1
            global_load_vector[idx] = bc_values[tag]
    
    return global_stiffness_matrix, global_load_vector


def plot_solution_as_base64(vertices, triangles, u, title="FEM Solution"):
    """
    Generate a base64 encoded contour plot of the solution.
    
    Parameters:
    vertices (array): Mesh vertices
    triangles (array): Mesh triangles
    u (array): Solution values
    title (str): Plot title
    
    Returns:
    str: Base64 encoded PNG image
    """
    x = vertices[:, 0]
    y = vertices[:, 1]
    triangles = np.array(triangles)
    
    plt.figure(figsize=(8, 8))
    contour = plt.tricontourf(x, y, triangles, u, levels=80, cmap='jet')
    plt.colorbar(contour, label='Solution u')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(title)
    plt.axis('equal')
    
    # Save plot to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')


def plot_solution_3d_as_base64(vertices, triangles, u, title="3D FEM Solution"):
    """
    Generate a base64 encoded 3D surface plot of the solution.
    
    Parameters:
    vertices (array): Mesh vertices
    triangles (array): Mesh triangles
    u (array): Solution values
    title (str): Plot title
    
    Returns:
    str: Base64 encoded PNG image
    """
    x = vertices[:, 0]
    y = vertices[:, 1]
    z_num = u
    triangles = np.array(triangles)
    
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    tri = ax.plot_trisurf(x, y, z_num, triangles=triangles, cmap='jet')
    fig.colorbar(tri, ax=ax, shrink=0.5, aspect=10)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('u')
    ax.set_title(title, pad=10)
    
    # Save plot to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')


def solve_heat_equation_2d(width=10, height=10, mesh_density=0.05, mesh_quality=30, 
                          bc_values={1: 0, 2: 0, 3: 1, 4: 1}, with_holes=False,
                          hole_rows=0, hole_cols=0, hole_radius=0.5):
    """
    Solve the 2D heat equation using FEM with customizable parameters.
    
    Parameters:
    width (float): Width of the domain
    height (float): Height of the domain
    mesh_density (float): Mesh density parameter (smaller = finer mesh)
    mesh_quality (int): Mesh quality parameter
    bc_values (dict): Boundary condition values for each edge
    with_holes (bool): Whether to include holes in the mesh
    hole_rows (int): Number of rows of holes (only used if with_holes=True)
    hole_cols (int): Number of columns of holes (only used if with_holes=True)
    hole_radius (float): Radius of the holes (only used if with_holes=True)
    
    Returns:
    dict: Results including solution, mesh, and plots
    """
    # Generate mesh
    mesh = mesh_generator.plot_geometry_and_generate_mesh(
        width=width, height=height, density=mesh_density, quality=mesh_quality,
        with_holes=with_holes, hole_rows=hole_rows, hole_cols=hole_cols, hole_radius=hole_radius
    )
    
    # Get mesh plot
    mesh_plot = mesh_generator.plot_mesh_as_base64(mesh)
    
    # Solve FEM problem
    ibntag = mesh['ibntag']
    all_basis_functions, derivatives, all_jacobian, all_jacobian_inverse, all_detJ, all_abs_detJ, all_stiffness_matrices = calculate_everything_for_all_triangles(mesh)
    global_stiffness_matrix = assemble_global_matrix(mesh['vertices'], mesh['triangles'], all_stiffness_matrices)
    global_stiffness_matrix, global_load_vector = apply_boundary_conditions(
        mesh['vertices'], global_stiffness_matrix, None, ibntag, bc_values
    )
    
    # Solve the system
    u = np.linalg.solve(global_stiffness_matrix, global_load_vector)
    
    # Generate plots
    contour_plot = plot_solution_as_base64(mesh['vertices'], mesh['triangles'], u, "2D Heat Equation - Contour Plot")
    surface_plot = plot_solution_3d_as_base64(mesh['vertices'], mesh['triangles'], u, "2D Heat Equation - Surface Plot")
    
    # Prepare results
    results = {
        "mesh": {
            "vertices": mesh['vertices'].tolist(),
            "triangles": mesh['triangles'].tolist(),
            "num_vertices": len(mesh['vertices']),
            "num_triangles": len(mesh['triangles'])
        },
        "solution": u.tolist(),
        "plots": {
            "mesh": mesh_plot,
            "contour": contour_plot,
            "surface": surface_plot
        },
        "parameters": {
            "width": width,
            "height": height,
            "mesh_density": mesh_density,
            "mesh_quality": mesh_quality,
            "bc_values": bc_values,
            "with_holes": with_holes,
            "hole_rows": hole_rows,
            "hole_cols": hole_cols,
            "hole_radius": hole_radius
        }
    }
    
    return results 