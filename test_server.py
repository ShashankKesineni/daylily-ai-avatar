from fastapi import FastAPI, UploadFile, File, Header
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/test-avatar")
async def test_avatar(
    audio: UploadFile = File(...),
    session_id: str = Header(None)
):
    """Simple test endpoint for avatar generation."""
    return JSONResponse({
        "message": "Test endpoint working",
        "audio_filename": audio.filename,
        "session_id": session_id
    })

@app.get("/test")
def test():
    return JSONResponse({"message": "Test endpoint"}) 