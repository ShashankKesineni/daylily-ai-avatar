# backend/speak.py
# Placeholder for text-to-speech (text to WAV) logic 
import time
import os
from typing import Tuple

def generate_speech(text: str) -> Tuple[bytes, float]:
    """
    Generate speech audio from text using Bark (preferred) or Coqui TTS (fallback).
    Saves output to output.wav and returns (WAV bytes, latency).
    """
    if not text or not text.strip():
        raise ValueError("Text input is empty.")
    start_time = time.time()
    try:
        # Try Bark first
        try:
            from bark import SAMPLE_RATE, generate_audio
            from scipy.io.wavfile import write as write_wav
            audio_array = generate_audio(text)
            write_wav("output.wav", SAMPLE_RATE, audio_array)
        except ImportError:
            # Fallback to Coqui TTS
            from TTS.api import TTS as CoquiTTS
            tts = CoquiTTS()
            tts.tts_to_file(text=text, file_path="output.wav")
        # Read the WAV file as bytes
        with open("output.wav", "rb") as f:
            wav_bytes = f.read()
        latency = round(time.time() - start_time, 2)
        return wav_bytes, latency
    except Exception as e:
        raise RuntimeError(f"TTS generation failed: {str(e)}") 