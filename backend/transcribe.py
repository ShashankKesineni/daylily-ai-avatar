# backend/transcribe.py
# Placeholder for speech-to-text (WAV to text) logic 
from fastapi import UploadFile
from typing import Dict
import time
from faster_whisper import WhisperModel
from pydub import AudioSegment
import tempfile
import os

model = None

def lazy_load_model():
    global model
    if model is None:
        # Load the Whisper model (tiny for speed/VRAM)
        model = WhisperModel("tiny", device="cpu", compute_type="int8")

SUPPORTED_TYPES = {"audio/wav", "audio/x-wav", "audio/wave", "audio/mp3", "audio/mpeg"}


def transcribe_audio(file: UploadFile) -> Dict:
    lazy_load_model()
    start_time = time.time()
    if file.content_type not in SUPPORTED_TYPES:
        return {"error": f"Unsupported file type: {file.content_type}"}
    try:
        # Save uploaded file to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            # Convert to WAV if needed
            if file.content_type in ["audio/mp3", "audio/mpeg"]:
                audio = AudioSegment.from_file(file.file, format="mp3")
                audio.export(tmp.name, format="wav")
            else:
                tmp.write(file.file.read())
                tmp.flush()
            tmp_path = tmp.name
        # Transcribe with faster-whisper
        segments, info = model.transcribe(tmp_path, beam_size=1)
        transcript = "".join([seg.text for seg in segments])
        latency = round(time.time() - start_time, 2)
        os.remove(tmp_path)
        return {"transcript": transcript, "latency": latency}
    except Exception as e:
        return {"error": f"Transcription failed: {str(e)}"} 