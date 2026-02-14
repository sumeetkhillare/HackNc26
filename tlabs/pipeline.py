"""
Simple TwelveLabs Upload & Analyze Script
Using REST API with requests library
Reads API key from environment variable
"""

import requests
import time
import json
import os
from pathlib import Path

# ========== CONFIGURATION ==========
API_KEY = os.getenv("TWELVELABS_API_KEY")
INDEX_ID = os.getenv("TWELVELABS_INDEX_ID", "6990df3a32be0dd2da150e36")
VIDEO_FILE_PATH = os.getenv("VIDEO_FILE_PATH", "./video.mp4")

BASE_URL = "https://api.twelvelabs.io/v1.3"

# ========== VALIDATION ==========
if not API_KEY:
    print("❌ Error: TWELVELABS_API_KEY environment variable not set!")
    print("\nSet it with:")
    print("  export TWELVELABS_API_KEY='your-api-key-here'")
    exit(1)

if not os.path.exists(VIDEO_FILE_PATH):
    print(f"❌ Error: Video file not found: {VIDEO_FILE_PATH}")
    exit(1)

print(f"📁 Video file: {VIDEO_FILE_PATH}")
print(f"📊 Index ID: {INDEX_ID}")

# ========== STEP 1: UPLOAD VIDEO ==========
print("\n⬆️  Uploading video...")

upload_url = f"{BASE_URL}/tasks"
headers = {"x-api-key": API_KEY}

with open(VIDEO_FILE_PATH, 'rb') as video_file:
    files = {'video_file': video_file}
    data = {'index_id': INDEX_ID}
    
    response = requests.post(upload_url, headers=headers, files=files, data=data)

if response.status_code not in [200, 201]:
    print(f"❌ Upload failed: {response.status_code}")
    print(response.text)
    exit(1)

upload_result = response.json()
task_id = upload_result.get('_id')
video_id = upload_result.get('video_id')

print(f"✅ Upload started!")
print(f"   Task ID: {task_id}")
print(f"   Video ID: {video_id}")

# ========== STEP 2: WAIT FOR INDEXING ==========
print("\n⏳ Waiting for indexing to complete...")

task_url = f"{BASE_URL}/tasks/{task_id}"

while True:
    response = requests.get(task_url, headers=headers)
    task_data = response.json()
    status = task_data.get('status')
    
    print(f"   Status: {status}")
    
    if status == 'ready':
        print("✅ Indexing complete!")
        break
    elif status == 'failed':
        print(f"❌ Indexing failed: {task_data.get('error_message')}")
        exit(1)
    
    time.sleep(5)

# ========== STEP 3: ANALYZE VIDEO ==========
print("\n🔍 Analyzing video...")

analyze_url = f"{BASE_URL}/analyze"
analyze_headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}
analyze_data = {
    "video_id": video_id,
    "prompt": "Give me summary of the video",
    "temperature": 0.7,
    "stream": False
}

response = requests.post(analyze_url, headers=analyze_headers, json=analyze_data)

if response.status_code != 200:
    print(f"❌ Analysis failed: {response.status_code}")
    print(response.text)
    exit(1)

result = response.json()
summary = result.get('data')

print(f"\n📝 Summary:")
print(summary)

print(f"\n🎉 Done! Video ID: {video_id}")