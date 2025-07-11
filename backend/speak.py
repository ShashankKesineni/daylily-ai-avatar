# backend/speak.py
# Placeholder for text-to-speech (text to WAV) logic 
import time
import os
from typing import Tuple

tts_model = None
bark_write_wav = None
bark_sample_rate = None

def lazy_load_model():
    global tts_model, bark_write_wav, bark_sample_rate
    if tts_model is not None or bark_write_wav is not None:
        return
    try:
        from bark import SAMPLE_RATE, generate_audio
        from scipy.io.wavfile import write as write_wav
        bark_write_wav = write_wav
        bark_sample_rate = SAMPLE_RATE
        tts_model = generate_audio
    except ImportError:
        from TTS.api import TTS as CoquiTTS
        tts_model = CoquiTTS()

def generate_speech(text: str) -> Tuple[bytes, float]:
    """
    Generate speech audio from text using Bark (preferred) or Coqui TTS (fallback).
    Saves output to output.wav and returns (WAV bytes, latency).
    """
    lazy_load_model()
    if not text or not text.strip():
        raise ValueError("Text input is empty.")
    start_time = time.time()
    try:
        # Try Bark first
        if bark_write_wav and bark_sample_rate and callable(tts_model):
            audio_array = tts_model(text)
            bark_write_wav("output.wav", bark_sample_rate, audio_array)
        else:
            tts_model.tts_to_file(text=text, file_path="output.wav")
        # Read the WAV file as bytes
        with open("output.wav", "rb") as f:
            wav_bytes = f.read()
        latency = round(time.time() - start_time, 2)
        return wav_bytes, latency
    except Exception as e:
        raise RuntimeError(f"TTS generation failed: {str(e)}") 