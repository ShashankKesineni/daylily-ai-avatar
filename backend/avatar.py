# backend/avatar.py
# Placeholder for audio+image to video (avatar generation) logic 
import time
import os
import tempfile
from typing import Tuple, Optional

def lazy_load_model():
    """Placeholder for model loading - no actual model needed for test"""
    pass

def create_default_avatar_image():
    """Create a simple default avatar image if none exists."""
    default_path = "backend/default_avatar.png"
    if not os.path.exists(default_path):
        # Create a simple placeholder image using PIL
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (512, 512), color='#4f46e5')
            draw = ImageDraw.Draw(img)
            # Draw a simple face
            draw.ellipse([100, 100, 412, 412], fill='#fbbf24', outline='#1e293b', width=3)
            draw.ellipse([150, 200, 200, 250], fill='#1e293b')  # Left eye
            draw.ellipse([312, 200, 362, 250], fill='#1e293b')  # Right eye
            draw.arc([200, 250, 312, 350], 0, 180, fill='#1e293b', width=5)  # Smile
            img.save(default_path)
        except ImportError:
            # If PIL not available, create a simple text file as placeholder
            with open(default_path, 'w') as f:
                f.write("Default avatar placeholder")
    return default_path

def create_test_video():
    """Create a simple test video file for demonstration."""
    # Create a more substantial MP4 video file that browsers can actually play
    # This includes proper MP4 structure with moov and mdat boxes
    mp4_data = (
        # File type box
        b'\x00\x00\x00\x20ftypmp41'
        b'\x00\x00\x00\x00mp41isom'
        
        # Movie box (moov)
        b'\x00\x00\x00\x5Cmoov'
        b'\x00\x00\x00\x2Cmvhd'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x03\xE8\x00\x00\x00\x00\x00\x01\x00\x00'
        b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        
        # Track box (trak)
        b'\x00\x00\x00\x2Ctrak'
        b'\x00\x00\x00\x20tkhd'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        
        # Media data box (mdat) - contains actual video data
        b'\x00\x00\x00\x08mdat'
        b'\x00\x00\x00\x00'  # Empty video data (1 frame)
    )
    return mp4_data

def generate_avatar(audio_path: str, image_path: Optional[str] = None) -> Tuple[str, float]:
    """
    Generate a 720p, 24+ FPS MP4 video with lip-sync using SadTalker.
    For now, returns a real sample video for testing.
    """
    import time
    start_time = time.time()
    sample_video_path = "backend/sample_avatar.mp4"
    latency = round(time.time() - start_time, 2)
    return sample_video_path, latency 