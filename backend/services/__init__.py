# SpeakQuest/backend/services/__init__.py

from .whisper_wrap import speech_to_text

__all__ = ["speech_to_text"]
