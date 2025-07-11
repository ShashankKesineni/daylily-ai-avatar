import asyncio
import httpx
import uuid
import time
import json
import csv
import os
from statistics import mean, median, quantiles
from typing import List, Dict
import psutil
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# Configurable parameters
API_URL = os.getenv("BENCH_API_URL", "http://localhost:8000")
CONCURRENCY = int(os.getenv("BENCH_CONCURRENCY", 10))
NUM_REQUESTS = int(os.getenv("BENCH_NUM_REQUESTS", 20))
AUDIO_PATH = os.getenv("BENCH_AUDIO", "test.wav")
IMAGE_PATH = os.getenv("BENCH_IMAGE", "test.png")
OUTPUT_CSV = os.getenv("BENCH_CSV", "benchmark_results.csv")
OUTPUT_JSON = os.getenv("BENCH_JSON", "benchmark_results.json")

# Helper to read binary files
with open(AUDIO_PATH, "rb") as f:
    AUDIO_BYTES = f.read()
with open(IMAGE_PATH, "rb") as f:
    IMAGE_BYTES = f.read()

async def get_memory_gpu_usage():
    mem = psutil.virtual_memory()
    mem_used = mem.used / (1024 ** 2)  # MB
    gpu_used = 0
    if GPU_AVAILABLE:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_used = max([gpu.memoryUsed for gpu in gpus])  # MB
    return mem_used, gpu_used

async def benchmark_user(client, user_id, results: List[Dict]):
    timings = {}
    session_id = str(uuid.uuid4())
    # 1. /transcribe
    start = time.perf_counter()
    mem_before, gpu_before = await get_memory_gpu_usage()
    files = {'file': (AUDIO_PATH, AUDIO_BYTES, 'audio/wav')}
    resp = await client.post(f"{API_URL}/transcribe", files=files, headers={"session_id": session_id})
    timings['transcribe_latency'] = resp.json().get('latency', -1)
    timings['transcribe_status'] = resp.status_code
    timings['transcribe_time'] = time.perf_counter() - start
    mem_after, gpu_after = await get_memory_gpu_usage()
    timings['mem_transcribe'] = mem_after - mem_before
    timings['gpu_transcribe'] = gpu_after - gpu_before
    # 2. /speak
    start = time.perf_counter()
    mem_before, gpu_before = await get_memory_gpu_usage()
    text = resp.json().get('transcript', 'Hello!')
    resp2 = await client.post(f"{API_URL}/speak", json={"text": text}, headers={"session_id": session_id})
    timings['speak_latency'] = float(resp2.headers.get('X-Latency', -1))
    timings['speak_status'] = resp2.status_code
    timings['speak_time'] = time.perf_counter() - start
    mem_after, gpu_after = await get_memory_gpu_usage()
    timings['mem_speak'] = mem_after - mem_before
    timings['gpu_speak'] = gpu_after - gpu_before
    # 3. /generate-avatar
    start = time.perf_counter()
    mem_before, gpu_before = await get_memory_gpu_usage()
    files = {
        'audio': (AUDIO_PATH, AUDIO_BYTES, 'audio/wav'),
        'image': (IMAGE_PATH, IMAGE_BYTES, 'image/png')
    }
    resp3 = await client.post(f"{API_URL}/generate-avatar", files=files, headers={"session_id": session_id})
    timings['avatar_latency'] = float(resp3.headers.get('X-Latency', -1))
    timings['avatar_status'] = resp3.status_code
    timings['avatar_time'] = time.perf_counter() - start
    mem_after, gpu_after = await get_memory_gpu_usage()
    timings['mem_avatar'] = mem_after - mem_before
    timings['gpu_avatar'] = gpu_after - gpu_before
    # Total time
    timings['total_time'] = timings['transcribe_time'] + timings['speak_time'] + timings['avatar_time']
    timings['user_id'] = user_id
    results.append(timings)
    print(f"User {user_id} done: {timings}")

async def main():
    results = []
    async with httpx.AsyncClient(timeout=120) as client:
        tasks = [benchmark_user(client, i, results) for i in range(NUM_REQUESTS)]
        await asyncio.gather(*tasks)
    # Output summary
    print("\n--- Benchmark Summary ---")
    for step in ['transcribe_time', 'speak_time', 'avatar_time', 'total_time']:
        times = [r[step] for r in results if r[step] >= 0]
        if times:
            print(f"{step}: avg={mean(times):.2f}s, p50={median(times):.2f}s, p95={quantiles(times, n=100)[94]:.2f}s, max={max(times):.2f}s")
    # Save to CSV
    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    # Save to JSON
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {OUTPUT_CSV} and {OUTPUT_JSON}")

if __name__ == "__main__":
    print(f"Benchmarking {NUM_REQUESTS} requests with concurrency {CONCURRENCY}...")
    asyncio.run(main()) 