import os
import sys
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil

# Ensure the root directory is in sys.path so we can import src modules
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.renderer import process_video
from src.physics.classifier import process_video_csv, generate_set_summary, detect_lift_type
from src.analysis.dtw_engine import compare_to_reference
from src.ai.coach import generate_feedback

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Gym Bro API")

# Mount the data directory so the frontend can stream the processed video
app.mount("/data", StaticFiles(directory="data"), name="data")

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join("data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Gym Bro AI Engine is Online"}

@app.post("/api/analyze")
async def analyze_video(file: UploadFile = File(...)):
    if not file.filename.endswith((".mp4", ".mov")):
        raise HTTPException(status_code=400, detail="Only MP4 or MOV files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Dummy progress updater for the backend
        def update_progress(progress, message):
            print(f"[Engine]: {progress}% - {message}")

        # Stage 1: Vision Tracking
        print("Starting vision tracking...")
        result = process_video(file_path, update_progress, lift_type=None)
        lift_selection = result.detected_lift_type

        # Stage 2: Biomechanics
        print(f"Starting biomechanics for {lift_selection}...")
        timeline_report = process_video_csv(result.smoothed_csv, lift_type=lift_selection)
        final_summary = generate_set_summary(timeline_report, lift_type=lift_selection)
        dtw_result = compare_to_reference(result.smoothed_csv, lift_type=lift_selection)

        # Stage 3: AI Coach
        print("Generating AI feedback...")
        coaching_report = generate_feedback(final_summary, dtw_result, lift_selection)

        import pandas as pd
        raw_preview = pd.read_csv(result.raw_csv).head(5).fillna("").to_dict(orient="records")

        # Return comprehensive JSON payload to the frontend
        return JSONResponse(content={
            "status": "success",
            "exercise": lift_selection,
            "metrics": final_summary,
            "tempo": dtw_result,
            "coach_feedback": coaching_report,
            "telemetry": timeline_report,
            "raw_preview": raw_preview,
            "files": {
                "output_video": result.output_video,
                "raw_csv": result.raw_csv,
                "smoothed_csv": result.smoothed_csv
            }
        })

    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
