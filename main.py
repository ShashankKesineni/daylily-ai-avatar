from fastapi import FastAPI, UploadFile, File, Request, Form, Header, Cookie, Response, Query
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import shutil
from typing import Optional

# Import backend modules (to be implemented)
from backend import transcribe, speak, avatar
from backend.session_manager import get_or_create_session

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Lazy model loading flags ---
models_loaded = {
    'whisper': False,
    'tts': False,
    'avatar': False
}

def lazy_load_whisper():
    if not models_loaded['whisper']:
        transcribe.lazy_load_model()
        models_loaded['whisper'] = True

def lazy_load_tts():
    if not models_loaded['tts']:
        speak.lazy_load_model()
        models_loaded['tts'] = True

def lazy_load_avatar():
    if not models_loaded['avatar']:
        avatar.lazy_load_model()
        models_loaded['avatar'] = True

@app.post("/warmup")
def warmup():
    """Endpoint to pre-load all heavy ML models for cold start mitigation."""
    lazy_load_whisper()
    lazy_load_tts()
    lazy_load_avatar()
    return {"status": "warmed up"}

# POST /transcribe — speech-to-text (WAV to text)
@app.post("/transcribe")
async def transcribe_endpoint(
    request: Request,
    response: Response,
    audio: UploadFile = File(None),
    file: UploadFile = File(None),
    session_id: str = Header(None),
    session_cookie: str = Cookie(None),
    session_id_query: Optional[str] = Query(None)
):
    """Endpoint for speech-to-text (WAV/MP3 to text) with session management. Accepts 'audio' or 'file' field."""
    lazy_load_whisper()
    sid = get_or_create_session(session_id or session_cookie or session_id_query)
    response.headers["X-Session-ID"] = sid
    upload = audio or file
    if not upload:
        return JSONResponse(content={"error": "No file uploaded."}, status_code=400)
    print(f"Received file: {upload.filename}, content_type: {upload.content_type}, size: {upload.size if hasattr(upload, 'size') else 'unknown'}")  # Debug log
    result = transcribe.transcribe_audio(upload)
    print(f"Transcription result: {result}")  # Debug log
    if "error" in result:
        return JSONResponse(content=result, status_code=400)
    return JSONResponse(content=result)

# POST /speak — text-to-speech (text to WAV)
@app.post("/speak")
async def speak_endpoint(
    request: Request,
    response: Response,
    session_id: str = Header(None),
    session_cookie: str = Cookie(None)
):
    """Endpoint for text-to-speech (text to WAV) with session management."""
    lazy_load_tts()
    sid = get_or_create_session(session_id or session_cookie)
    response.headers["X-Session-ID"] = sid
    try:
        data = await request.json()
        text = data.get("text") if data else None
        if not text or not text.strip():
            return JSONResponse(content={"error": "Missing or empty 'text' field."}, status_code=400)
        wav_bytes, latency = speak.generate_speech(text)
        headers = {"X-Latency": f"{latency}s", "X-Session-ID": sid}
        return StreamingResponse(
            iter([wav_bytes]),
            media_type="audio/wav",
            headers=headers
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# POST /generate-avatar — audio+image to video
@app.post("/generate-avatar")
async def generate_avatar_endpoint(
    response: Response,
    audio: UploadFile = File(...),
    image: UploadFile = File(None),
    session_id: str = Header(None),
    session_cookie: str = Cookie(None)
):
    lazy_load_avatar()
    sid = get_or_create_session(session_id or session_cookie)
    response.headers["X-Session-ID"] = sid
    if not audio:
        return JSONResponse(content={"error": "Missing audio file."}, status_code=400)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        try:
            shutil.copyfileobj(audio.file, tmp_audio)
            tmp_audio.flush()
            audio_path = tmp_audio.name
            image_path = None
            if image:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_image:
                    ext = ".jpg" if image.content_type in ["image/jpeg", "image/jpg"] else ".png"
                    tmp_image.close()
                    with open(tmp_image.name, "wb") as img_out:
                        shutil.copyfileobj(image.file, img_out)
                    image_path = tmp_image.name
            video_path, latency = avatar.generate_avatar(audio_path, image_path)
            headers = {"X-Latency": f"{latency}s", "X-Session-ID": sid}
            if video_path and os.path.exists(video_path):
                return FileResponse(
                    video_path,
                    media_type="video/mp4",
                    filename="avatar.mp4",
                    headers=headers
                )
            else:
                return JSONResponse(content={"error": "Failed to generate video file"}, status_code=500)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
        finally:
            temp_files = [tmp_audio.name]
            if 'image_path' in locals() and image_path:
                temp_files.append(image_path)
            for path in temp_files:
                if path and os.path.exists(path):
                    os.remove(path)

# GET /status — returns { "status": "ok" }
@app.get("/status")
def status():
    """Health check endpoint."""
    return JSONResponse(content={"status": "ok"})

@app.get("/")
def root():
    return JSONResponse({"message": "Welcome to the Daylily AI Avatar API! See /docs for usage."})

@app.get("/debug")
def debug():
    """Debug endpoint to check what's loaded."""
    return JSONResponse({
        "message": "Debug endpoint",
        "endpoints": [
            "/transcribe",
            "/speak", 
            "/generate-avatar",
            "/status",
            "/warmup"
        ]
    })

@app.post("/avatar-fix")
async def avatar_fix(audio: UploadFile = File(...), session_id: str = Header(None)):
    return JSONResponse({
        "message": "Avatar fix endpoint working",
        "audio_filename": audio.filename,
        "session_id": session_id
    })

# For serverless: entrypoint is app (FastAPI instance) 