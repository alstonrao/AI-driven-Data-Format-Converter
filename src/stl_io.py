import trimesh
import os
import io

def load_stl(file_input):
    """
    Load an STL file from a path or a file-like object.
    
    Args:
        file_input (str or file-like): The STL file to load.
        
    Returns:
        trimesh.Trimesh: The loaded mesh object, or None if loading fails.
    """
    try:
        if isinstance(file_input, str):
            # If it's a file path
            mesh = trimesh.load(file_input, file_type='stl')
        else:
            # If it's a file-like object (e.g. from Streamlit)
            # trimesh expects the file object to have a 'read' attribute
            file_type = 'stl'
            mesh = trimesh.load(file_input, file_type=file_type)

        # Ensure it's a Trimesh object (handling scenes if necessary, though STL usually isn't)
        if isinstance(mesh, trimesh.Scene):
             # If it loaded as a scene, try to get the geometry. 
             # For single STL this usually dumps geometry into a single mesh or a dict.
             # We grab the first available geometry.
             if len(mesh.geometry) == 0:
                 return None
             mesh = list(mesh.geometry.values())[0]

        return mesh
    except Exception as e:
        print(f"Error loading STL: {e}")
        return None

def save_stl(mesh, path):
    """
    Save a mesh object to an STL file.
    """
    try:
        mesh.export(path, file_type='stl')
        return True
    except Exception as e:
        print(f"Error saving STL: {e}")
        return False
