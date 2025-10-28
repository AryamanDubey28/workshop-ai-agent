#!/usr/bin/env python3
"""
CLI helper and FastAPI service for transcribing audio with OpenAI's Audio API.

Command line:
  python transcribe_audio.py                   # uses DEFAULT_AUDIO_PATH
  python transcribe_audio.py path/to/audio.mp3

FastAPI:
  uvicorn transcribe_audio:app --reload
"""

# Import the FastAPI app for backward compatibility with uvicorn
from endpoints import app

# Import CLI main function
from cli import main

# Re-export for convenience
__all__ = ["app", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
