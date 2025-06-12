from fastapi import HTTPException  # Correct import
from elevenlabs import ElevenLabs
from config import Config

class AudioService:
    def __init__(self):
        api_key = Config.ELEVENLABS_API_KEY
        self.client = ElevenLabs(api_key=api_key)

    def convert_to_audio(self, text: str) -> bytes:
        try:
            audio_gen = self.client.text_to_speech.convert(
                voice_id="UEKYgullGqaF0keqT8Bu",
                output_format="mp3_44100_128",
                text=text,
                model_id="eleven_flash_v2_5"
            )
            # Combine generator chunks into bytes
            audio_bytes = b"".join(audio_gen)
            if not audio_bytes:
                raise HTTPException(status_code=500, detail="Empty audio from ElevenLabs.")
            return audio_bytes
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error converting text to audio: {str(e)}")
