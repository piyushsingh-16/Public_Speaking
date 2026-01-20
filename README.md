# Public Speaking Evaluation System

A child-friendly public speaking evaluation app with Flutter frontend and FastAPI backend. Designed for K-12 students with age-appropriate feedback and gamified UI.

## Features

- **9 Evaluation Metrics**: Clarity, Pace, Pauses, Fillers, Repetition, Structure, Loudness, Pitch Variation, Stamina
- **Age-Appropriate Feedback**: Different output formats for ages 3-5, 6-8, 9-10, and 11+
- **Gamified UI**: Badges, characters, progress bars for younger students
- **Local Processing**: No cloud API costs, complete privacy
- **Dual Response**: Raw evaluation for teachers + child-friendly presentation

## Project Structure

```
Public_Speaking/
├── frontend/              # Flutter app (Speech Star)
│   ├── lib/               # Dart source code
│   ├── android/           # Android platform
│   ├── ios/               # iOS platform
│   ├── web/               # Web platform
│   └── pubspec.yaml       # Flutter dependencies
│
├── Logic/                 # FastAPI backend v3.0
│   ├── api.py             # Main FastAPI server
│   ├── evaluator.py       # Speech evaluation pipeline
│   ├── config/            # Configuration settings
│   ├── processors/        # Audio & speech processing
│   ├── metrics/           # 9 evaluation metrics
│   ├── presenters/        # Age-appropriate output
│   ├── models/            # Data models (Pydantic)
│   ├── tests/             # Test suite (35 tests)
│   └── requirements.txt   # Python dependencies
│
└── README.md              # This file
```

## Age Groups & Output

| Age Group | Ages | UI Format | Key Features |
|-----------|------|-----------|--------------|
| Pre-primary | 3-5 | Character-based | Lion/mouse voice, single badge, TTS |
| Lower-primary | 6-8 | Icon-based | 3 metric icons, badges, no numbers |
| Upper-primary | 9-10 | Progress bars | 4 bars, single tip, badge collection |
| Middle/Secondary | 11+ | Full analysis | All scores, detailed feedback |

## Backend Setup (FastAPI)

```bash
# Navigate to Logic folder
cd Logic

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install ffmpeg (required for audio processing)
sudo apt install ffmpeg  # Linux
# brew install ffmpeg    # Mac

# Run tests
PYTHONPATH=.. pytest tests/ -v

# Start the server
uvicorn api:app --reload --host 0.0.0.0 --port 8000

```

**Server**: `http://localhost:8000`
**API Docs**: `http://localhost:8000/docs`

## Frontend Setup (Flutter)

```bash
# Navigate to frontend folder
cd frontend

# Get dependencies
flutter pub get

# Run on connected device/emulator
flutter run

# Run on specific platform
flutter run -d chrome    # Web
flutter run -d linux     # Linux desktop
flutter run -d android   # Android device/emulator
```

## API Usage

### Upload & Evaluate

```bash
curl -X POST http://localhost:8000/evaluate \
  -F "audio_file=@speech.mp3" \
  -F "student_age=8" \
  -F "student_name=Alice"
```

### Response Structure

```json
{
  "job_id": "uuid",
  "status": "completed",
  "raw_evaluation": {
    "scores": { "overall": 75, "clarity": 80, "loudness": 85 },
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

## Quick Start

1. **Start backend** (Terminal 1):
   ```bash
   cd Logic && source venv/bin/activate
   uvicorn Logic.api:app --reload --port 8000
   ```

2. **Run Flutter app** (Terminal 2):
   ```bash
   cd frontend && flutter run
   ```

3. The app connects to `localhost:8000` by default

## Evaluation Metrics

### Transcript-Based
- **Clarity** - Speech recognition confidence
- **Pace** - Words per minute
- **Pause Management** - Excessive pause detection
- **Filler Reduction** - "um", "uh", "like" detection
- **Repetition Control** - Word/phrase repetition
- **Structure** - Intro/body/conclusion

### Audio-Based (New in v3.0)
- **Loudness** - Volume/energy analysis
- **Pitch Variation** - Prosody/expression
- **Stamina** - Energy consistency

## Tech Stack

**Backend**:
- FastAPI + Uvicorn
- faster-whisper (local speech recognition)
- librosa (audio analysis)
- ffmpeg (audio preprocessing)

**Frontend**:
- Flutter/Dart
- Cross-platform (iOS, Android, Web, Desktop)

## Version

- **Backend**: v3.0 (9 metrics, age-appropriate output)
- **Frontend**: v1.0

## License

Proprietary - K12 Public Speaking Platform
