# Daylily AI Avatar Frontend

A real-time, serverless-ready frontend for the Daylily AI Avatar Diffusion Challenge.

## Features
- Real-time chat with text and voice input
- Avatar video response (720p+)
- End-to-end latency display
- Session management (10+ concurrent users)
- Error handling and user-friendly UI
- Mobile-friendly, modern design
- Easy integration with any FastAPI backend

## Setup
1. Place this folder (`frontend/`) in your project root.
2. Start a static server:
   ```sh
   cd frontend
   python3 -m http.server 8080
   # or use Vercel, Netlify, S3, etc.
   ```
3. Open [http://localhost:8080](http://localhost:8080) in your browser.
4. Ensure your backend is running at `http://localhost:8000` (or update `app.js` with your backend URL).

## Deployment
- Deploy as static files to Vercel, Netlify, S3, CloudFront, or any static host.
- No build step required.

## Integration
- The frontend expects the following backend endpoints:
  - `POST /transcribe` (multipart audio → transcript)
  - `POST /speak` (JSON text → WAV audio)
  - `POST /generate-avatar` (multipart audio/image → MP4 video)
  - `GET /status` (health check)
- All requests include a `session_id` query param for concurrency.

## Customization
- Update branding in `index.html` and `app.css`.
- Replace `assets/logo.png` and `assets/avatar-placeholder.png` as needed.

## License
MIT 