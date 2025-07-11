from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse, StreamingResponse

# Import backend modules (to be implemented)
from backend import transcribe, speak, avatar

app = FastAPI()

# POST /transcribe — speech-to-text (WAV to text)
@app.post("/transcribe")
def transcribe_endpoint(file: UploadFile = File(...)):
    """Endpoint for speech-to-text (WAV/MP3 to text)."""
    if not file:
        return JSONResponse(content={"error": "No file uploaded."}, status_code=400)
    result = transcribe.transcribe_audio(file)
    if "error" in result:
        return JSONResponse(content=result, status_code=400)
    return JSONResponse(content=result)

# POST /speak — text-to-speech (text to WAV)
@app.post("/speak")
async def speak_endpoint(request: Request):
    """Endpoint for text-to-speech (text to WAV)."""
    try:
        data = await request.json()
        text = data.get("text") if data else None
        if not text or not text.strip():
            return JSONResponse(content={"error": "Missing or empty 'text' field."}, status_code=400)
        wav_bytes, latency = speak.generate_speech(text)
        headers = {"X-Latency": f"{latency}s"}
        return StreamingResponse(
            iter([wav_bytes]),
            media_type="audio/wav",
            headers=headers
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

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