"""Command-line interface for audio transcription."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional

from openai import OpenAI

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, assume env vars are set

from config import DEFAULT_AUDIO_PATH, DEFAULT_MODEL, OPENAI_API_KEY
from service import TranscriptionOptions, TranscriptionService, transcription_to_payload

# Set API key for OpenAI
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Transcribe an audio file with OpenAI's speech-to-text models."
    )
    parser.add_argument(
        "audio_path",
        nargs="?",
        default=DEFAULT_AUDIO_PATH,
        type=Path,
        help=(
            "Path to the audio file (mp3, mp4, mpga, m4a, wav, webm). "
            "Defaults to the Walpole Road recording."
        ),
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=(
            "Transcription model to use. Examples: gpt-4o-transcribe, "
            "gpt-4o-mini-transcribe, whisper-1."
        ),
    )
    parser.add_argument(
        "--response-format",
        choices=["json", "text", "srt", "verbose_json", "vtt", "diarized_json"],
        help="Optional response format override (varies by model).",
    )
    parser.add_argument(
        "--prompt",
        help="Optional prompt to guide the transcription (not supported by diarization).",
    )
    parser.add_argument(
        "--save-to",
        type=Path,
        help="Optional file path to save the transcript instead of printing to stdout.",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    service = TranscriptionService(OpenAI())
    options = TranscriptionOptions(
        model=args.model, response_format=args.response_format, prompt=args.prompt
    )

    try:
        transcription = service.transcribe_path(
            audio_path=args.audio_path,
            options=options,
        )
    except Exception as exc:  # noqa: BLE001
        parser.exit(2, f"{parser.prog}: error: {exc}\n")

    payload = transcription_to_payload(transcription)
    text = payload.get("text")
    if text is None:
        parser.exit(2, f"{parser.prog}: error: response missing `text` field.\n")

    if args.save_to:
        args.save_to.parent.mkdir(parents=True, exist_ok=True)
        args.save_to.write_text(text, encoding="utf-8")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

