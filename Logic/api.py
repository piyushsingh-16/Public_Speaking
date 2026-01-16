"""
FastAPI Server for Public Speaking Evaluator
Provides REST API endpoints for audio evaluation with file upload support
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
from pydantic import BaseModel, Field, HttpUrl

from evaluator import PublicSpeakingEvaluator
from audio_processor import AudioProcessor


# Job status enum
class JobStatus(str, Enum):
    PENDING = "pending"
    PREPROCESSING = "preprocessing"
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
    print("Starting Public Speaking Evaluation API")
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
        print("\n✓ API Server ready!")
        print("=" * 70)
        print("\nAPI Documentation:")
        print("  - Swagger UI: http://localhost:8000/docs")
        print("  - ReDoc: http://localhost:8000/redoc")
        print("=" * 70 + "\n")
    except Exception as e:
        print(f"\n✗ Failed to initialize evaluator: {str(e)}")
        raise

    yield

    # Cleanup on shutdown
    print("\nShutting down API server...")
    # Optionally cleanup upload directory
    # shutil.rmtree(UPLOAD_DIR, ignore_errors=True)


# Initialize FastAPI app
app = FastAPI(
    title="Public Speaking Evaluation API",
    description="AI-powered public speaking evaluation for school students (Ages 3-18)",
    version="2.0.0",
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
    result: Optional[dict] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health endpoint"""
    status: str
    model_loaded: bool
    model_info: dict
    version: str
    active_jobs: int


class WebhookPayload(BaseModel):
    """Payload sent to callback URL"""
    job_id: str
    status: JobStatus
    created_at: str
    completed_at: str
    result: Optional[dict] = None
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
        jobs[job_id]["progress"] = "Preprocessing audio..."
        jobs[job_id]["updated_at"] = datetime.now().isoformat()

        # Validate audio format
        audio_processor = AudioProcessor()
        if not audio_processor.is_supported_format(audio_path):
            raise ValueError(f"Unsupported audio format. Supported: {AudioProcessor.SUPPORTED_FORMATS}")

        # Update status: transcribing
        jobs[job_id]["status"] = JobStatus.TRANSCRIBING
        jobs[job_id]["progress"] = "Transcribing speech..."
        jobs[job_id]["updated_at"] = datetime.now().isoformat()

        # Run evaluation (this takes 30-60 seconds)
        result = evaluator.evaluate(
            audio_path=audio_path,
            student_age=student_age,
            student_name=student_name,
            topic=topic,
            save_json=False
        )

        # Update status: analyzing
        jobs[job_id]["status"] = JobStatus.ANALYZING
        jobs[job_id]["progress"] = "Analyzing metrics..."
        jobs[job_id]["updated_at"] = datetime.now().isoformat()

        # Check for evaluation errors
        if result.get("error", False):
            raise Exception(result.get("message", "Evaluation failed"))

        # Update status: completed
        jobs[job_id]["status"] = JobStatus.COMPLETED
        jobs[job_id]["progress"] = "Evaluation complete"
        jobs[job_id]["result"] = result
        jobs[job_id]["updated_at"] = datetime.now().isoformat()

        print(f"[{job_id}] Evaluation completed. Overall score: {result['scores']['overall']}")

        # Send webhook callback if provided
        if callback_url:
            webhook_payload = WebhookPayload(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                created_at=jobs[job_id]["created_at"],
                completed_at=datetime.now().isoformat(),
                result=result
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
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "POST /evaluate": "Upload audio file for evaluation (multipart/form-data)",
            "GET /jobs/{job_id}": "Poll job status and get results",
            "GET /jobs": "List all jobs",
            "GET /health": "Health check"
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
        JobStatus.TRANSCRIBING, JobStatus.ANALYZING
    ])

    return HealthResponse(
        status="healthy" if model_loaded else "initializing",
        model_loaded=model_loaded,
        model_info=model_info,
        version="2.0.0",
        active_jobs=active_jobs
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

    **How to use:**
    1. Upload an audio file with student info
    2. Receive a job_id immediately
    3. Poll `GET /jobs/{job_id}` every 2-3 seconds until status is "completed"
    4. Get the full results from the response

    **Request (multipart/form-data):**
    - `audio_file`: Audio file (required) - MP3, WAV, M4A, OGG, FLAC, WEBM
    - `student_age`: Student's age 3-18 (required)
    - `student_name`: Student's name (optional)
    - `topic`: Speech topic (optional)
    - `callback_url`: Webhook URL to POST results (optional)

    **Response:**
    ```json
    {
        "job_id": "abc-123-def",
        "status": "pending",
        "message": "Evaluation job queued. Poll GET /jobs/{job_id} for results.",
        "created_at": "2024-01-01T12:00:00"
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
        "result": None,
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
        cleanup_file=True  # Clean up uploaded file after processing
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
    audio_path: str = Field(..., description="Path to audio file on server (MP3, WAV, M4A, OGG, FLAC, WEBM)")
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

    **How to use:**
    1. Provide the path to an audio file on the server
    2. Receive a job_id immediately
    3. Poll `GET /jobs/{job_id}` every 2-3 seconds until status is "completed"
    4. Get the full results from the response

    **Request (JSON):**
    ```json
    {
        "audio_path": "/path/to/audio.mp3",
        "student_age": 10,
        "student_name": "John",
        "topic": "My Speech",
        "callback_url": "http://example.com/webhook"
    }
    ```

    **Response:**
    ```json
    {
        "job_id": "abc-123-def",
        "status": "pending",
        "message": "Evaluation job queued. Poll GET /jobs/{job_id} for results.",
        "created_at": "2024-01-01T12:00:00"
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
        "result": None,
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
        cleanup_file=False  # Don't delete the original file
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
    `pending` → `preprocessing` → `transcribing` → `analyzing` → `completed`

    **Response when completed:**
    ```json
    {
        "job_id": "abc-123",
        "status": "completed",
        "message": "Evaluation completed successfully",
        "result": {
            "metadata": { ... },
            "transcript": { "full_text": "...", "word_count": 150 },
            "scores": {
                "overall": 85,
                "clarity": 90,
                "pace": 80,
                "pause_management": 85,
                "filler_reduction": 75,
                "repetition_control": 90,
                "structure": 85
            },
            "detailed_analysis": { ... },
            "improvement_suggestions": [ ... ]
        }
    }
    ```
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
        result=job.get("result"),
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
        JobStatus.PENDING: "Job is queued and waiting to start",
        JobStatus.PREPROCESSING: "Preprocessing audio file",
        JobStatus.TRANSCRIBING: "Transcribing speech to text",
        JobStatus.ANALYZING: "Analyzing speech metrics",
        JobStatus.COMPLETED: "Evaluation completed successfully",
        JobStatus.FAILED: "Evaluation failed"
    }
    return messages.get(job_status, "Unknown status")


# =============================================================================
# WEBHOOK TEST ENDPOINTS (for development/testing)
# =============================================================================

@app.post("/webhook/test", tags=["Webhook Testing"])
async def receive_webhook_test(payload: dict):
    """
    Test endpoint to receive webhook callbacks.

    Use this URL as your callback_url for testing:
    - callback_url: "http://localhost:8000/webhook/test"
    """
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
    if payload.get("result"):
        print(f"  Overall Score: {payload['result'].get('scores', {}).get('overall', 'N/A')}")
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
    """
    Retrieve the full evaluation result received via webhook for a specific job.
    """
    if job_id not in webhook_test_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No webhook received for job: {job_id}. The job may still be processing."
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
        "result": payload.get("result")
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
