# AI-Powered PDF Report Generation Workflow

This project is an automated AI pipeline designed to ingest complex inspection and thermal PDF reports and synthesize a professional, structured **Detailed Diagnostic Report (DDR)**.
Video Link: https://www.loom.com/share/fd7af0c5083e478ebb8da5c8e2b03f05

## 🚀 Overview
The workflow extracts text and images from multiple sources, processes them through a high-reasoning LLM (Google Gemini 2.5 Flash), and generates a client-ready PDF with:
- **Professional Metadata**: Site Address, Structure Type, Age, etc.
- **Color-Coded Checklists**: High-fidelity tabular assessments with status-based colors (Red/Yellow/Brown).
- **Contextual Image Mapping**: Photos are automatically placed alongside relevant observations.
- **Summary Matrix**: A final table mapping impacted areas to their probable root causes.

## 🛠️ Performance & Stability Features
- **Dimensional Filtering**: Automatically discards tiny/noise PDF artifacts (<150x150 pixels) to ensure clean reports.
- **Auto-Retries**: Integrated with `tenacity` for exponential backoff retries against transient API 503 errors.
- **Strict Schema Enforcement**: Uses Pydantic to guarantee 100% valid JSON responses from the AI.
- **Intelligent Word Wrapping**: Custom horizontal space boundary logic inside the FPDF engine to prevent rendering crashes.

## 📁 Project Structure
- `app.py`: FastAPI backend and API routes.
- `frontend/`: Web interface (HTML/CSS/JS).
- `main.py`: CLI orchestration script.
- `pdf_processor.py`: PDF extraction logic (text/images).
- `llm_analyzer.py`: Gemini 2.5 Flash integration.
- `report_generator.py`: PDF layout engine.
- `Sample Report.pdf` & `Thermal Images.pdf`: Input files.
- `Main_DDR_Output.pdf`: Final generated output.

## ⚙️ Setup & Execution
1. **Prerequisites**: Python 3.10+ and a Google Gemini API Key.
2. **Installation**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Environment**: Create a `.env` file and add:
   ```env
   GEMINI_API_KEY=your_key_here
   ```
4. **Run**:
   - **Web Interface (Recommended)**:
     ```bash
     uvicorn app:app --reload
     ```
     Access at: `http://127.0.0.1:8000/`
   - **CLI Mode**:
     ```bash
     python main.py
     ```

## 🎥 Submission Requirements
- **Loom Video Link**: [Watch Video](https://www.loom.com/share/fd7af0c5083e478ebb8da5c8e2b03f05)
- **GitHub Repository Link**: [jayeshpandey01/DDR-Reports](https://github.com/jayeshpandey01/DDR-Reports)
- **Project Demo Link**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (Local Dev)

---
*Built within the 24-hour AI Workflow Challenge.*
#   D D R - R e p o r t s
