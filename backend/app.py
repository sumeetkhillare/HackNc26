import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import your scripts as modules
from video_extraction.video_data_extractor import download_and_extract
from video_extraction.clean_transcript import clean_vtt
from video_extraction.compacted_transcript import TranscriptSegmenter
from video_extraction.comment_analyzer import CommentAnalyzer
from video_extraction.utils import check_video_exists

app = Flask(__name__)
CORS(app)  # Allow requests from your future frontend

# Configuration
DOWNLOAD_FOLDER = "downloaded_content"
# Make sure your API Key is set here or in environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Server is running"}), 200


@app.route('/check_status', methods=['GET'])
def check_status():
    """
    Checks if a specific video ID or URL has already been processed.
    Example: /check_status?url=https://youtube.com/...
    """
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400
        
    exists, video_id = check_video_exists(video_url, DOWNLOAD_FOLDER)
    
    return jsonify({
        "video_id": video_id,
        "processed": exists,
        "folder_path": os.path.join(DOWNLOAD_FOLDER, video_id) if exists else None
    }), 200

@app.route('/extract_video_info', methods=['POST'])
def extract_video_info():
    """
    Main Pipeline:
    1. Download Video Data
    2. Clean Transcript
    3. Segment & Summarize Transcript (AI)
    4. Analyze Comments (AI)
    """
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    exists, video_id = check_video_exists(video_url, DOWNLOAD_FOLDER)
    if exists:
        return jsonify({
            "status": "success",
            "video_id": video_id,
            "message": "Video already processed. Loading from cache."
        }), 200

    print(f"--- Starting Pipeline for: {video_url} ---")
    


    ############################################## 1. RUN VIDEO EXTRACTOR
    try:
        # This calls your modified function that returns paths
        extraction_result = download_and_extract(video_url)
        
        if extraction_result.get("status") == "error":
            return jsonify({"error": extraction_result.get("message")}), 500
            
        video_id = extraction_result['video_id']
        folder_path = extraction_result['folder_path']
        vtt_path = extraction_result['vtt_file']
        metadata_path = extraction_result['metadata_file']
        
    except Exception as e:
        return jsonify({"error": f"Extraction failed: {str(e)}"}), 500

    ############################################## 2. RUN TRANSCRIPT CLEANER
    try:
        if os.path.exists(vtt_path):
            # The function now handles the saving internally and returns True/False
            success = clean_vtt(vtt_path)
            
            if success:
                print(f"Transcript cleaned and saved successfully.")
            else:
                print("Transcript cleaning failed.")
        else:
            print("No VTT file found, skipping cleaning.")
            
    except Exception as e:
        print(f"Warning: Transcript cleaning process threw an error: {e}")

    ############################################## 3. RUN COMPACTED TRANSCRIPT (AI SUMMARIZATION)
    # Define output path for the segments
    segmented_json_path = os.path.join(folder_path, f"{video_id}_segmented_summary.json")
    try:
        if os.path.exists(vtt_path):
            segmenter = TranscriptSegmenter(api_key=GEMINI_API_KEY)
            # This processes the file and saves the JSON to segmented_json_path
            segmenter.process_file(vtt_path, segmented_json_path)
        else:
            print("No VTT file found, skipping summarization.")
    except Exception as e:
        print(f"Warning: Summarization failed: {e}")

    # # 4. RUN COMMENT ANALYZER (AI)
    # # Define output path for analysis
    # analysis_json_path = os.path.join(folder_path, f"{video_id}_analysis.json")
    # try:
    #     analyzer = CommentAnalyzer(api_key=GEMINI_API_KEY)
    #     # We pass the metadata (comments) and the segmented transcript (context)
    #     # Note: If summarization failed/skipped, segmented_json_path might not exist.
    #     transcript_arg = segmented_json_path if os.path.exists(segmented_json_path) else None
        
    #     analyzer.run(metadata_path, transcript_path=transcript_arg, output_path=analysis_json_path)
    # except Exception as e:
    #     print(f"Warning: Comment analysis failed: {e}")

    return jsonify({
        "status": "success",
        "video_id": video_id,
        "message": "Data extracted successfully"
    }), 200


if __name__ == '__main__':
    # Run the server
    app.run(debug=True, port=5000)