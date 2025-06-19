from openai import OpenAI
import os
from backend.config import load_config_from_env

def speech_to_text(audio_file):
    load_config_from_env()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if not audio_file:
        raise ValueError("No audio file provided")
    transcription = client.audio.transcriptions.create(
        model="gpt-4o-transcribe", 
        file=audio_file,
        response_format="text"
    )

    return transcription
