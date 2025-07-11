# Multi-stage Dockerfile for serverless FastAPI AI avatar backend
FROM python:3.10-slim AS base

# Install system dependencies for audio/video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies in a separate layer for caching
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy only necessary source files
COPY backend ./backend
COPY main.py ./

# Optionally copy scripts/ if needed for warmup or health checks
# COPY scripts ./scripts

# Expose port for local dev (not required for serverless)
EXPOSE 8000

# Set minimal entrypoint for serverless cold start optimization
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 