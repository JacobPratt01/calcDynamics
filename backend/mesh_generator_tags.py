import numpy as np
import triangle as tr
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def generate_mesh_with_options(width=10, height=10, density=0.05, quality=30):
    """
    Generate a triangular mesh with customizable options.
    
    Parameters:
    width (float): Width of the rectangular domain
    height (float): Height of the rectangular domain
    density (float): Mesh density (smaller values create finer meshes)
    quality (int): Triangle quality parameter (higher values enforce better quality triangles)
    
    Returns:
    dict: Mesh data including vertices, triangles, and boundary tags
    """
    # Create rectangle vertices
    square_vertices = np.array([[0, 0], [width, 0], [width, height], [0, height]])
    vertices = square_vertices
    segments = np.array([[i, (i + 1) % 4] for i in range(4)])
    
    # Generate mesh with custom parameters
    mesh_input = {'vertices': vertices, 'segments': segments}
    mesh = tr.triangulate(mesh_input, f'pq{quality}a{density}')
    
    # Tag vertices based on their position
    vertex_tags = np.zeros(len(mesh['vertices']))
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
    
    mesh['ibntag'] = vertex_tags
    return mesh

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

def plot_geometry_and_generate_mesh(width=10, height=10, density=0.05, quality=30):
    """
    Generate a mesh with the specified parameters and return it.
    This function is compatible with the original code.
    
    Parameters:
    width (float): Width of the rectangular domain
    height (float): Height of the rectangular domain
    density (float): Mesh density (smaller values create finer meshes)
    quality (int): Triangle quality parameter (higher values enforce better quality triangles)
    
    Returns:
    dict: Mesh data including vertices, triangles, and boundary tags
    """
    return generate_mesh_with_options(width, height, density, quality) 