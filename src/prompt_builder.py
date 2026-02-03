import json

def build_structured_prompt(mesh_stats, features, options=None):
    """
    Construct the prompt for the LLM to generate a STEP strategy.
    
    Args:
        mesh_stats (dict): Statistics from mesh_stats.py
        features (dict): Feature hints from feature_hints.py
        options (dict): User options (e.g. detail level)
        
    Returns:
        str: The full prompt string.
    """
    
    system_context = (
        "You are an expert CAD engineer specialized in Reverse Engineering. "
        "Your task is to analyze mesh statistics and geometric hints to propose a "
        "strategy for representing this object in ISO 10303-21 (STEP) format using "
        "feature-based approximations (Planes, Cylinders)."
    )
    
    data_context = {
        "Mesh Statistics": mesh_stats,
        "Detected Hints": features
    }
    
    task_instructions = (
        "Based on the provided data:\n"
        "1. Identify the most likely geometric primitives (e.g., is the object a box, a cylinder, or a plate?).\n"
        "2. Propose a simplified B-Rep structure. Don't try to mesh every triangle. Group coplanar faces into single planes.\n"
        "3. Output a valid JSON object containing your strategy. The JSON must have the following fields:\n"
        "   - 'detected_shape': Single phrase description (e.g., 'Rectangular Plate').\n"
        "   - 'assumptions': List of assumptions made (e.g., 'Assuming Z-axis symmetry').\n"
        "   - 'entities': A list of entities to create. Each entity should have:\n"
        "       - 'type': 'PLANE' or 'CYLINDER'\n"
        "       - 'params': { 'origin': [x,y,z], 'normal': [x,y,z] } for PLANE\n"
        "       - 'params': { 'origin': [x,y,z], 'axis': [x,y,z], 'radius': r } for CYLINDER\n"
        "       - 'dimensions': { 'width': w, 'height': h } estimate for bounds (optional)\n"
        "\n"
        "Use the provided hints. If planar hints are large, use them as faces. "
        "If a cylindrical axis is hinted, fit a cylinder there."
    )
    
    prompt = f"{system_context}\n\nDATA:\n{json.dumps(data_context, indent=2)}\n\nINSTRUCTIONS:\n{task_instructions}"
    
    return prompt
