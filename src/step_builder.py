import datetime
import uuid

class StepBuilder:
    def __init__(self):
        self.entities = []
        self.next_id = 1
        
    def add(self, string_def):
        """Adds a raw entity string and returns its (id, ref_string)."""
        eid = self.next_id
        self.next_id += 1
        ref = f"#{eid}"
        self.entities.append(f"{ref}={string_def};")
        return eid, ref

    def generate_step_from_strategy(self, strategy_json):
        """
        Generates a valid AP214 STEP file with a Product -> Shape Representation -> Geometric Set hierarchy.
        This ensures the file is not "empty" in viewers.
        """
        # Reset only if empty?
        # Actually, we want to SUPPORT appending to existing entities (from add_mesh_solid)
        # so we DO NOT reset self.entities or self.next_id here.
        pass
        
        # 1. Product & Context Definitions (Boilerplate)
        _, app_context = self.add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
        _, p_context = self.add(f"PRODUCT_CONTEXT('',{app_context},'mechanical')")
        _, p_def_context = self.add(f"PRODUCT_DEFINITION_CONTEXT('part definition',{app_context},'design')")
        
        product_name = strategy_json.get("detected_shape", "Converted Model")
        _, product = self.add(f"PRODUCT('{product_name}','{product_name}','',({p_context}))")
        
        _, p_def_formation = self.add(f"PRODUCT_DEFINITION_FORMATION('','',{product})")
        _, p_def = self.add(f"PRODUCT_DEFINITION('design','',{p_def_formation},{p_def_context})")
        
        # Units
        _, len_unit = self.add("SI_UNIT(*,.MILLI.,.METRE.)")
        _, ang_unit = self.add("SI_UNIT($,.RADIAN.)")
        _, sol_unit = self.add("SI_UNIT($,.STERADIAN.)")
        
        _, geo_context = self.add(f"GEOMETRIC_REPRESENTATION_CONTEXT('3D',{app_context},3)")
        _, uncertainty = self.add(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(0.01),{len_unit},'distance_accuracy_value','confusion accuracy')")
        _, global_unc = self.add(f"GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({uncertainty}),{geo_context})")
        _, context_repr = self.add(f"GLOBAL_UNIT_ASSIGNED_CONTEXT(({len_unit},{ang_unit},{sol_unit}),{global_unc})")

        # 2. Geometry Elements
        geo_items_refs = [] # For things that are NOT faces (lines, points, axes)
        face_items_refs = [] # Strictly for ADVANCED_FACEs
        
        # Create an Axis Placement for the root (0,0,0)
        _, origin_pt = self.add("CARTESIAN_POINT('',(0.0,0.0,0.0))")
        _, z_dir = self.add("DIRECTION('',(0.0,0.0,1.0))")
        _, x_dir = self.add("DIRECTION('',(1.0,0.0,0.0))")
        _, axis2 = self.add(f"AXIS2_PLACEMENT_3D('',{origin_pt},{z_dir},{x_dir})")
        
        # We'll validly add the axis to a Geometric Set if needed, but NOT to a Shell
        
        # Generate items from strategy
        entities = strategy_json.get("entities", [])
        if not entities:
            print("Warning: No entities in strategy.")
            
        for item in entities:
             try:
                etype = item.get("type", "").upper()
                params = item.get("params", {})
                
                if etype == "PLANE":
                    # ... [Existing plane code] ...
                    # (Code ommitted for brevity, assume identical until the end)
                    origin = params.get("origin", [0,0,0])
                    normal = params.get("normal", [0,0,1])
                    width = params.get("width", 10.0) 
                    height = params.get("height", 10.0)
                    x_axis = params.get("x_axis", None) 
                    
                    # 1. Surface
                    _, p = self.add(f"CARTESIAN_POINT('',({origin[0]:.4f},{origin[1]:.4f},{origin[2]:.4f}))")
                    _, n = self.add(f"DIRECTION('',({normal[0]:.4f},{normal[1]:.4f},{normal[2]:.4f}))")
                    
                    if x_axis:
                        _, x_ref = self.add(f"DIRECTION('',({x_axis[0]:.4f},{x_axis[1]:.4f},{x_axis[2]:.4f}))")
                        _, ax = self.add(f"AXIS2_PLACEMENT_3D('',{p},{n},{x_ref})")
                        x_vec = x_axis
                    else:
                        _, ax = self.add(f"AXIS2_PLACEMENT_3D('',{p},{n},$)")
                        import numpy as np
                        n_vec = np.array(normal)
                        arb = np.array([0, 0, 1])
                        if np.abs(np.dot(n_vec, arb)) > 0.9: arb = np.array([0, 1, 0])
                        x_vec = np.cross(n_vec, arb)
                        x_vec = x_vec / np.linalg.norm(x_vec)
                        x_vec = x_vec.tolist()

                    _, plane_surf = self.add(f"PLANE('',{ax})")
                    
                    # 2. Bounding
                    import numpy as np
                    c = np.array(origin)
                    n_v = np.array(normal)
                    x_v = np.array(x_vec)
                    y_v = np.cross(n_v, x_v) 
                    w2 = width / 2.0
                    h2 = height / 2.0
                    
                    p1 = c - (x_v * w2) - (y_v * h2)
                    p2 = c + (x_v * w2) - (y_v * h2)
                    p3 = c + (x_v * w2) + (y_v * h2)
                    p4 = c - (x_v * w2) + (y_v * h2)
                    
                    v_ids = []
                    for pt in [p1, p2, p3, p4]:
                        _, cp = self.add(f"CARTESIAN_POINT('',({pt[0]:.4f},{pt[1]:.4f},{pt[2]:.4f}))")
                        _, vp = self.add(f"VERTEX_POINT('',{cp})")
                        v_ids.append(vp)
                        
                    edges = []
                    for i in range(4):
                        start = v_ids[i]
                        end = v_ids[(i+1)%4]
                        v_start = [p1, p2, p3, p4][i]
                        v_end = [p1, p2, p3, p4][(i+1)%4]
                        vec = v_end - v_start
                        vec_len = np.linalg.norm(vec)
                        vec = vec / (vec_len if vec_len > 0 else 1)
                        
                        _, l_pt = self.add(f"CARTESIAN_POINT('',({v_start[0]:.4f},{v_start[1]:.4f},{v_start[2]:.4f}))")
                        _, l_dir = self.add(f"DIRECTION('',({vec[0]:.4f},{vec[1]:.4f},{vec[2]:.4f}))")
                        _, line_geo = self.add(f"LINE('',{l_pt},{l_dir})")
                        _, edge = self.add(f"EDGE_CURVE('',{start},{end},{line_geo},.T.)")
                        _, o_edge = self.add(f"ORIENTED_EDGE('',*,*,{edge},.T.)")
                        edges.append(o_edge)
                        
                    edge_str = ",".join(edges)
                    _, loop = self.add(f"EDGE_LOOP('',({edge_str}))")
                    _, bound = self.add(f"FACE_BOUND('',{loop},.T.)")
                    _, face = self.add(f"ADVANCED_FACE('',({bound}),{plane_surf},.T.)")
                    
                    face_items_refs.append(face)
                    
                elif etype == "CYLINDER":
                    # Cylinders are simpler, infinite for now? 
                    # If infinite, put in geo_items as simple surface
                    # If you want bounded, need logic. Let's stick to infinite surface for fallback cylinder
                    origin = params.get("origin", [0,0,0])
                    axis = params.get("axis", [0,0,1])
                    radius = params.get("radius", 5.0)
                    
                    _, p = self.add(f"CARTESIAN_POINT('',({origin[0]:.4f},{origin[1]:.4f},{origin[2]:.4f}))")
                    _, a = self.add(f"DIRECTION('',({axis[0]:.4f},{axis[1]:.4f},{axis[2]:.4f}))")
                    _, ax = self.add(f"AXIS2_PLACEMENT_3D('',{p},{a},$)")
                    
                    _, ref = self.add(f"CYLINDRICAL_SURFACE('',{ax},{float(radius):.4f})")
                    geo_items_refs.append(ref)
                    
                elif etype == "BOX":
                    # Generate a MANIFOLD_SOLID_BREP for a box
                    # Ensure strict Topological Consistency (CCW Winding for Outward Normals)
                    center = params.get("center", [0,0,0])
                    dims = params.get("dimensions", [10,10,10])
                    dx, dy, dz = dims[0], dims[1], dims[2]
                    
                    x0 = center[0] - dx/2
                    x1 = center[0] + dx/2
                    y0 = center[1] - dy/2
                    y1 = center[1] + dy/2
                    z0 = center[2] - dz/2
                    z1 = center[2] + dz/2
                    
                    # 8 Vertices
                    v_coords = [
                        [x0, y0, z0], # 0
                        [x1, y0, z0], # 1
                        [x1, y1, z0], # 2
                        [x0, y1, z0], # 3
                        [x0, y0, z1], # 4
                        [x1, y0, z1], # 5
                        [x1, y1, z1], # 6
                        [x0, y1, z1]  # 7
                    ]
                    
                    v_ids = []
                    for c in v_coords:
                         _, cp = self.add(f"CARTESIAN_POINT('',({c[0]:.4f},{c[1]:.4f},{c[2]:.4f}))")
                         _, vp = self.add(f"VERTEX_POINT('',{cp})")
                         v_ids.append(vp)
                         
                    # Edge Helper (Create Edge Curve)
                    def make_edge(i_start, i_end):
                        p_s = v_coords[i_start]
                        p_e = v_coords[i_end]
                        vec = [p_e[0]-p_s[0], p_e[1]-p_s[1], p_e[2]-p_s[2]]
                        # Norm
                        import math
                        mag = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
                        vec = [x/mag for x in vec]
                        
                        _, l_pt = self.add(f"CARTESIAN_POINT('',({p_s[0]:.4f},{p_s[1]:.4f},{p_s[2]:.4f}))")
                        _, l_dir = self.add(f"DIRECTION('',({vec[0]:.4f},{vec[1]:.4f},{vec[2]:.4f}))")
                        _, line = self.add(f"LINE('',{l_pt},{l_dir})")
                        _, edge = self.add(f"EDGE_CURVE('',{v_ids[i_start]},{v_ids[i_end]},{line},.T.)")
                        return edge

                    # Define canonical edges (we define one direction, then use orientation)
                    # To minimize confusion, let's strictly define edges used in loops.
                    # Or reuse edges. Reusing edges is better for topology.
                    
                    # Horizontal Bottom
                    e_0_1 = make_edge(0,1)
                    e_1_2 = make_edge(1,2)
                    e_2_3 = make_edge(2,3)
                    e_3_0 = make_edge(3,0)
                    
                    # Horizontal Top
                    e_4_5 = make_edge(4,5)
                    e_5_6 = make_edge(5,6)
                    e_6_7 = make_edge(6,7)
                    e_7_4 = make_edge(7,4)
                    
                    # Verticals
                    e_0_4 = make_edge(0,4)
                    e_1_5 = make_edge(1,5)
                    e_2_6 = make_edge(2,6)
                    e_3_7 = make_edge(3,7)
                    
                    # Face Builder Helper
                    def build_face_from_loop(edges_with_sense, normal_vec):
                        # edges_with_sense: list of (edge_id, bool_is_forward)
                        o_edges = []
                        for (eid, fwd) in edges_with_sense:
                             s_str = ".T." if fwd else ".F."
                             _, oe = self.add(f"ORIENTED_EDGE('',*,*,{eid},{s_str})")
                             o_edges.append(oe)
                        
                        e_str = ",".join(o_edges)
                        _, loop = self.add(f"EDGE_LOOP('',({e_str}))")
                        _, bound = self.add(f"FACE_BOUND('',{loop},.T.)")
                        
                        # Plane Surface
                        # We use the FIRST vertex of the loop as origin for simplicity
                        # But plane origin can be center too. Let's use loop start.
                        # It doesn't matter for infinite plane, but good for visualization.
                        # Actually standard practice: use centroid or just valid point.
                        
                        _, pt = self.add(f"CARTESIAN_POINT('',({center[0]:.4f},{center[1]:.4f},{center[2]:.4f}))")
                        _, dir_n = self.add(f"DIRECTION('',({normal_vec[0]:.4f},{normal_vec[1]:.4f},{normal_vec[2]:.4f}))")
                        
                        # Arbitrary X-ref
                        if abs(normal_vec[2]) > 0.9: xref = [1,0,0]
                        else: xref = [0,0,1]
                        
                        _, dir_x = self.add(f"DIRECTION('',({xref[0]:.4f},{xref[1]:.4f},{xref[2]:.4f}))")
                        _, ax2 = self.add(f"AXIS2_PLACEMENT_3D('',{pt},{dir_n},{dir_x})")
                        _, plane = self.add(f"PLANE('',{ax2})")
                        
                        _, adv_face = self.add(f"ADVANCED_FACE('',({bound}),{plane},.T.)")
                        return adv_face

                    faces = []
                    
                    # 1. Bottom (Z-): 0->1->2->3 (CCW for Z-)
                    # Edges: 0-1(T), 1-2(T), 2-3(T), 3-0(T)
                    f_bottom = build_face_from_loop(
                        [(e_0_1,True), (e_1_2,True), (e_2_3,True), (e_3_0,True)], 
                        [0,0,-1]
                    )
                    faces.append(f_bottom)

                    # 2. Top (Z+): 4->5->6->7 (CCW for Z+)
                    # Edges: 4-5(T), 5-6(T), 6-7(T), 7-4(T)
                    f_top = build_face_from_loop(
                        [(e_4_5,True), (e_5_6,True), (e_6_7,True), (e_7_4,True)], 
                        [0,0,1]
                    )
                    faces.append(f_top)
                    
                    # 3. Front (Y-): 0->4->5->1 (Review: 0->1->5->4 was CCW)
                    # Let's re-verify: Normal Y- (0,-1,0).
                    # 0(0,0,0) -> 1(10,0,0) -> 5(10,0,10) -> 4(0,0,10).
                    # Loop: 0-1(e_0_1 T), 1-5(e_1_5 T), 5-4(e_4_5 REV/F), 4-0(e_0_4 REV/F)
                    f_front = build_face_from_loop(
                        [(e_0_1,True), (e_1_5,True), (e_4_5,False), (e_0_4,False)],
                        [0,-1,0]
                    )
                    faces.append(f_front)
                    
                    # 4. Right (X+): 1->5->6->2 (Normal X+)
                    # 1(10,0,0) -> 5(10,0,10) -> 6(10,10,10) -> 2(10,10,0)
                    # e_1_5(T), e_5_6(T), e_2_6(REV/F), e_1_2(REV/F)
                    f_right = build_face_from_loop(
                        [(e_1_5,True), (e_5_6,True), (e_2_6,False), (e_1_2,False)],
                        [1,0,0]
                    )
                    faces.append(f_right)
                    
                    # 5. Back (Y+): 2->6->7->3 (Normal Y+)
                    # 2(10,10,0) -> 6(10,10,10) -> 7(0,10,10) -> 3(0,10,0)
                    # e_2_6(T), e_6_7(T), e_3_7(REV/F), e_2_3(REV/F)
                    f_back = build_face_from_loop(
                        [(e_2_6,True), (e_6_7,True), (e_3_7,False), (e_2_3,False)],
                        [0,1,0]
                    )
                    faces.append(f_back)
                    
                    # 6. Left (X-): 3->7->4->0 (Normal X-)
                    # 3(0,10,0) -> 7(0,10,10) -> 4(0,0,10) -> 0(0,0,0)
                    # e_3_7(T), e_7_4(T), e_0_4(REV/F), e_3_0(REV/F)
                    f_left = build_face_from_loop(
                        [(e_3_7,True), (e_7_4,True), (e_0_4,False), (e_3_0,False)],
                        [-1,0,0]
                    )
                    faces.append(f_left)
                    
                    # Create CLOSED_SHELL
                    f_refs = ",".join(faces)
                    _, c_shell = self.add(f"CLOSED_SHELL('',({f_refs}))")
                    _, brep = self.add(f"MANIFOLD_SOLID_BREP('',{c_shell})")
                    
                    self.solid_breps = getattr(self, 'solid_breps', [])
                    self.solid_breps.append(brep)

             except Exception as e:
                 print(f"Error building entity {item}: {e}")

        # 3. Shape Representation
        
        # Priority: MANIFOLD_SOLID_BREP > SHELL_BASED_SURFACE_MODEL > GEOMETRIC_SET
        top_repr_items = []
        
        # Check for solids first
        solids = getattr(self, 'solid_breps', [])
        if solids:
             top_repr_items.extend(solids)
        
        # Then Open Shells (surfaces)
        if face_items_refs:
             shell_list = ",".join(face_items_refs)
             _, open_shell = self.add(f"OPEN_SHELL('',({shell_list}))")
             _, sbsm = self.add(f"SHELL_BASED_SURFACE_MODEL('',({open_shell}))")
             top_repr_items.append(sbsm)
             
        # 3b. Add any loose geometry (cylinders, axes) via GEOMETRIC_SET
        if geo_items_refs:
             # Always include original axis if we have loose items
             geo_items_refs.insert(0, axis2)
             gset_list = ",".join(geo_items_refs)
             _, geo_set = self.add(f"GEOMETRIC_SET('',({gset_list}))")
             top_repr_items.append(geo_set)
        
        # Check for solids (Faceted Breps from Mesh)
        solids = getattr(self, 'solid_breps', [])
        if solids:
             top_repr_items.extend(solids)
             
        if not top_repr_items:
             # Fallback if absolutely nothing
             _, geo_set = self.add(f"GEOMETRIC_SET('',({axis2}))")
             top_repr_items.append(geo_set)
             
        # Representation takes a list of items
        repr_items_str = ",".join(top_repr_items)
        _, shape_repr = self.add(f"SHAPE_REPRESENTATION('transferred geometry',({repr_items_str}),{context_repr})")
        
        # PRODUCT_DEFINITION_SHAPE
        _, prod_def_shape = self.add(f"PRODUCT_DEFINITION_SHAPE('','',{p_def})")
        
        # SHAPE_DEFINITION_REPRESENTATION
        self.add(f"SHAPE_DEFINITION_REPRESENTATION({prod_def_shape},{shape_repr})")

        # 4. Generate Output
        return self.build_final_string()

    def add_mesh_solid(self, vertices, faces):
        """
        Convert a raw mesh (vertices, faces) into a FACETED_BREP STEP entity.
        This uses POLY_LOOPs and implies planar faces.
        It is the simplest and most robust way to represent arbitrary geometry in STEP.
        """
        print(f"DEBUG: add_mesh_solid called with {len(vertices)} verts and {len(faces)} faces.")
        # 1. Create Cartesian Points
        # Map vertex index to STEP point ID to ensure topology sharing
        v_map = {}
        for i, v in enumerate(vertices):
            # Scale check? STL is usually units. STEP is defined as Millimeter in header.
            _, pid = self.add(f"CARTESIAN_POINT('',({v[0]:.4f},{v[1]:.4f},{v[2]:.4f}))")
            v_map[i] = pid
            
        # 2. Create Faces
        step_faces = []
        
        for face_indices in faces:
            # Create POLY_LOOP
            # We assume mesh winding is consistent (usually CCW for outward normal)
            p_ids = [v_map[idx] for idx in face_indices]
            p_ref_str = ",".join(p_ids)
            
            _, loop = self.add(f"POLY_LOOP('',({p_ref_str}))")
            _, bound = self.add(f"FACE_OUTER_BOUND('',{loop},.T.)")
            
            # Create FACE_SURFACE with explicit PLANE
            # Calculate Plane details
            p0 = vertices[face_indices[0]]
            p1 = vertices[face_indices[1]]
            p2 = vertices[face_indices[2]]
            
            # Vectors
            v1 = [p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]]
            v2 = [p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2]]
            
            # Normal
            nx = v1[1]*v2[2] - v1[2]*v2[1]
            ny = v1[2]*v2[0] - v1[0]*v2[2]
            nz = v1[0]*v2[1] - v1[1]*v2[0]
            
            import math
            mag = math.sqrt(nx*nx + ny*ny + nz*nz)
            if mag < 1e-9: n = [0,0,1]
            else: n = [nx/mag, ny/mag, nz/mag]
                
            # Plane Axis
            _, pt = self.add(f"CARTESIAN_POINT('',({p0[0]:.4f},{p0[1]:.4f},{p0[2]:.4f}))")
            _, dir_n = self.add(f"DIRECTION('',({n[0]:.4f},{n[1]:.4f},{n[2]:.4f}))")
             
            # Arbitrary X-axis
            if abs(n[2]) > 0.9: xref = [1,0,0]
            else: xref = [0,0,1]
            _, dir_x = self.add(f"DIRECTION('',({xref[0]:.4f},{xref[1]:.4f},{xref[2]:.4f}))")
            
            _, ax2 = self.add(f"AXIS2_PLACEMENT_3D('',{pt},{dir_n},{dir_x})")
            _, plane = self.add(f"PLANE('',{ax2})")
            
            # Create Face
            _, step_face = self.add(f"FACE_SURFACE('',({bound}),{plane},.T.)")
            step_faces.append(step_face)
            
        # 3. Create Shell
        f_list = ",".join(step_faces)
        _, c_shell = self.add(f"CLOSED_SHELL('',({f_list}))")
        
        # 4. Create Faceted Brep
        _, brep = self.add(f"FACETED_BREP('',{c_shell})")
        
        self.solid_breps = getattr(self, 'solid_breps', [])
        self.solid_breps.append(brep)

    def build_final_string(self):
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        header = f"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('STEP AP214'),'2;1');
FILE_NAME('converted.step','{now}',('AI-Converter'),('User'),'Processor','System','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));
ENDSEC;
DATA;"""
        footer = "ENDSEC;\nEND-ISO-10303-21;"
        
        body = "\n".join(self.entities)
        return f"{header}\n{body}\n{footer}"
