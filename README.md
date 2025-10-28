# Workshop AI Agent 🎙️

An AI-powered audio transcription service built with OpenAI's Whisper API. This project includes a CLI tool, REST API server, and an interactive Streamlit web interface for recording and transcribing audio.

## ✨ Features

- 🎤 **Record audio** directly in your browser
- 🤖 **AI-powered transcription** using OpenAI's latest models
- 🔌 **RESTful API** for easy integration
- 💻 **Command-line interface** for batch processing
- 🎨 **Beautiful web UI** built with Streamlit
- 🔒 **Secure** environment variable management

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

**⚠️ Important:** Never commit your `.env` file or API keys to version control!

## 💻 Usage

### Option 1: Web Interface (Recommended)

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

### Option 2: Command-Line Interface

Transcribe an audio file directly from the command line:

```bash
python cli.py path/to/audio.mp3
```

**Advanced CLI usage:**

```bash
# Specify a different model
python cli.py audio.mp3 --model whisper-1

# Change response format
python cli.py audio.mp3 --response-format srt

# Add a prompt to guide transcription
python cli.py audio.mp3 --prompt "This is a medical interview"

# Save output to a file
python cli.py audio.mp3 --save-to transcript.txt
```

**Available options:**
- `--model`: Model to use (default: `gpt-4o-transcribe`)
  - Options: `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `whisper-1`
- `--response-format`: Output format
  - Options: `json`, `text`, `srt`, `verbose_json`, `vtt`, `diarized_json`
- `--prompt`: Optional prompt to guide transcription
- `--save-to`: Save transcript to file instead of printing

### Option 3: API Integration

You can integrate the transcription API into your own applications.

**Start the server:**
```bash
uvicorn endpoints:app --reload --host 0.0.0.0 --port 8000
```

**API Documentation:** Visit `http://localhost:8000/docs` for interactive API documentation

**Example API call:**

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.mp3" \
  -F "model=gpt-4o-transcribe"
```

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

## 🛠️ Development

### Running in Development Mode

**API Server:**
```bash
uvicorn endpoints:app --reload --log-level debug
```

**Frontend:**
```bash
streamlit run frontend.py --server.runOnSave true
```

### Running Tests

```bash
# Add your test commands here
pytest
```

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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [OpenAI's Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- Frontend powered by [Streamlit](https://streamlit.io/)
- API built with [FastAPI](https://fastapi.tiangolo.com/)

## 🐛 Troubleshooting

### "OPENAI_API_KEY environment variable is not set"
- Make sure you've created a `.env` file with your API key
- Or set the environment variable: `export OPENAI_API_KEY="your_key"`

### "pydub is required to convert audio to MP3"
- Install pydub: `pip install pydub`
- Install FFmpeg (see Prerequisites section)

### "Connection refused" when using web interface
- Make sure the API server is running: `uvicorn endpoints:app --reload`
- Check that it's running on `http://localhost:8000`

### "File too large" error
- Maximum file size is 25 MB
- Compress your audio file or split it into smaller chunks
- Consider using a lower bitrate for recording

## 📞 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/AryamanDubey28/workshop-ai-agent/issues) on GitHub.

---

Made with ❤️ by the Workshop AI Team

