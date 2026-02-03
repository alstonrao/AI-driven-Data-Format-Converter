import json

def build_explanation(mesh_stats, hints, strategy):
    """
    Generate a human-readable explanation report.
    """
    
    report = f"""# Conversion Explanation Report

## 1. Input Analysis
- **Vertices**: {mesh_stats.get('num_vertices')}
- **Faces**: {mesh_stats.get('num_faces')}
- **Watertight**: {mesh_stats.get('is_watertight')}
- **Dimensions**: {mesh_stats.get('bbox_dimensions')}
    """

    # Physical Properties
    # Physical Properties
    vol = mesh_stats.get('volume')
    area = mesh_stats.get('surface_area')
    com = mesh_stats.get('center_mass')
    
    if vol: vol_mm3 = vol
    else: vol_mm3 = 0.0
    
    if area: area_mm2 = area
    else: area_mm2 = 0.0
    
    report += f"""
### 1.1 Physical Properties
- **Volume**: {vol_mm3:.2f} mm3
- **Surface Area**: {area_mm2:.2f} mm2
- **Center of Mass**: [{com[0]:.2f}, {com[1]:.2f}, {com[2]:.2f}] (mm)

## 2. Detected Features
We analyzed the input mesh and identified the following geometric features:
"""
    
    if hints.get('planar_features'):
        report += f"\n### Planar Surfaces ({len(hints['planar_features'])} detected)\n"
        # List top 5 largest planes
        for i, p in enumerate(hints['planar_features'][:5]):
            n = p['normal']
            report += f"- **Plane {i+1}**: Area={p['area']:.1f} mm², Normal=[{n[0]:.2f}, {n[1]:.2f}, {n[2]:.2f}]\n"
        if len(hints['planar_features']) > 5:
            report += f"- ... and {len(hints['planar_features']) - 5} smaller surfaces.\n"

    if hints.get('cylindrical_hints'):
        report += f"\n### Cylindrical Features ({len(hints['cylindrical_hints'])} detected)\n"
        for i, c in enumerate(hints['cylindrical_hints']):
             axis = c.get('axis_hint', [0,0,0])
             report += f"- **Cylinder {i+1}**: Axis aligned with [{axis[0]}, {axis[1]}, {axis[2]}]. {c.get('reason','')}\n"
        
    report += "\n## 3. Generative Strategy\n"
    report += f"**Detected Shape Class**: {strategy.get('detected_shape', 'General 3D Object')}\n\n"
    
    if strategy.get('assumptions'):
        report += "**Modeling Decisions**:\n"
        for asm in strategy.get('assumptions', []):
            report += f"- {asm}\n"
        
    report += "\n## 4. Output Entities\n"
    # Summarize entity types
    counts = {}
    for ent in strategy.get('entities', []):
        t = ent.get('type', 'Unknown')
        counts[t] = counts.get(t, 0) + 1
        
    if not counts:
        report += "- **FACETED_BREP**: 1 (Full Mesh Reconstruction)\n"
    else:
        for t, c in counts.items():
            report += f"- {t}: {c}\n"
            
    return report
