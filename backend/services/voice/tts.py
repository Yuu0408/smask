import requests
from fastapi import HTTPException

from config import Config


# Default voice for TTS (user requested)
DEFAULT_VOICE_ID = "3VnrjnYrskPMDsapTr8X"


def synthesize_speech(text: str, voice_id: str | None = None) -> bytes:
    """
    Convert text to speech using ElevenLabs API and return audio bytes.

    Args:
        text: The text to synthesize.
        voice_id: Optional ElevenLabs voice ID. Defaults to a standard voice.

    Returns:
        Raw audio bytes (MPEG).
    """
    api_key = Config.ELEVENLABS_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing ELEVENLABS_API_KEY")

    vid = voice_id or DEFAULT_VOICE_ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}"

    headers = {
        "xi-api-key": api_key,
        "accept": "audio/mpeg",
        "Content-Type": "application/json",
    }

    payload = {
        "text": text,
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TTS request failed: {e}")

    if resp.status_code != 200:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail={"tts_error": detail})

    return resp.content
