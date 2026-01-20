"""
FastAPI Server for Public Speaking Evaluator
Provides REST API endpoints for audio evaluation with file upload support

Returns dual structure:
- raw_evaluation: Detailed data for teachers/parents
- child_presentation: Age-appropriate visual feedback for Flutter UI
"""

import os
import uuid
import httpx
import shutil
import tempfile
from typing import Optional
from pathlib import Path
from datetime import datetime
from enum import Enum
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .evaluator import PublicSpeakingEvaluator
from .processors.audio_processor import AudioProcessor


# Job status enum
class JobStatus(str, Enum):
    PENDING = "pending"
    PREPROCESSING = "preprocessing"
    EXTRACTING_FEATURES = "extracting_features"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


# In-memory job storage (use Redis/DB for production)
jobs: dict = {}

# Webhook test storage - stores received callbacks for testing
webhook_test_results: dict = {}

# Upload directory for temporary files
UPLOAD_DIR = Path(tempfile.gettempdir()) / "public_speaking_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Global state
evaluator: Optional[PublicSpeakingEvaluator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize evaluator on startup"""
    global evaluator

    print("\n" + "=" * 70)
    print("Starting Public Speaking Evaluation API v3.0")
    print("=" * 70)

    whisper_model = os.getenv("WHISPER_MODEL", "base")
    device = os.getenv("DEVICE", "cpu")
    compute_type = os.getenv("COMPUTE_TYPE", "int8")

    print(f"\nConfiguration:")
    print(f"  - Whisper Model: {whisper_model}")
    print(f"  - Device: {device}")
    print(f"  - Compute Type: {compute_type}")
    print(f"  - Upload Directory: {UPLOAD_DIR}")

    try:
        evaluator = PublicSpeakingEvaluator(
            whisper_model=whisper_model,
            device=device,
            compute_type=compute_type
        )
        print("\nAPI Server ready!")
        print("=" * 70)
        print("\nAPI Documentation:")
        print("  - Swagger UI: http://localhost:8000/docs")
        print("  - ReDoc: http://localhost:8000/redoc")
        print("\nNew in v3.0:")
        print("  - Audio feature extraction (loudness, pitch, stamina)")
        print("  - Age-appropriate child presentations")
        print("  - Dual response structure (raw + child)")
        print("=" * 70 + "\n")
    except Exception as e:
        print(f"\nFailed to initialize evaluator: {str(e)}")
        raise

    yield

    # Cleanup on shutdown
    print("\nShutting down API server...")


# Initialize FastAPI app
app = FastAPI(
    title="Public Speaking Evaluation API",
    description="""
AI-powered public speaking evaluation for school students (Ages 3-18).

**New in v3.0:**
- Audio feature extraction (loudness, pitch variation, stamina)
- Age-appropriate child presentations (pre-primary, lower-primary, upper-primary, detailed)
- Dual response structure with `raw_evaluation` and `child_presentation`

**Age Groups:**
- **Pre-primary (3-5)**: Character-based feedback (lion/mouse voice)
- **Lower-primary (6-8)**: Icon-based metrics with badges
- **Upper-primary (9-10)**: Progress bars with single improvement tip
- **Middle/Secondary (11+)**: Full detailed analysis
    """,
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response Models
class JobResponse(BaseModel):
    """Response model for job creation"""
    job_id: str
    status: JobStatus
    message: str
    created_at: str


class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: JobStatus
    message: str
    progress: Optional[str] = None
    created_at: str
    updated_at: str
    raw_evaluation: Optional[dict] = None
    child_presentation: Optional[dict] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health endpoint"""
    status: str
    model_loaded: bool
    model_info: dict
    version: str
    active_jobs: int
    features: list


class WebhookPayload(BaseModel):
    """Payload sent to callback URL"""
    job_id: str
    status: JobStatus
    created_at: str
    completed_at: str
    raw_evaluation: Optional[dict] = None
    child_presentation: Optional[dict] = None
    error: Optional[str] = None


# Background task for processing
async def process_evaluation_task(
    job_id: str,
    audio_path: str,
    student_age: int,
    student_name: Optional[str],
    topic: Optional[str],
    callback_url: Optional[str] = None,
    cleanup_file: bool = False
):
    """Background task to process audio evaluation"""
    global evaluator, jobs

    try:
        # Update status: preprocessing
        jobs[job_id]["status"] = JobStatus.PREPROCESSING
        jobs[job_id]["progress"] = "Preparing your audio..."
        jobs[job_id]["updated_at"] = datetime.now().isoformat()

        # Validate audio format
        audio_processor = AudioProcessor()
        if not audio_processor.is_supported_format(audio_path):
            raise ValueError(f"Unsupported audio format. Supported: {AudioProcessor.SUPPORTED_FORMATS}")

        # Update status: extracting features
        jobs[job_id]["status"] = JobStatus.EXTRACTING_FEATURES
        jobs[job_id]["progress"] = "Analyzing your voice..."
        jobs[job_id]["updated_at"] = datetime.now().isoformat()

        # Update status: transcribing
        jobs[job_id]["status"] = JobStatus.TRANSCRIBING
        jobs[job_id]["progress"] = "Listening to your speech..."
        jobs[job_id]["updated_at"] = datetime.now().isoformat()

        # Run evaluation (this includes all steps)
        result = evaluator.evaluate(
            audio_path=audio_path,
            student_age=student_age,
            student_name=student_name,
            topic=topic,
            save_json=False
        )

        # Update status: analyzing
        jobs[job_id]["status"] = JobStatus.ANALYZING
        jobs[job_id]["progress"] = "Analyzing your performance..."
        jobs[job_id]["updated_at"] = datetime.now().isoformat()

        # Check for evaluation errors
        if result.get("error", False):
            raise Exception(result.get("message", "Evaluation failed"))

        # Update status: completed
        jobs[job_id]["status"] = JobStatus.COMPLETED
        jobs[job_id]["progress"] = "Evaluation complete!"
        jobs[job_id]["raw_evaluation"] = result.get("raw_evaluation")
        jobs[job_id]["child_presentation"] = result.get("child_presentation")
        jobs[job_id]["updated_at"] = datetime.now().isoformat()

        overall_score = result.get("raw_evaluation", {}).get("scores", {}).get("overall", "N/A")
        print(f"[{job_id}] Evaluation completed. Overall score: {overall_score}")

        # Send webhook callback if provided
        if callback_url:
            webhook_payload = WebhookPayload(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                created_at=jobs[job_id]["created_at"],
                completed_at=datetime.now().isoformat(),
                raw_evaluation=result.get("raw_evaluation"),
                child_presentation=result.get("child_presentation")
            )

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        callback_url,
                        json=webhook_payload.model_dump(),
                        headers={"Content-Type": "application/json"}
                    )
                    print(f"[{job_id}] Webhook sent to {callback_url}, status: {response.status_code}")
            except Exception as webhook_error:
                print(f"[{job_id}] Failed to send webhook: {webhook_error}")

    except Exception as e:
        error_msg = str(e)
        print(f"[{job_id}] Evaluation failed: {error_msg}")

        # Update job with error
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = error_msg
        jobs[job_id]["updated_at"] = datetime.now().isoformat()

        # Send failure webhook if callback_url provided
        if callback_url:
            webhook_payload = WebhookPayload(
                job_id=job_id,
                status=JobStatus.FAILED,
                created_at=jobs[job_id]["created_at"],
                completed_at=datetime.now().isoformat(),
                error=error_msg
            )

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    await client.post(
                        callback_url,
                        json=webhook_payload.model_dump(),
                        headers={"Content-Type": "application/json"}
                    )
            except Exception as webhook_error:
                print(f"[{job_id}] Failed to send webhook: {webhook_error}")

    finally:
        # Cleanup uploaded file if requested
        if cleanup_file and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                print(f"[{job_id}] Cleaned up uploaded file: {audio_path}")
            except Exception as e:
                print(f"[{job_id}] Failed to cleanup file: {e}")


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Public Speaking Evaluation API",
        "version": "3.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "Audio feature extraction (loudness, pitch, stamina)",
            "Age-appropriate child presentations",
            "9 evaluation metrics",
            "Dual response structure (raw + child)"
        ],
        "endpoints": {
            "POST /evaluate": "Upload audio file for evaluation (multipart/form-data)",
            "GET /jobs/{job_id}": "Poll job status and get results",
            "GET /jobs": "List all jobs",
            "GET /health": "Health check"
        },
        "age_groups": {
            "pre_primary (3-5)": "Character-based feedback",
            "lower_primary (6-8)": "Icon-based metrics",
            "upper_primary (9-10)": "Progress bars + tips",
            "middle/secondary (11+)": "Full detailed analysis"
        },
        "supported_formats": AudioProcessor.SUPPORTED_FORMATS
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check():
    """Health check endpoint with model and job info"""
    global evaluator, jobs

    model_loaded = evaluator is not None
    model_info = {}

    if model_loaded:
        model_info = {
            "size": evaluator.speech_to_text.model_size,
            "device": evaluator.speech_to_text.device,
            "compute_type": evaluator.speech_to_text.compute_type
        }

    active_jobs = sum(1 for j in jobs.values() if j["status"] in [
        JobStatus.PENDING, JobStatus.PREPROCESSING,
        JobStatus.EXTRACTING_FEATURES, JobStatus.TRANSCRIBING, JobStatus.ANALYZING
    ])

    return HealthResponse(
        status="healthy" if model_loaded else "initializing",
        model_loaded=model_loaded,
        model_info=model_info,
        version="3.0.0",
        active_jobs=active_jobs,
        features=[
            "loudness_detection",
            "pitch_variation",
            "stamina_analysis",
            "age_appropriate_output"
        ]
    )


