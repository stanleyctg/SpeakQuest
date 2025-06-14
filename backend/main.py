from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/upload-audio")
async def upload_audio_file(audio: UploadFile = File(...)):
    contents = await audio.read()
    size = len(contents)
    os.makedirs("uploads", exist_ok=True)
    # file_path = os.path.join("uploads", audio.filename)
    # with open(file_path, "wb") as f:
    #     f.write(contents)
    print(f"Received file {audio.filename!r}, size={size} bytes")
    return {
        "filename": audio.filename,
        "size": size,
        "content_type": audio.content_type
    }
