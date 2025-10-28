"""Core transcription service and utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Dict, Optional

from openai import OpenAI

from config import DEFAULT_MODEL, MAX_UPLOAD_BYTES


@dataclass
class TranscriptionOptions:
    """Options for configuring audio transcription requests."""

    model: str = DEFAULT_MODEL
    response_format: Optional[str] = None
    prompt: Optional[str] = None

    def build_kwargs(self, file_handle: BinaryIO) -> Dict[str, Any]:
        """Build keyword arguments for the OpenAI API call."""
        kwargs: Dict[str, Any] = {"file": file_handle, "model": self.model}
        if self.response_format:
            kwargs["response_format"] = self.response_format
        if self.prompt:
            kwargs["prompt"] = self.prompt
        return kwargs


class TranscriptionService:
    """Service for transcribing audio files using OpenAI's Audio API."""

    def __init__(self, client: OpenAI):
        self._client = client

    def transcribe_stream(
        self,
        file_handle: BinaryIO,
        options: TranscriptionOptions,
    ) -> Any:
        """Transcribe audio from a file-like object."""
        kwargs = options.build_kwargs(file_handle)
        return self._client.audio.transcriptions.create(**kwargs)

    def transcribe_path(
        self,
        audio_path: Path,
        options: TranscriptionOptions,
    ) -> Any:
        """Transcribe audio from a file path."""
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        if not audio_path.is_file():
            raise IsADirectoryError(f"Expected a file at: {audio_path}")

        file_size = audio_path.stat().st_size
        if file_size > MAX_UPLOAD_BYTES:
            human_size = f"{file_size / (1024 * 1024):.1f} MB"
            raise ValueError(
                f"Audio file is {human_size}, which exceeds the 25 MB upload limit."
                " Please compress or split the audio and retry."
            )

        with audio_path.open("rb") as file_handle:
            return self.transcribe_stream(file_handle=file_handle, options=options)


def transcription_to_payload(transcription: Any) -> Dict[str, Any]:
    """Convert a transcription response to a dictionary payload."""
    if hasattr(transcription, "model_dump"):
        return transcription.model_dump()
    if isinstance(transcription, dict):
        return transcription

    text = getattr(transcription, "text", None)
    if text is not None:
        return {"text": text}

    return {"text": str(transcription)}

