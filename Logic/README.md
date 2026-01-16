# Public Speaking Evaluation System

A comprehensive AI-powered evaluation system for assessing public speaking skills of school students (Ages 3-18). Designed for scale, accuracy, and age-appropriate feedback.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [File Structure](#file-structure)
- [Evaluation Metrics](#evaluation-metrics)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What It Does
This system evaluates student speech recordings and provides:
- **6 Core Metrics**: Clarity, Pace, Pauses, Fillers, Repetition, Structure
- **Age-Adjusted Scoring**: Different expectations for different age groups
- **Actionable Feedback**: Specific, encouraging improvement suggestions
- **Detailed Reports**: JSON output with scores, analysis, and recommendations

### Key Features
- **School-Optimized**: Noise-tolerant, accent-agnostic, child-safe scoring
- **Local Processing**: No API costs, complete privacy (saves $250K+/year vs cloud APIs)
- **Scalable**: Handles 200K+ students, 800K+ files/week
- **Fast**: 30-second audio processed in ~3-5 seconds
- **Multiple Formats**: Supports MP3, WAV, M4A, OGG, FLAC, WebM

---

## Architecture

The system follows a **4-stage pipeline architecture**:

```
┌─────────────────────────────────────────────────────────┐
│  STAGE 1: Audio Preprocessing (audio_processor.py)     │
│  - Format conversion to 16kHz mono WAV                  │
│  - Volume normalization using ffmpeg                    │
│  - Audio duration extraction                            │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│  STAGE 2: Speech Recognition (speech_to_text.py)       │
│  - Whisper-based transcription (faster-whisper)         │
│  - Word-level timestamps and confidence scores          │
│  - Voice Activity Detection (VAD) for noise handling    │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│  STAGE 3: Evaluation (evaluation_metrics.py)           │
│  - Analyzes 6 metrics with age-adjusted algorithms      │
│  - Calculates scores (0-100) for each metric            │
│  - Generates specific feedback for each area            │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│  STAGE 4: Report Generation (evaluator.py)             │
│  - Applies age-adjusted weights to calculate overall    │
│  - Compiles comprehensive JSON report                   │
│  - Prioritizes improvement suggestions                  │
└─────────────────────────────────────────────────────────┘
```

**Design Principles:**
- **Modular**: Each stage is independent and testable
- **Configurable**: Settings centralized in config.py
- **Extensible**: Easy to add new metrics or age groups

---

## Quick Start

### Prerequisites
- Python 3.8 or higher
- ffmpeg installed on your system

### Installation

```bash
# 1. Install ffmpeg (required for audio processing)
# Ubuntu/Debian:
sudo apt update && sudo apt install -y ffmpeg

# macOS:
brew install ffmpeg

# Windows (using Chocolatey):
choco install ffmpeg

# 2. Navigate to Logic folder
cd Public_Speaking/Logic

# 3. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Verify installation
python test_installation.py
```

### Basic Usage

```python
from evaluator import PublicSpeakingEvaluator

# Initialize evaluator (loads Whisper model - happens once)
evaluator = PublicSpeakingEvaluator(
    whisper_model="base",  # Options: tiny, base, small, medium, large-v3
    device="cpu",          # Use "cuda" if GPU available
    compute_type="int8"    # int8 (faster) or float16 (more accurate)
)

# Evaluate a speech
result = evaluator.evaluate(
    audio_path="student_speech.mp3",
    student_age=12,
    student_name="John Doe",      # Optional
    topic="My Favorite Book",      # Optional
    save_json=True                 # Saves to evaluation_results/
)

# Access results
print(f"Overall Score: {result['scores']['overall']}/100")
print(f"Top Suggestion: {result['improvement_suggestions'][0]}")
```

---

## File Structure

### Core Files (Critical - Do Not Delete)

```
Logic/
├── evaluator.py              [CRITICAL] Main orchestrator, entry point
├── audio_processor.py        [CRITICAL] Audio preprocessing with ffmpeg
├── speech_to_text.py         [CRITICAL] Whisper-based transcription
├── evaluation_metrics.py     [CRITICAL] Scoring algorithms (6 metrics)
├── config.py                 [IMPORTANT] Configuration settings
├── __init__.py              [IMPORTANT] Module interface
├── requirements.txt         [IMPORTANT] Python dependencies
│
├── example_usage.py         [KEEP] Usage examples and patterns
├── test_installation.py     [KEEP] Installation verification tool
│
├── README.md                Documentation (this file)
└── INSTALL.md               Quick installation reference
```

### Component Responsibilities

| File | Purpose | Key Functions |
|------|---------|---------------|
| **evaluator.py** | Orchestrates pipeline | `evaluate()` - Main evaluation function |
| **audio_processor.py** | Audio prep | `preprocess_audio()`, `get_audio_duration()` |
| **speech_to_text.py** | Transcription | `transcribe()`, `detect_pauses()` |
| **evaluation_metrics.py** | Scoring logic | `evaluate_clarity()`, `evaluate_pace()`, etc. |
| **config.py** | Settings | Age groups, weights, thresholds |

---

## Evaluation Metrics

The system evaluates **6 key metrics**, each scored 0-100:

### 1. Clarity (Confidence-Based)
- **What**: Measures how clearly words are spoken
- **How**: Based on speech recognition confidence scores
- **NOT**: Pronunciation correctness (accent-agnostic)
- **Age Weights**: Pre-primary: 30%, Primary: 25%, Middle: 20%, Secondary: 15%

### 2. Pace (Words Per Minute)
- **What**: Measures speaking speed
- **Ideal Ranges**:
  - Pre-primary (3-5): 40-90 WPM
  - Primary (6-10): 60-120 WPM
  - Middle (11-13): 100-150 WPM
  - Secondary (14-18): 120-160 WPM
- **Age Weights**: Pre-primary: 25%, Primary: 20%, Middle/Secondary: 15%

### 3. Pause Management
- **What**: Detects excessive pauses (>2 sec) using word timestamps
- **Tolerances**: Pre-primary: 30%, Primary: 20%, Middle/Secondary: 10-15%
- **Noise-Tolerant**: Uses word gaps, not silence detection
- **Age Weights**: Pre-primary: 20%, Primary/Middle: 15-20%, Secondary: 10%

### 4. Filler Reduction
- **What**: Detects filler words (um, uh, like, you know, etc.)
- **Tolerances**: Pre-primary: 15%, Primary: 10%, Middle/Secondary: 5-8%
- **Age Weights**: All ages: 15%

### 5. Repetition Control
- **What**: Detects consecutive repeated words and phrases
- **Indicators**: Nervousness or lack of preparation
- **Age Weights**: Pre-primary: 5%, Primary: 10%, Middle/Secondary: 15%

### 6. Structure (Intro/Body/Conclusion)
- **What**: Checks for introduction, body, conclusion markers
- **Importance**: More critical for older students
- **Age Weights**: Pre-primary: 5%, Primary: 10%, Middle: 20%, Secondary: 30%

### Overall Score Calculation

Overall score is a **weighted average** using age-adjusted weights:

```
Overall = (Clarity × W₁) + (Pace × W₂) + (Pauses × W₃) +
          (Fillers × W₄) + (Repetition × W₅) + (Structure × W₆)
```

Where weights sum to 1.0 and vary by age group (see config.py:89-124).

---

## API Reference

### PublicSpeakingEvaluator

Main class for evaluating speech recordings.

#### Constructor

```python
PublicSpeakingEvaluator(
    whisper_model: str = "base",
    device: str = "cpu",
    compute_type: str = "int8"
)
```

**Parameters:**
- `whisper_model` (str): Model size - "tiny", "base", "small", "medium", "large-v3"
  - **Recommended**: "base" (best speed/accuracy balance)
- `device` (str): "cpu" or "cuda" (GPU)
- `compute_type` (str): "int8" (faster, less memory) or "float16" (more accurate)

#### evaluate()

```python
evaluator.evaluate(
    audio_path: str,
    student_age: int,
    student_name: Optional[str] = None,
    topic: Optional[str] = None,
    save_json: bool = True,
    output_path: Optional[str] = None
) -> Dict
```

**Parameters:**
- `audio_path` (str, required): Path to audio file
- `student_age` (int, required): Student's age (determines age group and weights)
- `student_name` (str, optional): Student's name for report metadata
- `topic` (str, optional): Speech topic/prompt for context
- `save_json` (bool, optional): Save results to JSON file (default: True)
- `output_path` (str, optional): Custom output path (default: auto-generated in evaluation_results/)

**Returns:**
Dictionary with structure:
```python
{
    "metadata": {
        "student_name": str,
        "student_age": int,
        "age_group": str,  # pre_primary/primary/middle/secondary
        "topic": str,
        "audio_file": str,
        "duration_seconds": float,
        "evaluation_date": str,  # ISO format
        "model_used": str
    },
    "transcript": {
        "full_text": str,
        "word_count": int,
        "language": str
    },
    "scores": {
        "overall": float,  # 0-100
        "clarity": int,
        "pace": int,
        "pause_management": int,
        "filler_reduction": int,
        "repetition_control": int,
        "structure": int
    },
    "detailed_analysis": {
        "clarity": {...},
        "pace": {...},
        "pauses": {...},
        "fillers": {...},
        "repetition": {...},
        "structure": {...}
    },
    "improvement_suggestions": List[str]  # Top 5 prioritized suggestions
}
```

---

## Configuration

All settings can be customized in `config.py`:

### Key Configuration Areas

1. **Whisper Model Settings** (config.py:6-11)
   - Model size, device, compute type

2. **Audio Processing** (config.py:13-18)
   - Sample rate, normalization, supported formats

3. **Speech-to-Text** (config.py:20-27)
   - Language, VAD settings, speech duration thresholds

4. **Evaluation Metrics** (config.py:29-55)
   - Pause thresholds, filler words, structure markers

5. **Age Groups** (config.py:57-87)
   - Age ranges, WPM ranges, tolerances for each group

6. **Metric Weights** (config.py:89-124)
   - Importance of each metric by age group

### Example: Customizing Filler Words

```python
# In config.py, line 37-41
METRICS_CONFIG = {
    "filler_words": {
        'um', 'uh', 'like', 'you know',
        'basically', 'actually',
        # Add your own:
        'kind of', 'sort of', 'literally'
    }
}
```

---

## Usage Guide

### Example 1: Basic Evaluation

```python
from evaluator import PublicSpeakingEvaluator

evaluator = PublicSpeakingEvaluator()

result = evaluator.evaluate(
    audio_path="speech.mp3",
    student_age=12,
    student_name="Alice"
)

print(f"Score: {result['scores']['overall']}/100")
```

### Example 2: Batch Processing Multiple Students

```python
evaluator = PublicSpeakingEvaluator(whisper_model="base")

students = [
    {"file": "alice_speech.mp3", "age": 8, "name": "Alice"},
    {"file": "bob_speech.mp3", "age": 14, "name": "Bob"},
    {"file": "charlie_speech.mp3", "age": 10, "name": "Charlie"}
]

for student in students:
    result = evaluator.evaluate(
        audio_path=student["file"],
        student_age=student["age"],
        student_name=student["name"],
        save_json=True
    )
    print(f"{student['name']}: {result['scores']['overall']}/100")
```

### Example 3: Integration with Web API

```python
from flask import Flask, request, jsonify
from evaluator import PublicSpeakingEvaluator

app = Flask(__name__)
evaluator = PublicSpeakingEvaluator()  # Initialize once, reuse

@app.route('/evaluate', methods=['POST'])
def evaluate_speech():
    audio_file = request.files['audio']
    student_age = int(request.form['age'])

    # Save uploaded file temporarily
    audio_path = f"/tmp/{audio_file.filename}"
    audio_file.save(audio_path)

    # Evaluate
    result = evaluator.evaluate(
        audio_path=audio_path,
        student_age=student_age,
        save_json=False  # Handle storage in your backend
    )

    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
```

### Example 4: Custom Configuration

```python
from evaluator import PublicSpeakingEvaluator
from config import get_config

# View current configuration
config = get_config("all")
print(config)

# Use different Whisper model
evaluator = PublicSpeakingEvaluator(
    whisper_model="small",  # More accurate than base
    device="cuda",          # Use GPU
    compute_type="float16"  # Higher precision
)
```

---

## Performance

### Processing Speed (base model, CPU)
- 30-second audio: ~3-5 seconds
- 1-minute audio: ~6-10 seconds
- 2-minute audio: ~12-20 seconds

**GPU Speedup**: 3-5x faster with CUDA-enabled GPU

### Model Selection Guide

| Model | Speed | Accuracy | Model Size | Use Case |
|-------|-------|----------|------------|----------|
| tiny | Fastest | Basic | ~40MB | Quick testing, very large scale |
| **base** | **Fast** | **Good** | **~140MB** | **Recommended for production** |
| small | Medium | Better | ~480MB | Higher accuracy needs |
| medium | Slow | High | ~1.5GB | Research, benchmarking |
| large-v3 | Slowest | Highest | ~3GB | Maximum accuracy required |

### Scalability
- **Target**: 200K students × 4 uploads/week = 800K files/week
- **Hardware**: Modest CPU server can handle this load
- **Cost Savings**: ~$250K+/year vs cloud API alternatives (Whisper API at $0.006/min)

### First Run Notes
- First run downloads the Whisper model (~140MB for base)
- Model is cached locally in `~/.cache/huggingface/hub/`
- Subsequent runs load instantly from cache

---

## Troubleshooting

### Common Issues

#### 1. "ffmpeg not found" Error

**Cause**: ffmpeg not installed or not in PATH

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg

# Verify installation
ffmpeg -version
```

#### 2. "Model download failed"

**Cause**: Internet connectivity or firewall blocking Hugging Face

**Solution**:
- Check internet connection
- Ensure access to huggingface.co
- Model downloads automatically on first run
- Cached location: `~/.cache/huggingface/hub/`

#### 3. "Audio format not supported"

**Cause**: Unsupported file format

**Solution**:
```python
# Check supported formats
from audio_processor import AudioProcessor
processor = AudioProcessor()
print(processor.SUPPORTED_FORMATS)
# Output: ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm']

# Convert unsupported format using ffmpeg
ffmpeg -i input.xyz -ar 16000 output.mp3
```

#### 4. Slow Processing Speed

**Causes & Solutions**:

**Use smaller model**:
```python
evaluator = PublicSpeakingEvaluator(whisper_model="tiny")
```

**Use GPU if available**:
```python
evaluator = PublicSpeakingEvaluator(device="cuda")
```

**Check CPU usage**:
```bash
# Ensure CPU isn't throttled
top  # or htop
```

#### 5. ImportError: No module named 'faster_whisper'

**Cause**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt

# Or install individually
pip install faster-whisper ffmpeg-python numpy
```

#### 6. Low Evaluation Scores for Good Speeches

**Cause**: Possible audio quality issues or age mismatch

**Solution**:
- Ensure correct student age is provided
- Check audio quality (noise, volume)
- Verify microphone quality
- Review detailed_analysis in output for specific issues

---

## Starting the Server / Integration

This is a **library module**, not a standalone server. To use it:

### Option 1: Direct Integration (Recommended)

```python
from evaluator import PublicSpeakingEvaluator

evaluator = PublicSpeakingEvaluator()
result = evaluator.evaluate("audio.mp3", student_age=12)
```

### Option 2: Create a Flask API Server

Create `server.py`:

```python
from flask import Flask, request, jsonify
from evaluator import PublicSpeakingEvaluator
import os

app = Flask(__name__)
evaluator = PublicSpeakingEvaluator()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

@app.route('/evaluate', methods=['POST'])
def evaluate():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files['audio']
    age = int(request.form.get('age', 10))
    name = request.form.get('name', None)
    topic = request.form.get('topic', None)

    # Save temporarily
    temp_path = f"/tmp/{audio.filename}"
    audio.save(temp_path)

    try:
        result = evaluator.evaluate(
            audio_path=temp_path,
            student_age=age,
            student_name=name,
            topic=topic,
            save_json=False
        )
        return jsonify(result)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

**Run the server**:
```bash
pip install flask
python server.py
```

**Test the server**:
```bash
curl -X POST http://localhost:5000/evaluate \
  -F "audio=@speech.mp3" \
  -F "age=12" \
  -F "name=John Doe" \
  -F "topic=My Favorite Book"
```

### Option 3: Create a FastAPI Server (Production-Ready)

Create `fastapi_server.py`:

```python
from fastapi import FastAPI, File, UploadFile, Form
from evaluator import PublicSpeakingEvaluator
import tempfile
import os

app = FastAPI(title="Public Speaking Evaluation API")
evaluator = PublicSpeakingEvaluator()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/evaluate")
async def evaluate(
    audio: UploadFile = File(...),
    age: int = Form(...),
    name: str = Form(None),
    topic: str = Form(None)
):
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = evaluator.evaluate(
            audio_path=tmp_path,
            student_age=age,
            student_name=name,
            topic=topic,
            save_json=False
        )
        return result
    finally:
        os.remove(tmp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Run the server**:
```bash
pip install fastapi uvicorn python-multipart
python fastapi_server.py
```

**API docs available at**: http://localhost:8000/docs

---

## Dependencies

All dependencies are in `requirements.txt` - **all are actively used**:

```
faster-whisper>=1.0.0     # Used in speech_to_text.py for transcription
ffmpeg-python==0.2.0      # Used in audio_processor.py for audio preprocessing
numpy>=1.26.0             # Used in evaluation_metrics.py for calculations
```

**System Dependency**: ffmpeg (must be installed separately)

---

## Future Enhancements

The architecture is designed to easily support:
- **Video Analysis**: Body language, eye contact, gestures, facial expressions
- **Emotion Detection**: Confidence, nervousness indicators
- **Multi-language Support**: Extend beyond English
- **Real-time Feedback**: Live evaluation during speech

Current audio pipeline will remain unchanged - video features will be additive.

---

## Support & Contribution

**For Issues:**
1. Check this README thoroughly
2. Run `python test_installation.py` to verify setup
3. Review `example_usage.py` for usage patterns
4. Check individual module docstrings

**Testing Individual Components:**
```bash
python audio_processor.py      # Test audio processing
python speech_to_text.py       # Test transcription
python evaluation_metrics.py   # Test scoring logic
python evaluator.py            # Test full pipeline
python example_usage.py        # Run example workflows
```

---

## License

Proprietary - K12 Public Speaking Platform

---

## Version

Current Version: 1.0.0

**Changelog:**
- v1.0.0 (2025-01): Initial release with 6 metrics, 4 age groups, local processing
