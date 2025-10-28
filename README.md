# Workshop AI Agent 

An AI-powered audio transcription service built with OpenAI's Whisper API. This project includes a CLI tool, REST API server, and an interactive Streamlit web interface for recording and transcribing audio.


## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- FFmpeg (required for audio conversion in the web UI)

### Installing FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/AryamanDubey28/workshop-ai-agent.git
cd workshop-ai-agent
```

### 2. Set Up Environment

Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Configure API Key

Create a `.env` file in the project root:
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

Or set it as an environment variable:
```bash
export OPENAI_API_KEY="your_api_key_here"
```


## 💻 Usage

### Web Interface 

The easiest way to use the transcription service is through the web interface.

**Step 1:** Start the API server
```bash
uvicorn endpoints:app --reload
```

The API will be available at `http://localhost:8000`

**Step 2:** In a new terminal, start the Streamlit app
```bash
streamlit run frontend.py
```

The web interface will open automatically in your browser at `http://localhost:8501`

**Step 3:** Record and transcribe
1. Click "Tap to record" to start recording audio
2. Click "Send to Transcribe" to get your transcript
3. View the results in the Transcript column

**Available options:**
- `--model`: Model to use (default: `gpt-4o-transcribe`)
  - Options: `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `whisper-1`
- `--response-format`: Output format
  - Options: `json`, `text`, `srt`, `verbose_json`, `vtt`, `diarized_json`
- `--prompt`: Optional prompt to guide transcription
- `--save-to`: Save transcript to file instead of printing

**Python example:**
```python
import requests

with open("audio.mp3", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/transcribe",
        files=files,
        data={"model": "gpt-4o-transcribe"}
    )
    
print(response.json()["text"])
```

## 🏗️ Project Structure

```
workshop-ai-agent/
├── cli.py              # Command-line interface
├── endpoints.py        # FastAPI server with /transcribe endpoint
├── frontend.py         # Streamlit web interface
├── service.py          # Core transcription service logic
├── config.py           # Configuration constants
├── transcribe_audio.py # Audio transcription utilities
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## 🎯 Supported Audio Formats

- MP3 (`.mp3`)
- MP4 Audio (`.m4a`, `.mp4`)
- WAV (`.wav`)
- WebM (`.webm`)
- MPEG (`.mpeg`, `.mpg`, `.mpga`)

**Maximum file size:** 25 MB

## 🔧 Configuration

All configuration is done through environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |

You can also modify constants in `config.py`:
- `DEFAULT_MODEL`: Default transcription model
- `MAX_UPLOAD_BYTES`: Maximum file upload size
- `SUPPORTED_CONTENT_TYPES`: Allowed audio formats


## 📝 API Reference

### POST `/transcribe`

Transcribe an uploaded audio file.

**Parameters:**
- `file` (file, required): Audio file to transcribe
- `model` (string, optional): Model to use (default: `gpt-4o-transcribe`)
- `response_format` (string, optional): Response format
- `prompt` (string, optional): Prompt to guide transcription

**Response:**
```json
{
  "text": "Transcribed text appears here..."
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (empty file)
- `413`: File too large (>25 MB)
- `415`: Unsupported content type
- `502`: Transcription service error
