# backend/speak.py
# Text-to-speech with fallback to simple audio generation
import time
import os
import struct
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
        print("Loaded Bark TTS model")
    except ImportError:
        try:
            from TTS.api import TTS as CoquiTTS
            tts_model = CoquiTTS()
            print("Loaded Coqui TTS model")
        except ImportError:
            print("No TTS libraries found, using simple audio fallback")
            tts_model = None

def generate_simple_audio(text: str) -> bytes:
    """Generate a simple beep audio as fallback when TTS is not available."""
    # Create a simple WAV file with a beep sound
    sample_rate = 22050
    duration = 1.0  # 1 second
    frequency = 440  # A4 note
    
    # Generate sine wave
    num_samples = int(sample_rate * duration)
    audio_data = []
    for i in range(num_samples):
        sample = int(32767 * 0.3 * (i % 2))  # Simple square wave beep
        audio_data.append(sample)
    
    # WAV file header
    wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF',                    # Chunk ID
        36 + len(audio_data) * 2,   # Chunk size
        b'WAVE',                    # Format
        b'fmt ',                    # Subchunk1 ID
        16,                         # Subchunk1 size
        1,                          # Audio format (PCM)
        1,                          # Num channels
        sample_rate,                # Sample rate
        sample_rate * 2,            # Byte rate
        2,                          # Block align
        16,                         # Bits per sample
        b'data',                    # Subchunk2 ID
        len(audio_data) * 2         # Subchunk2 size
    )
    
    # Convert audio data to bytes
    audio_bytes = struct.pack(f'<{len(audio_data)}h', *audio_data)
    
    return wav_header + audio_bytes

def generate_speech(text: str) -> Tuple[bytes, float]:
    """
    Generate speech audio from text using Bark (preferred) or Coqui TTS (fallback).
    Falls back to simple beep if no TTS libraries are available.
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
            with open("output.wav", "rb") as f:
                wav_bytes = f.read()
        # Try Coqui TTS
        elif tts_model and hasattr(tts_model, 'tts_to_file'):
            tts_model.tts_to_file(text=text, file_path="output.wav")
            with open("output.wav", "rb") as f:
                wav_bytes = f.read()
        # Fallback to simple audio
        else:
            wav_bytes = generate_simple_audio(text)
        
        latency = round(time.time() - start_time, 2)
        return wav_bytes, latency
        
    except Exception as e:
        # If all else fails, return simple beep
        print(f"TTS generation failed: {str(e)}, using fallback")
        wav_bytes = generate_simple_audio(text)
        latency = round(time.time() - start_time, 2)
        return wav_bytes, latency 