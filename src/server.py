from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import json
import uuid
import logging
import datetime
from typing import List, Optional

# Import existing modules
from src import stl_io, mesh_stats, feature_hints, prompt_builder, llm_client, step_builder, explain, storage, config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="STL to STEP Converter API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for session state (simulation of DB)
# In production, use a real DB or Redis
SESSIONS = {}

# Persistent History
HISTORY_FILE = os.path.join(config.get_output_dir(), "history.json")

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history_record(record):
    history = load_history()
    # Prepend new record
    history.insert(0, record)
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

class AnalysisResult(BaseModel):
    stats: dict
    planar_hints: List[dict]
    cylindrical_hints: List[dict]
    session_id: str

class GenerationResponse(BaseModel):
    step_file_path: str
    explanation: str

@app.get("/api/history")
async def get_history():
    return load_history()

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload an STL file, parse it, and return analysis.
    """
    session_id = str(uuid.uuid4())
    
    # Save temp file
    temp_dir = os.path.join(config.get_output_dir(), "temp", session_id)
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Parse and Analyze
    logger.info(f"Analyzing {file.filename}...")
    try:
        mesh = stl_io.load_stl(file_path)
        if mesh is None:
            raise HTTPException(status_code=400, detail="Failed to parse STL file")
            
        stats = mesh_stats.compute_mesh_stats(mesh)
        planar_hints = feature_hints.extract_planar_hints(mesh)
        cyl_hints = feature_hints.extract_cylindrical_hints(mesh)
        
        # Store in session
        SESSIONS[session_id] = {
            "mesh_path": file_path,
            "filename": file.filename,
            "stats": stats,
            "planar_hints": planar_hints,
            "cylindrical_hints": cyl_hints,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        return {
            "session_id": session_id,
            "stats": stats,
            "planar_hints_count": len(planar_hints),
            "cylindrical_hints_count": len(cyl_hints)
        }
        
    except Exception as e:
        logger.error(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/{session_id}")
async def generate_step(session_id: str):
    """
    Generate STEP file based on session data.
    """
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    data = SESSIONS[session_id]
    
    try:
        # Build prompt
        prompt = prompt_builder.build_structured_prompt(
            data['stats'],
            {
                "planar": data['planar_hints'],
                "cylindrical": data['cylindrical_hints']
            }
        )
        
        # Call LLM (We still call it for 'Explanation' and feature hints, but NOT for geometry generation)
        strategy_json = llm_client.call_llm(prompt)
        
        # Determine Status
        generation_source = "Hybrid (Mesh + AI Explanation)"
        
        # Build STEP
        builder = step_builder.StepBuilder()
        
        # Robust Geometry Generation: Load the original mesh
        # We access the file path from session data
        mesh_path = data.get("mesh_path")
        
        # FORCE MESH GEOMETRY ONLY - Remove AI hallucinations
        strategy_json["entities"] = [] 
        
        if mesh_path and os.path.exists(mesh_path):
             logger.info(f"Loading mesh for robust conversion: {mesh_path}")
             mesh = stl_io.load_stl(mesh_path)
             if mesh:
                 logger.info(f"Mesh loaded. Vertices: {len(mesh.vertices)}, Faces: {len(mesh.faces)}")
                 try:
                     builder.add_mesh_solid(mesh.vertices.tolist(), mesh.faces.tolist())
                     logger.info("Successfully added Faceted B-Rep to builder.")
                     strategy_json["assumptions"].append("Geometry reconstructed using full-fidelity Faceted B-Rep (Mesh).")
                 except Exception as build_err:
                     logger.error(f"Error in add_mesh_solid: {build_err}")
                     raise
             else:
                 logger.error("Failed to parse mesh for conversion.")
        else:
             logger.error("Mesh path missing from session.")

        # Note: strategy_json['entities'] is now empty, so generate_step_from_strategy 
        # will ONLY write the solid_breps (and boilerplate).
        step_content = builder.generate_step_from_strategy(strategy_json)
        
        # Build Explanation
        report = explain.build_explanation(
            data['stats'],
            {
                "planar_features": data['planar_hints'],
                "cylindrical_hints": data['cylindrical_hints']
            },
            strategy_json
        )
        
        # Save artifacts
        run_id = f"{session_id}_run"
        saved_dir, step_path = storage.save_temp_artifacts(
            run_id,
            data['filename'],
            step_content,
            report
        )
        
        # Update session with result paths
        SESSIONS[session_id]['step_path'] = step_path
        SESSIONS[session_id]['report'] = report
        
        # Save to History
        now = datetime.datetime.now()
        history_record = {
            "id": session_id,
            "fileName": data['filename'],
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "status": "success",
            "planarSurfaces": len(data['planar_hints']),
            "cylindricalFeatures": len(data['cylindrical_hints']),
            "edgeFeatures": strategy_json.get("edge_count", 0),
            "fileSize": f"{os.path.getsize(data['mesh_path']) / 1024 / 1024:.1f} MB",
            "step_path": step_path
        }
        save_history_record(history_record)
        
        return {
            "download_url": f"/api/download/{session_id}",
            "explanation": report,
            "status": generation_source
        }
        
    except Exception as e:
        logger.error(f"Error generating STEP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{session_id}")
async def download_result(session_id: str):
    # Try SESSIONS first
    if session_id in SESSIONS and 'step_path' in SESSIONS[session_id]:
        path = SESSIONS[session_id]['step_path']
        filename = os.path.basename(path)
        return FileResponse(path, filename=filename, media_type='application/step')
    
    # Try History
    history = load_history()
    record = next((r for r in history if r['id'] == session_id), None)
    if record and 'step_path' in record:
        path = record['step_path']
        if os.path.exists(path):
             filename = os.path.basename(path)
             return FileResponse(path, filename=filename, media_type='application/step')
             
    raise HTTPException(status_code=404, detail="File not found")

@app.get("/api/session/{session_id}")
async def get_session_details(session_id: str):
    """
    Retrieve full details for a session (active or historical).
    """
    # 1. Try Active Session
    if session_id in SESSIONS:
        data = SESSIONS[session_id]
        if 'report' in data: # Completed session
             return {
                 "status": "complete",
                 "analysis": {
                     "stats": data.get('stats'),
                     "planar_hints_count": len(data.get('planar_hints', [])),
                     "cylindrical_hints_count": len(data.get('cylindrical_hints', []))
                 },
                 "generation": {
                     "download_url": f"/api/download/{session_id}",
                     "explanation": data['report']
                 }
             }

    # 2. Try History (Disk)
    history = load_history()
    record = next((r for r in history if r['id'] == session_id), None)
    
    if record:
        # Reconstruct paths
        step_path = record.get('step_path')
        if step_path:
            dir_path = os.path.dirname(step_path)
            explanation_path = os.path.join(dir_path, "explanation.md")
            
            explanation_text = "Explanation not found."
            if os.path.exists(explanation_path):
                with open(explanation_path, "r") as f:
                    explanation_text = f.read()
                    
            # Reconstruct Analysis Stats (Approximate from record if not saved)
            # History record has summary counts
            analysis_summary = {
                "stats": {
                    "num_faces": "Unknown (History)",
                    "num_vertices": "Unknown (History)",
                    "bbox_dimensions": ["?", "?", "?"]
                },
                "planar_hints_count": record.get('planarSurfaces', 0),
                "cylindrical_hints_count": record.get('cylindricalFeatures', 0)
            }
            
            return {
                "status": "complete",
                "analysis": analysis_summary,
                "generation": {
                    "download_url": f"/api/download/{session_id}",
                    "explanation": explanation_text
                }
            }
            
    raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
