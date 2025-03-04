import numpy as np
import triangle as tr
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def generate_mesh_with_options(width=10, height=10, density=0.05, quality=30, with_holes=False, 
                              hole_rows=0, hole_cols=0, hole_radius=0.5):
    """
    Generate a triangular mesh with customizable options, optionally including holes.
    
    Parameters:
    width (float): Width of the rectangular domain
    height (float): Height of the rectangular domain
    density (float): Mesh density (smaller values create finer meshes)
    quality (int): Triangle quality parameter (higher values enforce better quality triangles)
    with_holes (bool): Whether to include holes in the mesh
    hole_rows (int): Number of rows of holes (only used if with_holes=True)
    hole_cols (int): Number of columns of holes (only used if with_holes=True)
    hole_radius (float): Radius of the holes (only used if with_holes=True)
    
    Returns:
    dict: Mesh data including vertices, triangles, and boundary tags
    """
    # Create rectangle vertices
    square_vertices = np.array([[0, 0], [width, 0], [width, height], [0, height]])
    vertices = square_vertices
    segments = np.array([[i, (i + 1) % 4] for i in range(4)])
    
    # Initialize vertex tags
    vertex_tags = [0, 0, 0, 0]  # Initial tags for the four corners
    
    # Add holes if requested
    hole_centers = []
    if with_holes and hole_rows > 0 and hole_cols > 0 and hole_radius > 0:
        x_spacing = width / (hole_cols + 1)
        y_spacing = height / (hole_rows + 1)
        
        for i in range(1, hole_cols + 1):
            for j in range(1, hole_rows + 1):
                center = np.array([i * x_spacing, j * y_spacing])
                hole_centers.append(center)
                
                # Create circle vertices for this hole
                circle = np.array([center + [hole_radius * np.cos(angle), hole_radius * np.sin(angle)] 
                                  for angle in np.linspace(0, 2 * np.pi, num=32, endpoint=False)])
                
                circle_idx_start = len(vertices)
                vertices = np.vstack([vertices, circle])
                
                # Create segments for this circle
                circle_segments = np.array([[circle_idx_start + k, circle_idx_start + (k + 1) % 32] 
                                           for k in range(32)])
                segments = np.vstack([segments, circle_segments])
                
                # Tag the circle vertices with tag 5 (hole boundary)
                vertex_tags.extend([5] * 32)
    
    # Generate mesh
    mesh_input = {'vertices': vertices, 'segments': segments}
    if hole_centers:
        mesh_input['holes'] = hole_centers
    
    mesh = tr.triangulate(mesh_input, f'pq{quality}a{density}')
    
    # Complete the vertex tags for all mesh vertices
    additional_tags = [6] * (len(mesh['vertices']) - len(vertex_tags))
    vertex_tags.extend(additional_tags)
    
    # Tag vertices based on their position
    for i, vertex in enumerate(mesh['vertices']):
        x, y = vertex
        if abs(y - 0) < 1e-10:  # Bottom edge (y = 0)
            vertex_tags[i] = 1
        elif abs(x - 0) < 1e-10:  # Left edge (x = 0)
            vertex_tags[i] = 2
        elif abs(y - height) < 1e-10:  # Top edge (y = height)
            vertex_tags[i] = 3
        elif abs(x - width) < 1e-10:  # Right edge (x = width)
            vertex_tags[i] = 4
    
    mesh['ibntag'] = np.array(vertex_tags)
    return mesh

# Add an alias for backward compatibility
generate_mesh_with_holes = generate_mesh_with_options

def plot_mesh_as_base64(mesh):
    """
    Generate a base64 encoded image of the mesh.
    
    Parameters:
    mesh (dict): Mesh data
    
    Returns:
    str: Base64 encoded PNG image
    """
    plt.figure(figsize=(8, 8))
    tr.plot(plt.axes(), **mesh)
    plt.title('Generated Mesh')
    plt.axis('equal')
    
    # Save plot to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def plot_geometry_and_generate_mesh(width=10, height=10, density=0.05, quality=30, 
                                   with_holes=False, hole_rows=0, hole_cols=0, hole_radius=0.5):
    """
    Generate a mesh with the specified parameters and return it.
    This function is compatible with both the original code and the holes version.
    
    Parameters:
    width (float): Width of the rectangular domain
    height (float): Height of the rectangular domain
    density (float): Mesh density (smaller values create finer meshes)
    quality (int): Triangle quality parameter (higher values enforce better quality triangles)
    with_holes (bool): Whether to include holes in the mesh
    hole_rows (int): Number of rows of holes (only used if with_holes=True)
    hole_cols (int): Number of columns of holes (only used if with_holes=True)
    hole_radius (float): Radius of the holes (only used if with_holes=True)
    
    Returns:
    dict: Mesh data including vertices, triangles, and boundary tags
    """
    return generate_mesh_with_options(
        width, height, density, quality, with_holes, hole_rows, hole_cols, hole_radius
    ) 