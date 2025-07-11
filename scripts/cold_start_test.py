import httpx
import time
import os
import statistics
import json

# Configurable parameters
API_URL = os.getenv("COLD_START_URL", "https://your-serverless-endpoint.com/warmup")
NUM_RUNS = int(os.getenv("COLD_START_RUNS", 10))
OUTPUT_JSON = os.getenv("COLD_START_JSON", "cold_start_results.json")

# Optionally, add a delay between runs to allow the serverless platform to scale to zero
COLD_DELAY = int(os.getenv("COLD_START_DELAY", 120))  # seconds

results = []

print(f"Testing cold start latency for {NUM_RUNS} runs at {API_URL}...")

for i in range(NUM_RUNS):
    print(f"Run {i+1}/{NUM_RUNS}...")
    # Wait for cold start (simulate scale-to-zero)
    if i > 0:
        print(f"Waiting {COLD_DELAY}s for cold start...")
        time.sleep(COLD_DELAY)
    start = time.perf_counter()
    try:
        resp = httpx.post(API_URL, timeout=120)
        latency = time.perf_counter() - start
        print(f"  Status: {resp.status_code}, Latency: {latency:.2f}s")
        results.append(latency)
    except Exception as e:
        print(f"  Error: {e}")
        results.append(None)

# Filter out failed runs
latencies = [r for r in results if r is not None]

print("\n--- Cold Start Latency Report ---")
if latencies:
    print(f"Average: {statistics.mean(latencies):.2f}s")
    print(f"Median: {statistics.median(latencies):.2f}s")
    print(f"Max: {max(latencies):.2f}s")
    print(f"Min: {min(latencies):.2f}s")
else:
    print("No successful runs.")

with open(OUTPUT_JSON, 'w') as f:
    json.dump({"latencies": latencies, "all_results": results}, f, indent=2)
print(f"Results saved to {OUTPUT_JSON}") 