@app.post("/evaluate", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Evaluation"])
async def evaluate_speech(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(..., description="Audio file (MP3, WAV, M4A, OGG, FLAC, WEBM)"),
    student_age: int = Form(..., ge=3, le=18, description="Student age (3-18 years)"),
    student_name: Optional[str] = Form(None, description="Student name (optional)"),
    topic: Optional[str] = Form(None, description="Speech topic (optional)"),
    callback_url: Optional[str] = Form(None, description="Webhook URL for results (optional)")
):
    """
    Upload and evaluate a public speaking audio file.

    **Response Structure:**

    The completed job returns a dual structure:

    ```json
    {
        "raw_evaluation": {
            "metadata": { "student_age": 8, "age_group": "lower_primary", ... },
            "scores": { "overall": 75, "clarity": 80, "loudness": 85, ... },
            "detailed_analysis": { ... },
            "improvement_suggestions": [ ... ]
        },
        "child_presentation": {
            "age_group": "lower_primary",
            "metrics": [
                {"id": "voice_strength", "icon": "🔊", "level": 4},
                {"id": "pace", "icon": "👍"},
                {"id": "expression", "icon": "😊", "level": 3}
            ],
            "badge": {"name": "Confident Speaker", "emoji": "🏅"},
            "message": {"text": "Great job!"}
        }
    }
    ```

    **Processing Time:** 30-60 seconds depending on audio length
    """
    global evaluator, jobs

    if evaluator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Evaluator not initialized. Please try again later."
        )

    # Validate file extension
    file_ext = Path(audio_file.filename).suffix.lower()
    if file_ext not in AudioProcessor.SUPPORTED_FORMATS:
        supported = ", ".join(AudioProcessor.SUPPORTED_FORMATS)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format '{file_ext}'. Supported formats: {supported}"
        )

    # Generate job ID and save file
    job_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    # Save uploaded file
    file_path = UPLOAD_DIR / f"{job_id}{file_ext}"
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    # Create job record
    jobs[job_id] = {
        "status": JobStatus.PENDING,
        "progress": "Job queued",
        "created_at": created_at,
        "updated_at": created_at,
        "request": {
            "original_filename": audio_file.filename,
            "student_age": student_age,
            "student_name": student_name,
            "topic": topic,
            "callback_url": callback_url
        },
        "raw_evaluation": None,
        "child_presentation": None,
        "error": None
    }

    # Queue background task
    background_tasks.add_task(
        process_evaluation_task,
        job_id=job_id,
        audio_path=str(file_path),
        student_age=student_age,
        student_name=student_name,
        topic=topic,
        callback_url=callback_url,
        cleanup_file=True
    )

    print(f"[{datetime.now().isoformat()}] Job {job_id} created")
    print(f"  File: {audio_file.filename} ({file_ext})")
    print(f"  Student: {student_name or 'Anonymous'}, Age: {student_age}")

    return JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Evaluation job queued. Poll GET /jobs/{job_id} for results.",
        created_at=created_at
    )


