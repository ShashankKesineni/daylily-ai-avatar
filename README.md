# FastAPI AI Avatar Backend

## Cold Start Optimization Strategies

- **Minimal Container Size:**
  - Uses `python:3.10-slim` and multi-stage Dockerfile.
  - Installs only required system and Python dependencies.
- **Lazy Model Loading:**
  - Heavy ML models (Whisper, Bark/Coqui TTS, SadTalker) are loaded only on first request.
  - Reduces cold start time and memory usage.
- **Warm-up Endpoint:**
  - `POST /warmup` endpoint pre-loads all models for cold start mitigation.
  - Can be called by serverless platform health checks or deployment scripts.
- **Optimized Dockerfile:**
  - Multi-stage, minimal layers, only necessary files copied.
  - Fast startup and small image size.
- **Entry-level GPU Compatibility:**
  - Models use CPU or low-VRAM settings by default.

## Serverless Deployment Instructions

### AWS Lambda (Container)
- Build and push Docker image to ECR:
  ```sh
  docker build -t avatar-backend .
  # Tag and push to your ECR repo
  ```
- Use AWS Lambda console or AWS SAM to deploy the container.
- Example `template.yaml` for AWS SAM:
  ```yaml
  AWSTemplateFormatVersion: '2010-09-09'
  Transform: AWS::Serverless-2016-10-31
  Resources:
    AvatarApi:
      Type: AWS::Serverless::Function
      Properties:
        PackageType: Image
        ImageUri: <your-ecr-image-uri>
        MemorySize: 4096
        Timeout: 900
        Environment:
          Variables:
            LOG_LEVEL: INFO
  ```

### Google Cloud Run
- Build and deploy:
  ```sh
  gcloud builds submit --tag gcr.io/<project-id>/avatar-backend
  gcloud run deploy avatar-backend --image gcr.io/<project-id>/avatar-backend --platform managed --memory 4Gi --timeout 900
  ```
- Example `cloudrun.yaml`:
  ```yaml
  apiVersion: serving.knative.dev/v1
  kind: Service
  metadata:
    name: avatar-backend
  spec:
    template:
      spec:
        containers:
        - image: gcr.io/<project-id>/avatar-backend
          resources:
            limits:
              memory: 4Gi
          env:
          - name: LOG_LEVEL
            value: INFO
        timeoutSeconds: 900
  ```

## Measuring Cold Start Latency
- Use `scripts/cold_start_test.py` to measure cold start times.
- Configure `COLD_START_URL` to your deployed `/warmup` endpoint.
- The script will invoke the endpoint multiple times, simulating cold starts and reporting latency statistics.

## Warm-up Endpoint Usage
- `POST /warmup` can be called after deployment to pre-load all models and reduce first-request latency.

## Notes
- For best results, use the smallest model variants and CPU/low-VRAM settings in serverless environments.
- For GPU support, ensure your serverless platform provides a compatible GPU and adjust model loading accordingly. 