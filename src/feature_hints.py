import numpy as np
import trimesh

def extract_planar_hints(mesh, min_area_fraction=0.01):
    """
    Identify potential planar features in the mesh.
    Uses trimesh's facet generation (clustering of coplanar faces).
    
    Args:
        mesh (trimesh.Trimesh): The target mesh.
        min_area_fraction (float): Minimum area fraction to consider a facet as a significant plane.
        
    Returns:
        list: A list of dictionaries describing planar hints.
    """
    hints = []
    
    # trimesh.facets returns list of lists of face indices
    # We want to filter them by area
    total_area = mesh.area
    
    # Facets (groups of coplanar faces)
    facets = mesh.facets
    
    for facet_face_indices in facets:
        facet_area = np.sum(mesh.area_faces[facet_face_indices])
        
        if facet_area / total_area >= min_area_fraction:
            normal = mesh.face_normals[facet_face_indices[0]]
            
            # Get all unique vertices in this facet
            # mesh.faces contains vertex indices for each face. 
            # We want all vertex indices involved in this facet.
            face_vertex_indices = mesh.faces[facet_face_indices].flatten()
            unique_v_indices = np.unique(face_vertex_indices)
            vertices = mesh.vertices[unique_v_indices]
            
            # Compute Oriented Bounding Box for this set of vertices
            # 1. Project to 2D plane defined by normal
            # Simple approach: find a dominant tangent vector
            # Arbitrary vector not parallel to normal
            arb = np.array([0, 0, 1])
            if np.abs(np.dot(normal, arb)) > 0.9:
                arb = np.array([0, 1, 0])
            
            x_axis = np.cross(normal, arb)
            x_axis = x_axis / np.linalg.norm(x_axis)
            y_axis = np.cross(normal, x_axis)
            
            # Project vertices
            center_v = np.mean(vertices, axis=0) # centered
            centered_vs = vertices - center_v
            
            u = np.dot(centered_vs, x_axis)
            v = np.dot(centered_vs, y_axis)
            
            # 2D Bounding Box
            min_u, max_u = np.min(u), np.max(u)
            min_v, max_v = np.min(v), np.max(v)
            
            width = max_u - min_u
            height = max_v - min_v
            
            # Center of the bbox in 3D
            u_center = (min_u + max_u) / 2
            v_center = (min_v + max_v) / 2
            
            bbox_center = center_v + (u_center * x_axis) + (v_center * y_axis)
            
            hints.append({
                "type": "plane",
                "normal": normal.tolist(),
                "area": float(facet_area),
                "center": bbox_center.tolist(), # Use bbox center, not mass center
                "param_u": float(width),
                "param_v": float(height),
                "x_axis": x_axis.tolist(),
                "y_axis": y_axis.tolist(),
                "face_count": len(facet_face_indices)
            })
            
    # Sort by area descending
    hints.sort(key=lambda x: x["area"], reverse=True)
    return hints

def extract_cylindrical_hints(mesh):
    """
    Identify potential cylindrical features.
    
    This is a simplified heuristic since full B-Rep extraction is complex.
    We assume that if we have large non-planar components, they might be cylindrical.
    
    For Milestone 3, we act conservatively:
    - If we find a region that isn't a plane, we describe its bounding box or dominant axis.
    """
    # Placeholder for advanced logic.
    # We can rely on the fact that if a mesh is mostly planes, the "rest" might be fillets or cylinders.
    # For now, we return a generic hint if the planar area is significantly less than total area.
    
    hints = []
    
    # If standard cylinder detection is needed, we'd need RANSAC here.
    # Since we lack a dedicated library in the requirements for RANSAC primitive fitting (like pyransac3d),
    # we will rely on a "Global Feature Assumption" for the LLM.
    # i.e., "If there are many normals perpendicular to Z, it might be a vertical cylinder."
    
    # Function to check for curvature (varying normals)
    def has_curvature(face_mask, axis_of_rotation):
        relevant_normals = mesh.face_normals[face_mask]
        if len(relevant_normals) == 0:
            return False
        
        # Project normals onto difference plane (exclude axis comp) and check variance
        # Or simpler: check if they are all parallel to each other.
        # If mean normal length is close to 1, they are all pointing same way.
        mean_normal = np.mean(relevant_normals, axis=0)
        mean_len = np.linalg.norm(mean_normal)
        
        # If mean length is close to 1.0, vectors are aligned -> Flat Plane
        # If mean length is significantly < 1.0, vectors are spread -> Curved
        return mean_len < 0.95  # Threshold: lower means more spread

    # Check for vertical cylinder characteristics (normals perpendicular to Z)
    z_axis = [0, 0, 1]
    dots = np.abs(np.dot(mesh.face_normals, z_axis))
    # Faces with dot product near 0 are vertical (normals in XY plane)
    vertical_faces_mask = dots < 0.1
    vertical_area = np.sum(mesh.area_faces[vertical_faces_mask])
    
    if vertical_area / mesh.area > 0.1:
        if has_curvature(vertical_faces_mask, z_axis):
            hints.append({
                "type": "cylinder_candidate",
                "axis_hint": [0, 0, 1],
                "reason": "Significant curved surface area with normals perpendicular to Z axis."
            })

    # Check for horizontal cylinder (X axis)
    x_axis = [1, 0, 0]
    dots_x = np.abs(np.dot(mesh.face_normals, x_axis))
    horizontal_faces_mask = dots_x < 0.1
    horizontal_area = np.sum(mesh.area_faces[horizontal_faces_mask])
    
    if horizontal_area / mesh.area > 0.1:
         if has_curvature(horizontal_faces_mask, x_axis):
            hints.append({
                "type": "cylinder_candidate",
                "axis_hint": [1, 0, 0],
                "reason": "Significant curved surface area with normals perpendicular to X axis."
            })
            
    return hints

def get_feature_report(mesh):
    """
    Combined feature report for LLM.
    """
    planar = extract_planar_hints(mesh)
    cylindrical = extract_cylindrical_hints(mesh)
    
    return {
        "planar_features": planar,
        "cylindrical_hints": cylindrical,
        "summary": f"Detected {len(planar)} major planar surfaces."
    }
