# backend/avatar.py
# Placeholder for audio+image to video (avatar generation) logic 
import time
import os
import tempfile
from typing import Tuple

sadtalker_model = None

def lazy_load_model():
    global sadtalker_model
    if sadtalker_model is None:
        from sadtalker import SadTalker
        sadtalker_model = SadTalker()

def generate_avatar(audio_path: str, image_path: str) -> Tuple[str, float]:
    """
    Generate a 720p, 24+ FPS MP4 video with lip-sync using SadTalker.
    Returns the path to the generated video file.
    """
    lazy_load_model()
    start_time = time.time()
    video_path = None
    try:
        # Create a temp file for the output video
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
            video_path = tmp_video.name
        # Use sadtalker_model
        sadtalker_model.generate(
            audio_path=audio_path,
            image_path=image_path,
            output_path=video_path,
            size=720,
            fps=24
        )
        latency = round(time.time() - start_time, 2)
        return video_path, latency
    except Exception as e:
        # Clean up temp video if created
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
        raise RuntimeError(f"Avatar generation failed: {str(e)}") 