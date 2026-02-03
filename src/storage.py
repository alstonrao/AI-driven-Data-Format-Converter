import os
import shutil
import datetime

OUTPUT_DIR = "outputs/runs"

def init_storage():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_temp_artifacts(run_id, stl_file, step_content, report_content):
    """
    Save artifacts to a timestamped folder.
    """
    run_dir = os.path.join(OUTPUT_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)
    
    # Save STEP
    step_path = os.path.join(run_dir, "converted.step")
    with open(step_path, "w") as f:
        f.write(step_content)
        
    # Save Report
    report_path = os.path.join(run_dir, "explanation.md")
    with open(report_path, "w") as f:
        f.write(report_content)
        
    return run_dir, step_path
