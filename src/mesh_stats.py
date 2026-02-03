import numpy as np

def compute_mesh_stats(mesh):
    """
    Compute basic statistics for a given mesh.
    
    Args:
        mesh (trimesh.Trimesh): The mesh object.
        
    Returns:
        dict: A dictionary containing mesh statistics.
    """
    if mesh is None:
        return {}

    stats = {
        "num_faces": len(mesh.faces),
        "num_vertices": len(mesh.vertices),
        "bbox_min": mesh.bounds[0].tolist(),
        "bbox_max": mesh.bounds[1].tolist(),
        "bbox_dimensions": mesh.extents.tolist(),
        "is_watertight": mesh.is_watertight,
        "volume": mesh.volume if mesh.is_watertight else None,
        "surface_area": mesh.area,
        "center_mass": mesh.center_mass.tolist() if mesh.is_watertight else mesh.centroid.tolist()
    }
    
    return stats

def get_validity_report(mesh):
    """
    Check if the mesh is valid for processing and return a report.
    """
    valid = True
    issues = []

    if mesh.is_empty:
        valid = False
        issues.append("Mesh is empty.")
    
    # Check for non-manifold edges? For now just watertightness as a warning
    if not mesh.is_watertight:
        issues.append("Mesh is not watertight (may affect volume calc).")

    return {
        "valid": valid,
        "issues": issues
    }
