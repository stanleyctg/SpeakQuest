from openai import OpenAI
import os
from backend.config import load_config_from_env

class Services:
    def __init__(self, audio_file):
        load_config_from_env()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.audio_file = audio_file

    def speech_to_text(self):
        load_config_from_env()
        if not self.audio_file:
            raise ValueError("No audio file provided")
        transcription = self.client.audio.transcriptions.create(
            model="gpt-4o-transcribe", 
            file=self.audio_file,
            response_format="text"
        )

        return transcription
