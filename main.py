from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Import backend modules (to be implemented)
from backend import transcribe, speak, avatar

app = FastAPI()

# POST /transcribe — speech-to-text (WAV to text)
@app.post("/transcribe")
def transcribe_audio():
    """Endpoint for speech-to-text (WAV to text)."""
    # TODO: Implement speech-to-text logic
    pass

# POST /speak — text-to-speech (text to WAV)
@app.post("/speak")
def speak_text():
    """Endpoint for text-to-speech (text to WAV)."""
    # TODO: Implement text-to-speech logic
    pass

# POST /generate-avatar — audio+image to video
@app.post("/generate-avatar")
def generate_avatar():
    """Endpoint for generating avatar video from audio and image."""
    # TODO: Implement avatar video generation logic
    pass

# GET /status — returns { "status": "ok" }
@app.get("/status")
def status():
    """Health check endpoint."""
    return JSONResponse(content={"status": "ok"})

# For serverless: entrypoint is app (FastAPI instance) 