class EvaluatePathRequest(BaseModel):
    """Request model for path-based evaluation"""
    audio_path: str = Field(..., description="Path to audio file on server")
    student_age: int = Field(..., ge=3, le=18, description="Student age (3-18 years)")
    student_name: Optional[str] = Field(None, description="Student name (optional)")
    topic: Optional[str] = Field(None, description="Speech topic (optional)")
    callback_url: Optional[str] = Field(None, description="Webhook URL for results (optional)")


@app.post("/evaluate/path", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Evaluation"])
async def evaluate_speech_from_path(
    background_tasks: BackgroundTasks,
    request: EvaluatePathRequest
):
    """
    Evaluate a public speaking audio file using a file path.

    Use this endpoint when the audio file is already on the server.
    """
    global evaluator, jobs

    if evaluator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Evaluator not initialized. Please try again later."
        )

    # Validate file exists
    if not os.path.exists(request.audio_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Audio file not found: {request.audio_path}"
        )

    # Validate file extension
    file_ext = Path(request.audio_path).suffix.lower()
    if file_ext not in AudioProcessor.SUPPORTED_FORMATS:
        supported = ", ".join(AudioProcessor.SUPPORTED_FORMATS)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format '{file_ext}'. Supported formats: {supported}"
        )

    # Generate job ID
    job_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    # Create job record
    jobs[job_id] = {
        "status": JobStatus.PENDING,
        "progress": "Job queued",
        "created_at": created_at,
        "updated_at": created_at,
        "request": {
            "audio_path": request.audio_path,
            "student_age": request.student_age,
            "student_name": request.student_name,
            "topic": request.topic,
            "callback_url": request.callback_url
        },
        "raw_evaluation": None,
        "child_presentation": None,
        "error": None
    }

    # Queue background task (don't cleanup file since it's not uploaded)
    background_tasks.add_task(
        process_evaluation_task,
        job_id=job_id,
        audio_path=request.audio_path,
        student_age=request.student_age,
        student_name=request.student_name,
        topic=request.topic,
        callback_url=request.callback_url,
        cleanup_file=False
    )

    print(f"[{datetime.now().isoformat()}] Job {job_id} created (from path)")
    print(f"  File: {request.audio_path}")
    print(f"  Student: {request.student_name or 'Anonymous'}, Age: {request.student_age}")

    return JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Evaluation job queued. Poll GET /jobs/{job_id} for results.",
        created_at=created_at
    )


