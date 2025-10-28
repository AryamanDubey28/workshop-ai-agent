"""Streamlit frontend for recording audio and sending it to the transcription API."""

from __future__ import annotations

import io
from typing import Any, Dict, Optional

import requests
import streamlit as st

try:
    from pydub import AudioSegment
except ImportError:  
    AudioSegment = None


DEFAULT_TRANSCRIBE_URL = "http://localhost:8000/transcribe"
DEFAULT_INSIGHTS_URL = "http://localhost:8000/insights"


def convert_audio_to_mp3(audio_bytes: bytes, source_format: str = None) -> bytes:
    """Convert audio bytes to MP3 using pydub/ffmpeg.
    
    Args:
        audio_bytes: Raw audio data
        source_format: Original format (e.g., 'wav', 'ogg'). If None, pydub will auto-detect.
    
    Returns:
        MP3-encoded audio bytes
    """
    if AudioSegment is None:
        raise RuntimeError(
            "pydub is required to convert audio to MP3. "
            "Install it with `pip install pydub` and ensure FFmpeg is on your PATH."
        )

    audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format=source_format)
    mp3_buffer = io.BytesIO()
    audio_segment.export(mp3_buffer, format="mp3")
    return mp3_buffer.getvalue()


def post_for_transcription(mp3_bytes: bytes, endpoint: str) -> Dict[str, Any]:
    """Send the MP3 bytes to the backend transcription endpoint."""
    files = {
        "file": ("recording.mp3", mp3_bytes, "audio/mpeg"),
    }
    response = requests.post(endpoint, files=files, timeout=60)
    response.raise_for_status()
    return response.json()


def extract_text(payload: Dict[str, Any]) -> Optional[str]:
    """Best-effort extraction of transcription text from the backend payload."""
    text = payload.get("text")
    if isinstance(text, str) and text.strip():
        return text.strip()
    return None


def fetch_insights(endpoint: str) -> Dict[str, Any]:
    """Fetch AI insights from the backend insights endpoint."""
    response = requests.post(endpoint, timeout=60)
    response.raise_for_status()
    return response.json()


def render_insight_card(title: str, items: list[str]) -> None:
    """Render a single insight card with a title and list of items."""
    # Format title for display (replace underscores with spaces, capitalize)
    display_title = title.replace("_", " ").title()
    
    # Create card HTML
    card_html = f"""
    <div style="
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    ">
        <h3 style="
            color: #667eea;
            margin-top: 0;
            margin-bottom: 1rem;
            font-size: 1.2rem;
            font-weight: 600;
        ">{display_title}</h3>
        <ul style="
            margin: 0;
            padding-left: 1.5rem;
            color: #333;
            line-height: 1.8;
        ">
    """
    
    for item in items:
        card_html += f'<li style="margin-bottom: 0.5rem;">{item}</li>'
    
    card_html += """
        </ul>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="Workshop AI", layout="wide", page_icon="⚡")
    
    # Custom CSS for better styling
    st.markdown(
        """
        <style>
        /* Main title styling */
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            padding-bottom: 1rem;
        }
        
        /* Improve subheaders */
        h2 {
            color: #667eea;
            font-weight: 600;
        }
        
        /* Better button styling */
        .stButton>button {
            font-weight: 500;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        /* Info box styling */
        .stInfo {
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.title("Workshop AI")
    st.markdown("*Transcribe audio with AI-powered accuracy*")
    st.divider()

    if "transcript" not in st.session_state:
        st.session_state["transcript"] = None
    if "transcription_error" not in st.session_state:
        st.session_state["transcription_error"] = None
    if "raw_payload" not in st.session_state:
        st.session_state["raw_payload"] = None
    if "insights" not in st.session_state:
        st.session_state["insights"] = None
    if "insights_error" not in st.session_state:
        st.session_state["insights_error"] = None

    # Use default endpoint
    endpoint = DEFAULT_TRANSCRIBE_URL

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Record Audio")
        st.markdown("Click below to start recording your audio")
        audio_file = st.experimental_audio_input("Tap to record", key="microphone")
        transcribe_clicked = st.button(
            "Send to Transcribe",
            type="primary",
            use_container_width=True,
            disabled=audio_file is None,
        )

    if transcribe_clicked:
        st.session_state["transcription_error"] = None
        st.session_state["transcript"] = None
        st.session_state["raw_payload"] = None

        if not endpoint:
            st.session_state["transcription_error"] = (
                "Please provide a valid endpoint URL."
            )
        elif audio_file is None:
            st.session_state["transcription_error"] = (
                "No audio captured. Please record again."
            )
        else:
            with st.spinner("Converting audio and contacting the transcription API..."):
                try:
                    # The recorded audio from st.experimental_audio_input is in WAV format
                    wav_bytes = audio_file.getvalue()
                    mp3_bytes = convert_audio_to_mp3(wav_bytes, source_format="wav")
                    
                    payload = post_for_transcription(mp3_bytes, endpoint)
                    st.session_state["raw_payload"] = payload
                    transcript_text = extract_text(payload)
                    if transcript_text:
                        st.session_state["transcript"] = transcript_text
                    else:
                        st.session_state["transcription_error"] = (
                            "Received a response but could not find transcription text. "
                            "Check the raw payload for details."
                        )
                except Exception as exc:  # noqa: BLE001
                    st.session_state["transcription_error"] = str(exc)

    with col2:
        st.subheader("Transcript")
        
        if st.session_state["transcription_error"]:
            st.error(st.session_state["transcription_error"])
        elif st.session_state["transcript"]:
            # Display transcript in a nice styled container
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    margin: 1rem 0;
                ">
                    <div style="
                        background: white;
                        padding: 1.5rem;
                        border-radius: 8px;
                        color: #333;
                        font-size: 1.1rem;
                        line-height: 1.8;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    ">
                        {st.session_state["transcript"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            # Add copy button
            if st.button("Copy Transcript", use_container_width=True):
                st.toast("Transcript copied to clipboard!")
        else:
            st.info("Record audio and send it to see the transcription here.")

        if st.session_state["raw_payload"]:
            with st.expander("View Raw Response"):
                st.json(st.session_state["raw_payload"])

    with col3:
        st.subheader("AI Insights")
        st.markdown("Get AI-powered analysis of your transcript")
        
        insights_clicked = st.button(
            "Generate Insights",
            disabled=st.session_state["transcript"] is None,
            help="Generate AI insights for your transcript.",
            type="primary",
            use_container_width=True,
        )
        
        if insights_clicked:
            st.session_state["insights_error"] = None
            st.session_state["insights"] = None
            
            with st.spinner("Generating AI insights..."):
                try:
                    insights_data = fetch_insights(DEFAULT_INSIGHTS_URL)
                    response_data = insights_data.get("response", {})
                    if response_data:
                        st.session_state["insights"] = response_data
                    else:
                        st.session_state["insights_error"] = (
                            "Received a response but could not find insights data."
                        )
                except Exception as exc:  # noqa: BLE001
                    st.session_state["insights_error"] = str(exc)
        
        # Display insights
        if st.session_state["insights_error"]:
            st.error(st.session_state["insights_error"])
        elif st.session_state["insights"]:
            for key, value in st.session_state["insights"].items():
                if isinstance(value, list):
                    render_insight_card(key, value)
        else:
            st.info("Transcribe audio first, then generate insights to see AI-powered analysis here.")


if __name__ == "__main__":
    main()
