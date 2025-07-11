import asyncio
import httpx
import uuid

API_URL = "http://localhost:8000"

async def transcribe(client, session_id):
    files = {'file': ('test.wav', b'RIFF....', 'audio/wav')}
    headers = {'session_id': session_id}
    # Replace b'RIFF....' with actual WAV bytes for real test
    resp = await client.post(f"{API_URL}/transcribe", files=files, headers=headers)
    print(f"/transcribe [{session_id}]:", resp.status_code, resp.json())

async def speak(client, session_id):
    json_data = {"text": "Hello, this is a test."}
    headers = {'session_id': session_id}
    resp = await client.post(f"{API_URL}/speak", json=json_data, headers=headers)
    print(f"/speak [{session_id}]:", resp.status_code, resp.headers.get('X-Latency'))

async def generate_avatar(client, session_id):
    files = {
        'audio': ('test.wav', b'RIFF....', 'audio/wav'),
        'image': ('test.png', b'\x89PNG....', 'image/png')
    }
    headers = {'session_id': session_id}
    # Replace b'RIFF....' and b'\x89PNG....' with real file bytes for real test
    resp = await client.post(f"{API_URL}/generate-avatar", files=files, headers=headers)
    print(f"/generate-avatar [{session_id}]:", resp.status_code, resp.headers.get('X-Latency'))

async def main():
    async with httpx.AsyncClient(timeout=60) as client:
        tasks = []
        for i in range(12):  # Simulate 12 concurrent users
            session_id = str(uuid.uuid4())
            tasks.append(transcribe(client, session_id))
            tasks.append(speak(client, session_id))
            tasks.append(generate_avatar(client, session_id))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main()) 