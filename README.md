# Daylily AI Avatar Diffusion Challenge

## Project Overview
This project is a real-time, serverless-ready, diffusion-based talking head avatar system.

## Current Status
- End-to-end demo flow is working with placeholder video.
- Awaiting DreamTalk checkpoints for real generative video.

## How to Run
1. Create and activate the Python virtual environment.
2. Install dependencies: pip install -r requirements.txt
3. Start backend: source .venv/bin/activate && uvicorn main:app --reload
4. Start frontend: cd frontend && python3 -m http.server 8080
5. Open http://localhost:8080 in your browser.

## Demo Mode
- The avatar video is a placeholder until DreamTalk is integrated.
- All other features (STT, TTS, API, UI) are fully functional.

## Next Steps
- Integrate DreamTalk as soon as checkpoints are available.
- Update backend to generate real videos.

## Rubric Checklist
- [x] Real-time backend/frontend integration
- [x] Serverless-ready architecture
- [x] Speech-to-text and text-to-speech
- [x] Placeholder video for demo
- [ ] Generative diffusion model (pending DreamTalk)
- [x] Documentation and usage guide
- [ ] Final performance/latency benchmarks (after DreamTalk)

