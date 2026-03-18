import os
import shutil
import uuid
import json
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from pdf_processor import extract_pdf_content
from llm_analyzer import analyze_with_gemini
from report_generator import generate_pdf

load_dotenv(override=True)

app = FastAPI(title="DDR Report Generator API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def cleanup_workspace(workspace_dir: str):
    """Cleanup temporary files after request is complete."""
    try:
        if os.path.exists(workspace_dir):
            shutil.rmtree(workspace_dir)
    except Exception as e:
        print(f"Failed to cleanup {workspace_dir}: {e}")

@app.post("/api/generate")
async def generate_report(
    background_tasks: BackgroundTasks,
    sample_report: UploadFile = File(...),
    thermal_images: UploadFile = File(...)
):
    if not os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY") == "your-key":
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured on the server.")

    # Create a unique workspace for this request to avoid collisions
    request_id = str(uuid.uuid4())
    workspace_dir = os.path.join(os.getcwd(), "temp_workspaces", request_id)
    image_dir = os.path.join(workspace_dir, "extracted_images")
    os.makedirs(image_dir, exist_ok=True)

    try:
        # Save uploaded files
        sample_path = os.path.join(workspace_dir, "Sample_Report.pdf")
        thermal_path = os.path.join(workspace_dir, "Thermal_Images.pdf")
        
        with open(sample_path, "wb") as f:
            shutil.copyfileobj(sample_report.file, f)
        with open(thermal_path, "wb") as f:
            shutil.copyfileobj(thermal_images.file, f)

        # 1. Extract
        sample_data = extract_pdf_content(sample_path, image_dir, "sample")
        thermal_data = extract_pdf_content(thermal_path, image_dir, "thermal")

        # 2. Analyze
        report_data = analyze_with_gemini(sample_data, thermal_data)
        if not report_data:
            raise HTTPException(status_code=500, detail="Analysis failed to return structured data.")

        # 3. Generate outputs
        json_path = os.path.join(workspace_dir, "Main_DDR_Output.json")
        pdf_path = os.path.join(workspace_dir, "Main_DDR_Output.pdf")

        with open(json_path, "w") as f:
            json.dump(report_data, f, indent=4)
        
        generate_pdf(report_data, pdf_path, image_dir)

        # To return the files, we could create a ZIP or return URLs.
        # For simplicity in this challenge, we'll move the final files to a public "outputs" folder 
        # and return their URLs.
        outputs_dir = os.path.join(os.getcwd(), "frontend", "outputs", request_id)
        os.makedirs(outputs_dir, exist_ok=True)
        
        final_pdf_path = os.path.join(outputs_dir, "Main_DDR_Output.pdf")
        final_json_path = os.path.join(outputs_dir, "Main_DDR_Output.json")
        
        shutil.copy2(pdf_path, final_pdf_path)
        shutil.copy2(json_path, final_json_path)

        # Cleanup temp workspace after we've copied what we need
        background_tasks.add_task(cleanup_workspace, workspace_dir)

        return JSONResponse({
            "status": "success",
            "message": "Report generated successfully!",
            "results": {
                "pdf_url": f"/api/download/{request_id}/pdf",
                "json_url": f"/api/download/{request_id}/json"
            }
        })

    except Exception as e:
        background_tasks.add_task(cleanup_workspace, workspace_dir)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{request_id}/pdf")
async def download_pdf(request_id: str):
    file_path = os.path.join(os.getcwd(), "frontend", "outputs", request_id, "Main_DDR_Output.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(path=file_path, filename="Detailed_Diagnostic_Report.pdf", media_type='application/pdf')

@app.get("/api/download/{request_id}/json")
async def download_json(request_id: str):
    file_path = os.path.join(os.getcwd(), "frontend", "outputs", request_id, "Main_DDR_Output.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="JSON not found")
    return FileResponse(path=file_path, filename="Detailed_Diagnostic_Report.json", media_type='application/json')


# Mount frontend at the root last so it acts as a fallback for static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
