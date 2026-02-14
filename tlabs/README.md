# TwelveLabs Video Upload & Analysis

Simple Python script to upload and analyze videos using TwelveLabs REST API.

## Setup

### 1. Install Dependencies

```bash
pip install requests python-dotenv
```

### 2. Set Environment Variables

#### Option A: Export in Terminal (Quick)

```bash
export TWELVELABS_API_KEY="tlk_2KTCT0X34QGJ6124GJC2V0EEQ8NA"
export TWELVELABS_INDEX_ID="6990df3a32be0dd2da150e36"
export VIDEO_FILE_PATH="./video.mp4"
```

#### Option B: Use .env File (Recommended)

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
TWELVELABS_API_KEY=tlk_2KTCT0X34QGJ6124GJC2V0EEQ8NA
TWELVELABS_INDEX_ID=6990df3a32be0dd2da150e36
VIDEO_FILE_PATH=./video.mp4
```

Then use the dotenv version:

```bash
python simple_rest_api_dotenv.py
```

## Usage

### Quick Run (with exports)

```bash
export TWELVELABS_API_KEY="your-key"
export TWELVELABS_INDEX_ID="your-index-id"
python simple_rest_api_env.py
```

### With Custom Video

```bash
export TWELVELABS_API_KEY="your-key"
export TWELVELABS_INDEX_ID="your-index-id"
export VIDEO_FILE_PATH="/path/to/your/video.mp4"
python simple_rest_api_env.py
```

### One-liner

```bash
TWELVELABS_API_KEY="your-key" TWELVELABS_INDEX_ID="your-index-id" python simple_rest_api_env.py
```

## What It Does

1. ⬆️  Uploads video to TwelveLabs
2. ⏳ Waits for indexing (checks every 5 seconds)
3. 🔍 Analyzes video with custom prompt
4. 📝 Prints summary

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TWELVELABS_API_KEY` | ✅ Yes | - | Your TwelveLabs API key |
| `TWELVELABS_INDEX_ID` | No | `6990df3a32be0dd2da150e36` | Target index ID |
| `VIDEO_FILE_PATH` | No | `./video.mp4` | Path to video file |

## Example Output

```
📁 Video file: ./video.mp4
📊 Index ID: 6990df3a32be0dd2da150e36

⬆️  Uploading video...
✅ Upload started!
   Task ID: 67890abcdef
   Video ID: 12345xyz

⏳ Waiting for indexing to complete...
   Status: validating
   Status: pending
   Status: indexing
   Status: ready
✅ Indexing complete!

🔍 Analyzing video...

📝 Summary:
This video shows...

🎉 Done! Video ID: 12345xyz
```

## Troubleshooting

### "API_KEY environment variable not set"

Make sure you've exported the variable:

```bash
export TWELVELABS_API_KEY="your-key"
```

Or check your .env file exists and has the correct format.

### "Video file not found"

Check the path:

```bash
ls -lh ./video.mp4
```

Or set the full path:

```bash
export VIDEO_FILE_PATH="/full/path/to/video.mp4"
```

### "Upload failed: 400"

Your video might not meet requirements:
- Duration: 4 seconds to 2 hours
- Size: Up to 2 GB
- Format: MP4, MOV, etc.
- Resolution: 360x360 to 3840x2160