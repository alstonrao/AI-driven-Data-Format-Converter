# AI-driven Data Format Converter (STL to STEP)

This project is an advanced engineering assistant that uses Artificial Intelligence to convert 3D STL mesh models into feature-based STEP files. It features a modern web interface and a powerful Python backend.

## 🚀 Start Guide

### 1. Prerequisites (What you need installed)

Before you begin, make sure you have the following installed on your computer:

*   **Node.js** (for the website interface): [Download Node.js](https://nodejs.org/) (Choose the "LTS" version).
*   **Python** (for the logic and AI): [Download Python](https://www.python.org/downloads/) (Version 3.10 or newer is recommended).
*   **Git** (to download this code): [Download Git](https://git-scm.com/downloads).

---

### 2. Download the Code

Open your terminal (Command Prompt on Windows, Terminal on Mac) and run:

```bash
git clone https://github.com/alstonrao/AI-driven-Data-Format-Converter.git
cd AI-driven-Data-Format-Converter
```

---

### 3. Setup Backend (The Brains) 🧠

The backend handles the file conversion and AI analysis.

1.  **Create a Virtual Environment** (This keeps the project clean):
    ```bash
    # Mac/Linux:
    python3 -m venv venv
    
    # Windows:
    python -m venv venv
    ```

2.  **Activate the Environment**:
    ```bash
    # Mac/Linux:
    source venv/bin/activate
    
    # Windows:
    venv\Scripts\activate
    ```
    *(You should see `(venv)` appear at the start of your terminal line)*

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **🔑 Important: Configure Environment Variables (.env)**
    You need to tell the app your API keys.
    
    1.  In the project folder, create a new file named `.env` (no name, just `.env`).
    2.  Open it with any text editor (Notepad, TextEdit, VS Code).
    3.  Paste the following content and fill in your details:
    
    ```env
    OPENAI_API_KEY=your_actual_api_key_here
    OPENAI_BASE_URL=https://api.openai.com/v1/
    OPENAI_MODEL_NAME=gpt-4-turbo
    ```

---

### 4. Setup Frontend (The Interface) 💻

The frontend is the website you see and interact with.

1.  Open a **new** terminal window (keep the backend one open!).
2.  Navigate to the project folder again.
3.  **Install Dependencies**:
    
    ```bash
    npm install
    ```

---

### 5. Run the Application ▶️

You always need **two terminals** running at the same time:

**Terminal 1: Backend**
```bash
# Make sure (venv) is active
# If not, run: source venv/bin/activate (Mac) or venv\Scripts\activate (Win)

uvicorn src.server:app --port 8000 --reload
```
*You will see "Application startup complete".*

**Terminal 2: Frontend**
```bash
npm run dev
```
*You will see a link like `http://localhost:5173`.*

👉 **Open your browser and go to `http://localhost:5173` to use the app!**

---

### ❓ Troubleshooting

*   **"command not found: python"**: Try using `python3` instead.
*   **"Module not found" error**: Make sure you activated the virtual environment (`source venv/bin/activate`) before running `pip install` or starting the server.
*   **Upload failed**: Check your `.env` file to ensure your API Key is correct.