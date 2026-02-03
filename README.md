# AI-driven Data Format Converter (STL to STEP)

This project is an AI-driven engineering assistant that converts STL mesh models into FEATURE-BASED STEP files. It uses a **Hybrid Architecture**:
- **Frontend**: React + TypeScript (Modern UI)
- **Backend**: Python FastAPI (Geometry processing & AI Analysis)

## 📦 Deployment & Setup Guide (Offline Bundle)

This guide assumes you have received the complete project package (including `offline_packages` and `node_modules`).

### 1. Prerequisites
Ensure the following are installed on your system:
- **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 16+**: [Download Node.js](https://nodejs.org/)

### 2. Installation Steps

#### Step A: Unzip and Navigate
Unzip the project package and open a terminal in the root directory:
```bash
cd path/to/project-folder
```

#### Step B: Backend Setup (Python)
1.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
2.  Activate the environment:
    - **Mac/Linux**: `source venv/bin/activate`
    - **Windows**: `venv\Scripts\activate`
3.  Install dependencies (Offline Mode):
    ```bash
    # Installs libraries from the local 'offline_packages' folder
    pip install --no-index --find-links=offline_packages -r requirements.txt
    ```

#### Step C: Frontend Setup
*The dependencies are already included in the `node_modules` folder, so no installation is required.*

### 3. Running the Application

You need to run **two separate terminals** (one for Backend, one for Frontend).

#### Terminal 1: Backend API
```bash
# Ensure venv is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.server:app --port 8000 --reload
```
*The backend will start at `http://localhost:8000`*

#### Terminal 2: Frontend UI
```bash
# Start the development server
npm run dev
```
*The app will open at `http://localhost:5173`. If it doesn't open automatically, visit that link in your browser.*

---

### Alternative: Online Installation
If you are cloning from Git or missing the Bundled folders:
- **Python**: `pip install -r requirements.txt`
- **Node**: `npm install`


## Features
- **Upload**: Support for STL files (binary/ASCII).
- **Physical Analysis**: Precise Volume, Surface Area, and Center of Mass calculations.
- **Generate**: Robust STEP file generation from Mesh data.
- **Explain**: Detailed engineering report on geometry and physical properties.