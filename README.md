# Public Speaking Evaluation System

A child-friendly public speaking evaluation app with Flutter frontend and FastAPI backend.

## Project Structure

```
Public_Speaking/
├── frontend/          # Flutter app (Speech Star)
│   ├── lib/           # Dart source code
│   ├── android/       # Android platform files
│   ├── ios/           # iOS platform files
│   ├── web/           # Web platform files
│   └── pubspec.yaml   # Flutter dependencies
│
├── Logic/             # FastAPI backend
│   ├── api.py         # Main FastAPI server
│   ├── evaluator.py   # Speech evaluation logic
│   ├── speech_to_text.py
│   ├── audio_processor.py
│   ├── config.py
│   └── requirements.txt
│
└── .gitignore
```

## Backend Setup (FastAPI)

```bash
# Navigate to Logic folder
cd Logic

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install ffmpeg (required for audio processing)
sudo apt install ffmpeg  # Linux
# brew install ffmpeg    # Mac

# Start the server
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: `http://localhost:8000`

API docs: `http://localhost:8000/docs`

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

## Quick Start

1. Start the backend server first (terminal 1)
2. Run the Flutter app (terminal 2)
3. The app connects to `localhost:8000` by default