@app.get("/jobs/{job_id}", response_model=JobStatusResponse, tags=["Jobs"])
async def get_job_status(job_id: str):
    """
    Get the status and results of an evaluation job.

    **Poll this endpoint** every 2-3 seconds until status is "completed" or "failed".

    **Status Flow:**
    `pending` → `preprocessing` → `extracting_features` → `transcribing` → `analyzing` → `completed`

    **Response includes:**
    - `raw_evaluation`: Full detailed evaluation (for teachers/parents)
    - `child_presentation`: Age-appropriate visual feedback (for Flutter UI)
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )

    job = jobs[job_id]

    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        message=_get_status_message(job["status"]),
        progress=job.get("progress"),
        created_at=job["created_at"],
        updated_at=job["updated_at"],
        raw_evaluation=job.get("raw_evaluation"),
        child_presentation=job.get("child_presentation"),
        error=job.get("error")
    )


@app.get("/jobs", tags=["Jobs"])
async def list_jobs(limit: int = 10, status_filter: Optional[JobStatus] = None):
    """List recent jobs with optional status filter"""
    filtered_jobs = []

    for job_id, job in list(jobs.items())[-limit:]:
        if status_filter is None or job["status"] == status_filter:
            filtered_jobs.append({
                "job_id": job_id,
                "status": job["status"],
                "created_at": job["created_at"],
                "updated_at": job["updated_at"]
            })

    return {
        "total": len(filtered_jobs),
        "jobs": filtered_jobs
    }


def _get_status_message(job_status: JobStatus) -> str:
    """Get human-readable status message"""
    messages = {
        JobStatus.PENDING: "Waiting in queue...",
        JobStatus.PREPROCESSING: "Preparing your audio...",
        JobStatus.EXTRACTING_FEATURES: "Analyzing your voice...",
        JobStatus.TRANSCRIBING: "Listening to your speech...",
        JobStatus.ANALYZING: "Analyzing your performance...",
        JobStatus.COMPLETED: "Evaluation complete!",
        JobStatus.FAILED: "Evaluation failed"
    }
    return messages.get(job_status, "Unknown status")


# =============================================================================
# WEBHOOK TEST ENDPOINTS (for development/testing)
# =============================================================================

@app.post("/webhook/test", tags=["Webhook Testing"])
async def receive_webhook_test(payload: dict):
    """Test endpoint to receive webhook callbacks."""
    global webhook_test_results

    job_id = payload.get("job_id", "unknown")
    received_at = datetime.now().isoformat()

    webhook_test_results[job_id] = {
        "received_at": received_at,
        "payload": payload
    }

    print(f"\n{'='*60}")
    print(f"[WEBHOOK RECEIVED] Job: {job_id}")
    print(f"  Status: {payload.get('status')}")
    print(f"  Received at: {received_at}")
    if payload.get("raw_evaluation"):
        score = payload["raw_evaluation"].get("scores", {}).get("overall", "N/A")
        print(f"  Overall Score: {score}")
    if payload.get("child_presentation"):
        age_group = payload["child_presentation"].get("age_group", "N/A")
        print(f"  Child Presentation: {age_group}")
    if payload.get("error"):
        print(f"  Error: {payload.get('error')}")
    print(f"{'='*60}\n")

    return {
        "received": True,
        "job_id": job_id,
        "received_at": received_at
    }


@app.get("/webhook/test/{job_id}", tags=["Webhook Testing"])
async def get_webhook_test_result(job_id: str):
    """Retrieve the full evaluation result received via webhook for a specific job."""
    if job_id not in webhook_test_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No webhook received for job: {job_id}."
        )

    data = webhook_test_results[job_id]
    payload = data["payload"]

    return {
        "job_id": job_id,
        "status": payload.get("status"),
        "received_at": data["received_at"],
        "created_at": payload.get("created_at"),
        "completed_at": payload.get("completed_at"),
        "error": payload.get("error"),
        "raw_evaluation": payload.get("raw_evaluation"),
        "child_presentation": payload.get("child_presentation")
    }


@app.get("/webhook/test", tags=["Webhook Testing"])
async def list_webhook_test_results(limit: int = 10):
    """List all received webhook callbacks (for testing)."""
    results = []
    for job_id, data in list(webhook_test_results.items())[-limit:]:
        results.append({
            "job_id": job_id,
            "received_at": data["received_at"],
            "status": data["payload"].get("status")
        })

    return {
        "total": len(results),
        "webhooks": results
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"\nStarting server on {host}:{port}")
    print("Use Ctrl+C to stop\n")

    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
