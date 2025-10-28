"""Configuration constants for the audio transcription service."""

import os
from pathlib import Path

DEFAULT_MODEL = "gpt-4o-transcribe"
DEFAULT_AUDIO_PATH = Path("/Users/aryamandubey/Downloads/Walpole Road.mp3")
MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB

SUPPORTED_CONTENT_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/mpeg3",
    "audio/mpg",
    "audio/mpga",
    "audio/m4a",
    "audio/wav",
    "audio/webm",
}

# API Key - Load from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file or environment.")

