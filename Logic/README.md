# Public Speaking Evaluation System - Backend

AI-powered speech evaluation for school students (Ages 3-18) with age-appropriate feedback.

## Version 3.0 Features

- **9 Evaluation Metrics**: Clarity, Pace, Pauses, Fillers, Repetition, Structure + **Loudness, Pitch Variation, Stamina**
- **Age-Appropriate Output**: Different presentation formats for different age groups
- **Dual API Response**: `raw_evaluation` (teachers) + `child_presentation` (gamified UI)
- **Local Processing**: No API costs, complete privacy

## Architecture

```
Logic/
├── api.py                    # FastAPI server v3.0
├── evaluator.py              # Main pipeline orchestrator
├── requirements.txt          # Dependencies
│
├── config/                   # Configuration
│   ├── settings.py           # General settings
│   ├── age_groups.py         # Age group definitions & weights
│   ├── metrics_config.py     # Metric thresholds
│   └── presentation_config.py # Badges, messages, icons
│
├── processors/               # Audio/Speech processing
│   ├── audio_processor.py    # Audio preprocessing (ffmpeg)
│   ├── speech_to_text.py     # Whisper transcription
│   └── audio_features.py     # Waveform analysis (librosa)
│
├── metrics/                  # Evaluation metrics
│   ├── base.py               # Base metric class
│   ├── clarity.py            # Speech clarity
│   ├── pace.py               # Speaking speed
│   ├── pauses.py             # Pause management
│   ├── fillers.py            # Filler word detection
│   ├── repetition.py         # Repetition detection
│   ├── structure.py          # Speech structure
│   ├── loudness.py           # Volume/energy analysis
│   ├── pitch_variation.py    # Pitch/prosody analysis
│   ├── stamina.py            # Energy consistency
│   └── evaluator.py          # Combined metrics evaluator
│
├── presenters/               # Age-appropriate output
│   ├── base.py               # Base presenter
│   ├── pre_primary.py        # Ages 3-5 (character-based)
│   ├── lower_primary.py      # Ages 6-8 (icon-based)
│   ├── upper_primary.py      # Ages 9-10 (progress bars)
│   ├── detailed.py           # Ages 11+ (full analysis)
│   └── factory.py            # Presenter factory
│
├── models/                   # Data models (Pydantic)
│   ├── audio_features.py     # AudioFeatures dataclass
│   ├── evaluation_result.py  # EvaluationResult models
│   └── child_presentation.py # Child presentation models
│
└── tests/                    # Test suite
    ├── test_metrics.py       # Metrics tests
    ├── test_presenters.py    # Presenter tests
    └── fixtures/             # Test audio files
```

## Quick Start

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install ffmpeg (required)
sudo apt install ffmpeg  # Linux
# brew install ffmpeg    # macOS

# 4. Run tests
PYTHONPATH=.. pytest tests/ -v

# 5. Start API server
uvicorn Logic.api:app --reload --host 0.0.0.0 --port 8000
```

## Age Groups & Output Formats

| Age Group | Ages | Output Format |
|-----------|------|---------------|
| Pre-primary | 3-5 | Character-based (lion/mouse voice), badges, TTS |
| Lower-primary | 6-8 | Icon-based metrics (3 icons), badges, no numbers |
| Upper-primary | 9-10 | Progress bars (4), single improvement tip, badges |
| Middle/Secondary | 11+ | Full detailed analysis with multiple suggestions |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/evaluate` | POST | Upload audio file for evaluation |
| `/evaluate/path` | POST | Evaluate audio from server path |
| `/jobs/{job_id}` | GET | Get job status and results |
| `/jobs` | GET | List all jobs |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger API documentation |

## Response Structure

```json
{
  "job_id": "uuid",
  "status": "completed",
  "raw_evaluation": {
    "metadata": { "student_age": 8, "age_group": "lower_primary" },
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

## Evaluation Metrics

### Transcript-Based (6)
1. **Clarity** - Speech recognition confidence
2. **Pace** - Words per minute vs age-appropriate range
3. **Pause Management** - Excessive pause detection
4. **Filler Reduction** - "um", "uh", "like" detection
5. **Repetition Control** - Word/phrase repetition
6. **Structure** - Intro/body/conclusion detection

### Audio-Based (3) - NEW in v3.0
7. **Loudness** - RMS energy analysis (too soft/loud/optimal)
8. **Pitch Variation** - Prosody analysis (monotone/expressive/erratic)
9. **Stamina** - Energy consistency over time

## Configuration

All settings in `config/`:
- `settings.py` - Whisper model, audio settings
- `age_groups.py` - Age ranges, WPM ranges, metric weights
- `metrics_config.py` - Thresholds for each metric
- `presentation_config.py` - Badges, messages, icons

## Testing

```bash
# Run all tests
PYTHONPATH=.. pytest tests/ -v

# Run specific test file
PYTHONPATH=.. pytest tests/test_metrics.py -v

# Run with coverage
PYTHONPATH=.. pytest tests/ --cov=. --cov-report=html
```

## Dependencies

- `faster-whisper` - Local speech recognition
- `ffmpeg-python` - Audio preprocessing
- `librosa` - Audio feature extraction (RMS, pitch)
- `numpy`, `pydantic` - Data handling
- `fastapi`, `uvicorn` - API server

## Version History

- **v3.0** (2025-01): Age-appropriate output, 3 new audio metrics, modular architecture
- **v2.0** (2025-01): FastAPI with async jobs, webhook support
- **v1.0** (2025-01): Initial release with 6 metrics
