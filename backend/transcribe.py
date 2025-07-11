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

SUPPORTED_TYPES = {"audio/wav", "audio/x-wav", "audio/wave", "audio/mp3", "audio/mpeg", "audio/webm", "audio/webm;codecs=opus"}


def transcribe_audio(file: UploadFile) -> Dict:
    lazy_load_model()
    start_time = time.time()
    
    # Validate file type
    if file.content_type not in SUPPORTED_TYPES:
        return {"error": f"Unsupported file type: {file.content_type}"}
    
    # Check if file is empty
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size == 0:
        return {"error": "Audio file is empty"}
    
    if file_size < 100:  # Very small files are likely corrupted
        return {"error": "Audio file is too small or corrupted"}
    
    try:
        # Save uploaded file to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            # Convert to WAV if needed
            if file.content_type in ["audio/mp3", "audio/mpeg"]:
                audio = AudioSegment.from_file(file.file, format="mp3")
                audio.export(tmp.name, format="wav")
            elif file.content_type in ["audio/webm", "audio/webm;codecs=opus"]:
                audio = AudioSegment.from_file(file.file, format="webm")
                audio.export(tmp.name, format="wav")
            else:
                tmp.write(file.file.read())
                tmp.flush()
            tmp_path = tmp.name
            
        # Validate the temp file exists and has content
        if not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            return {"error": "Failed to save audio file"}
            
        # Transcribe with faster-whisper
        if model is None:
            return {"error": "Whisper model not loaded"}
        segments, info = model.transcribe(tmp_path, beam_size=1)
        transcript = "".join([seg.text for seg in segments])
        latency = round(time.time() - start_time, 2)
        
        # Clean up temp file
        try:
            os.remove(tmp_path)
        except:
            pass
            
        return {"transcript": transcript, "latency": latency}
    except Exception as e:
        # Clean up temp file on error
        try:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except:
            pass
        return {"error": f"Transcription failed: {str(e)}"} 