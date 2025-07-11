from fastapi import FastAPI, UploadFile, File, Request, Form, Header, Cookie, Response
from fastapi.responses import JSONResponse, StreamingResponse
import os
import tempfile
import shutil

# Import backend modules (to be implemented)
from backend import transcribe, speak, avatar
from backend.session_manager import get_or_create_session

app = FastAPI()

# POST /transcribe — speech-to-text (WAV to text)
@app.post("/transcribe")
async def transcribe_endpoint(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    session_id: str = Header(None),
    session_cookie: str = Cookie(None)
):
    """Endpoint for speech-to-text (WAV/MP3 to text) with session management."""
    sid = get_or_create_session(session_id or session_cookie)
    response.headers["X-Session-ID"] = sid
    if not file:
        return JSONResponse(content={"error": "No file uploaded."}, status_code=400)
    result = transcribe.transcribe_audio(file)
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
    image: UploadFile = File(...),
    session_id: str = Header(None),
    session_cookie: str = Cookie(None)
):
    """Endpoint for generating avatar video from audio and image with session management."""
    sid = get_or_create_session(session_id or session_cookie)
    response.headers["X-Session-ID"] = sid
    if not audio or not image:
        return JSONResponse(content={"error": "Missing audio or image file."}, status_code=400)
    # Save files to temp locations
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio, \
         tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_image:
        try:
            shutil.copyfileobj(audio.file, tmp_audio)
            tmp_audio.flush()
            audio_path = tmp_audio.name
            # Accept both PNG and JPG
            ext = ".jpg" if image.content_type in ["image/jpeg", "image/jpg"] else ".png"
            tmp_image.close()
            with open(tmp_image.name, "wb") as img_out:
                shutil.copyfileobj(image.file, img_out)
            image_path = tmp_image.name
            # Generate video
            video_path, latency = avatar.generate_avatar(audio_path, image_path)
            headers = {"X-Latency": f"{latency}s", "X-Session-ID": sid}
            def iterfile():
                with open(video_path, "rb") as f:
                    yield from f
            response = StreamingResponse(iterfile(), media_type="video/mp4", headers=headers)
            return response
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
        finally:
            # Clean up temp files
            for path in [tmp_audio.name, tmp_image.name]:
                if path and os.path.exists(path):
                    os.remove(path)
            # Clean up video file if generated
            try:
                if 'video_path' in locals() and video_path and os.path.exists(video_path):
                    os.remove(video_path)
            except Exception:
                pass

# GET /status — returns { "status": "ok" }
@app.get("/status")
def status():
    """Health check endpoint."""
    return JSONResponse(content={"status": "ok"})

# For serverless: entrypoint is app (FastAPI instance) 