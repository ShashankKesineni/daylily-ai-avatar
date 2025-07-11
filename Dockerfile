# Minimal Dockerfile for serverless FastAPI deployment
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port (optional for serverless, but useful for local dev)
EXPOSE 8000

# Entrypoint for serverless: uvicorn main:app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 