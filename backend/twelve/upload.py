"""
TwelveLabs Video Upload Script
Reads video_extract.json, uploads video, adds video_id and task_id to it
"""

import requests
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIGURATION ==========
API_KEY = os.getenv("TWELVELABS_API_KEY")
INDEX_ID = os.getenv("TWELVELABS_INDEX_ID")
BASE_URL = "https://api.twelvelabs.io/v1.3"

# ========== VALIDATION ==========
if not API_KEY:
    print(" Error: TWELVELABS_API_KEY not found in .env file!")
    exit(1)

if not INDEX_ID:
    print(" Error: TWELVELABS_INDEX_ID not found in .env file!")
    exit(1)

# ========== LOAD VIDEO EXTRACT DATA ==========
if not os.path.exists('video_extract.json'):
    print(" Error: video_extract.json not found!")
    print("Please run extract_store.py first.")
    exit(1)

print(" Loading video extract data...")
with open('video_extract.json', 'r', encoding='utf-8') as f:
    video_extract = json.load(f)

# Get video file path from video_info.json
if not os.path.exists('video_info.json'):
    print(" Error: video_info.json not found!")
    exit(1)

with open('video_info.json', 'r') as f:
    video_info = json.load(f)

VIDEO_FILE_PATH = video_info.get('video_file')

if not os.path.exists(VIDEO_FILE_PATH):
    print(f" Error: Video file not found: {VIDEO_FILE_PATH}")
    exit(1)

print(f"Video file: {VIDEO_FILE_PATH}")
print(f"Index ID: {INDEX_ID}")

# ========== STEP 1: UPLOAD VIDEO ==========
print("\n Uploading video...")

upload_url = f"{BASE_URL}/tasks"
headers = {"x-api-key": API_KEY}

with open(VIDEO_FILE_PATH, 'rb') as video_file:
    files = {'video_file': video_file}
    data = {'index_id': INDEX_ID}
    
    response = requests.post(upload_url, headers=headers, files=files, data=data)

if response.status_code not in [200, 201]:
    print(f" Upload failed: {response.status_code}")
    print(response.text)
    exit(1)

upload_result = response.json()
task_id = upload_result.get('_id')
video_id = upload_result.get('video_id')

print(f"Upload started!")
print(f"   Task ID: {task_id}")
print(f"   Video ID: {video_id}")

# ========== STEP 2: WAIT FOR INDEXING ==========
print("\n Waiting for indexing to complete...")

task_url = f"{BASE_URL}/tasks/{task_id}"

while True:
    response = requests.get(task_url, headers=headers)
    task_data = response.json()
    status = task_data.get('status')
    
    print(f"   Status: {status}")
    
    if status == 'ready':
        print(" Indexing complete!")
        break
    elif status == 'failed':
        print(f" Indexing failed: {task_data.get('error_message')}")
        exit(1)
    
    time.sleep(5)

# ========== STEP 3: UPDATE video_extract.json ==========
print("\n Updating video_extract.json with upload data...")

# Add new fields to existing data
video_extract['video_id'] = video_id
video_extract['task_id'] = task_id
video_extract['index_id'] = INDEX_ID
video_extract['status'] = 'ready'

# Save back to video_extract.json
with open('video_extract.json', 'w', encoding='utf-8') as f:
    json.dump(video_extract, f, indent=2, ensure_ascii=False)

print(f" video_extract.json updated with video_id and task_id")
print(f"\n Done! Video ID: {video_id}")
print(f" You can now run analyze.py")