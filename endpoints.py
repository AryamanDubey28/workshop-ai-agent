"""FastAPI endpoints for audio transcription service."""

import io
import os
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from openai import OpenAI


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  

from config import DEFAULT_MODEL, MAX_UPLOAD_BYTES, OPENAI_API_KEY, SUPPORTED_CONTENT_TYPES
from service import TranscriptionOptions, TranscriptionService, transcription_to_payload

# Set API key for OpenAI
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

app = FastAPI(title="Audio Transcription API")


def _get_service() -> TranscriptionService:
    """Factory function to create a TranscriptionService instance."""
    return TranscriptionService(OpenAI())


@app.post("/transcribe")
async def transcribe_endpoint(
    file: UploadFile = File(...),
    model: str = DEFAULT_MODEL,
    response_format: Optional[str] = None,
    prompt: Optional[str] = None,
) -> JSONResponse:
    """
    Transcribe an uploaded audio file.

    Args:
        file: Audio file to transcribe
        model: Model to use for transcription
        response_format: Optional response format (json, text, srt, etc.)
        prompt: Optional prompt to guide transcription

    Returns:
        JSONResponse containing the transcription result
    """
    if file.content_type and file.content_type not in SUPPORTED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported content type: {file.content_type}",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(contents) > MAX_UPLOAD_BYTES:
        human_size = f"{len(contents) / (1024 * 1024):.1f} MB"
        raise HTTPException(
            status_code=413,
            detail=f"File is {human_size}; limit is 25 MB. Please compress or split it.",
        )

    buffer = io.BytesIO(contents)
    buffer.name = file.filename or "audio_upload.mp3"
    buffer.seek(0)

    service = _get_service()
    options = TranscriptionOptions(
        model=model, response_format=response_format, prompt=prompt
    )

    try:
        transcription = service.transcribe_stream(
            file_handle=buffer,
            options=options,
        )
    except Exception as exc:  
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    payload = transcription_to_payload(transcription)
    return JSONResponse(content=payload)


@app.post("/insights")
async def insights_endpoint() -> JSONResponse:
    """
    Generate AI insights from a transcript (dummy implementation).

    Returns:
        JSONResponse containing insights, themes, questions, gaps, and risks
    """
    # Dummy response for now
    dummy_insights = {
        "response": {
            "insights": [
                "Sender requests a short (15-min) meeting to locate/receive docs or an intro to Workshop AI and quickly assess what can be delivered before year-end — indicates urgency and timeboxed planning.",
                "Lack of shared documentation is an immediate blocker for scoping deliverables; the meeting will likely focus on prioritisation and quick feasibility checks."
            ],
            "themes": [
                "Time-constrained year-end delivery planning",
                "Need for foundational documentation/intro to enable scoping"
            ],
            "suggested_questions": [
                "Which specific projects or deliverables should we assess for the remainder of the year (priorities)?",
                "Can you share any existing docs or a one-page intro to Workshop AI before the meeting, and confirm the firm year-end deadline and available effort?"
            ],
            "gaps_and_ambiguities": [
                "No documentation/shared materials provided or referenced.",
                "Unclear scope/prioritisation of 'what we can deliver' and exact deadline or resource availability."
            ],
            "risks_and_dependencies": [
                "Insufficient time and detail to accurately scope work before year-end if docs aren't provided in advance.",
                "Meeting effectiveness depends on stakeholder availability and presence of at least minimal documentation or clear priorities."
            ]
        }
    }
    return JSONResponse(content=dummy_insights)

