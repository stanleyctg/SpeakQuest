from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
from backend.services.whisper_wrap import speech_to_text 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/upload-audio")
async def upload_audio_file(audio: UploadFile = File(...)):
    contents = await audio.read()
    size = len(contents)
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", audio.filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    print(f"Received file {audio.filename!r}, size={size} bytes")
    return {
        "filename": audio.filename,
        "size": size,
        "content_type": audio.content_type
    }

@app.post("/api/feedback")
async def feedback():
    # Get absolute path to recording
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(base_dir, "uploads", "recording.webm")
    audio_path = os.path.abspath(audio_path)

    audio_file = open(audio_path, "rb")
    transcription = speech_to_text(audio_file)

    return {
        "transcription": transcription,
        "audio_path": audio_path
    }

    # Wire this transcript to chatgpt service then return the response