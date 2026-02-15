import os
import json
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import your scripts as modules
from video_extraction.video_data_extractor import download_and_extract
from video_extraction.clean_transcript import clean_vtt
from video_extraction.compacted_transcript import TranscriptSegmenter
from video_extraction.comment_analyzer import CommentAnalyzer
from video_extraction.utils.check_video_exits import check_video_exists
from video_extraction.utils.check_comment_analysis_exists import check_analysis_exists
from valkey_rest.crud import valkey_get, valkey_set, valkey_delete, valkey_exists
from video_extraction.fact_checker import FactChecker


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

    # 1. RUN VIDEO EXTRACTOR
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

    # 2. RUN TRANSCRIPT CLEANER
    try:
        if vtt_path and os.path.exists(vtt_path):
            # The function now handles the saving internally and returns True/False
            success = clean_vtt(vtt_path, video_id)

            if success:
                print(f"Transcript cleaned and saved successfully.")
            else:
                print("Transcript cleaning failed.")
        else:
            print("No VTT file found, skipping cleaning.")

    except Exception as e:
        print(f"Warning: Transcript cleaning process threw an error: {e}")

    # 3. RUN COMPACTED TRANSCRIPT (AI SUMMARIZATION)
    # Define output path for the segments
    segmented_json_path = os.path.join(
        folder_path, f"{video_id}_segmented_summary.json")
    try:
        if vtt_path and os.path.exists(vtt_path):
            segmenter = TranscriptSegmenter(api_key=GEMINI_API_KEY)
            # This processes the file and saves the JSON to segmented_json_path
            segmenter.process_file(
                vtt_path, segmented_json_path, video_id=video_id)
        else:
            print("No VTT file found, skipping summarization.")
    except Exception as e:
        print(f"Warning: Summarization failed: {e}")

    return jsonify({
        "status": "success",
        "video_id": video_id,
        "message": "Data extracted successfully"
    }), 200


@app.route('/analyze/quality', methods=['POST'])
def analyze_twelve_labs():
    """
    Calls the Twelve Labs pipeline using flow.py
    Usage: Send a POST request to /analyze_twelve_labs
    """
    # 1. Define paths relative to the backend folder
    twelve_folder = os.path.join(os.getcwd(), "twelve")
    flow_script = os.path.join(twelve_folder, "flow.py")
    result_json_path = os.path.join(twelve_folder, "result.json")

    data = request.json
    db_id = data.get('video_id')

    valkey_key = f"{db_id}_twelve_analysis.json"

    # 3. Use the existing 'get' function from your teammate's crud.py
    # If it returns None, the key does not exist
    # exists = valkey_exists(valkey_key) is not None
    cached_result = valkey_get(valkey_key)

    if cached_result is not None:
        print(f"Returning cached analysis for {db_id}")
        # cached_result = valkey_get(valkey_key)
        try:
            return jsonify(cached_result), 200
        except json.JSONDecodeError:
            return jsonify({"error": "Cached analysis is corrupted"}), 500

    print(f"--- Starting Twelve Labs Pipeline ---")

    try:

        log_path = os.path.join(twelve_folder, "pipeline_debug.log")

        with open(log_path, "w") as log_file:
            process = subprocess.run(
                ["python", "flow.py", "--all"],
                cwd=twelve_folder,
                stdout=log_file,   # Sends normal prints to the file
                stderr=log_file,   # Sends errors/tracebacks to the file
                text=True,
                check=True
            )
        print(f"✅ Check {log_path} for full debug details.")
        # 2. Execute the flow.py script
        # Using cwd=twelve_folder ensures flow.py can find its local files (upload.py, etc.)
        # process = subprocess.run(
        #     ["python", "flow.py", "--all"],
        #     cwd=twelve_folder,
        #     capture_output=True,
        #     text=True,
        #     check=True
        # )

        print("✅ Pipeline execution successful")

        # 3. Read and return the result.json
        if os.path.exists(result_json_path):
            with open(result_json_path, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
                return jsonify(analysis_data), 200
        else:
            return jsonify({"error": "result.json not found after analysis"}), 500

    except subprocess.CalledProcessError as e:
        print(f"❌ Pipeline failed: {e.stderr}")
        return jsonify({
            "error": "Twelve Labs pipeline failed",
            "details": e.stderr
        }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/analyze_comments', methods=['POST'])
def analyze_comments():
    data = request.json
    video_id = data.get('video_id')

    if not video_id:
        return jsonify({"error": "No video_id provided"}), 400

    # 1. Define Paths
    folder_path = os.path.join(DOWNLOAD_FOLDER, video_id)
    metadata_path = os.path.join(folder_path, f"{video_id}_summary.json")
    # vtt_summary_path = os.path.join(
    #     folder_path, f"{video_id}_segmented_summary.json")
    # print(folder_path, metadata_path, vtt_summary_path)

    # 2. Check if analysis already exists
    exists, analysis_path = check_analysis_exists(video_id, DOWNLOAD_FOLDER)

    if exists:
        print(f"Returning cached analysis for {video_id}")
        return jsonify(valkey_get(f"{video_id}_analysis.json")), 200

    # 3. Run Analysis if not found
    try:
        # print("BEFORE GET - Checking Valkey for existing analysis...")
        summary_get = valkey_get(video_id + "_summary.json")
        # print("AFTER GET - Valkey response:", "Found summary" if summary_get else "No summary found")
        if summary_get is None:
            return jsonify({"error": f"Video metadata not found in Valkey. Run extraction first."}), 404

        analyzer = CommentAnalyzer(api_key=GEMINI_API_KEY)

        # Check if we have transcript context to make analysis "Context-Aware"
        # transcript_arg = vtt_summary_path if os.path.exists(
        #     vtt_summary_path) else None

        # Run process (saves to analysis_path internally)
        # analyzer.run(metadata_path, transcript_path=transcript_arg,
        #              output_path=analysis_path)
        analyzer.run(video_id,
                     output_path=analysis_path, input_path=metadata_path)

        # Load and return the newly created file
        with open(analysis_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f)), 200

    except Exception as e:
        return jsonify({"error": f"Comment analysis failed: {str(e)}"}), 500


@app.route("/ping", methods=["GET"])
def ping_route():
    return jsonify({"status": "ok", "valkey": ping()})


@app.route("/get/<key>", methods=["GET"])
def get_route(key):
    """
        Sample usage:
        curl http://localhost:5000/get/key1      
    """
    value = valkey_get(key)
    if value is None:
        return jsonify({"error": "Key not found"}), 404
    return jsonify({"key": key, "value": value})


@app.route("/set/<key>", methods=["PUT", "POST"])
def set_route(key):
    """
        Sample usage:
    """

    value = request.get_json(silent=True)          # entire body = value
    if value is None:
        value = request.get_data(as_text=True)     # fallback for plain text

    expire = request.args.get("expire")            # ?expire=3600 in URL

    valkey_set(key, value, expire=int(expire) if expire else None)

    return jsonify({"message": "OK", "key": key})


@app.route("/delete/<key>", methods=["DELETE"])
def delete_route(key):
    """
        Sample usage:
        curl -X DELETE http://localhost:5000/delete/key1 
    """
    deleted = valkey_delete(key)
    return jsonify({"deleted": deleted})


@app.route('/fact_check', methods=['POST'])
def fact_check_video():
    """
    Endpoint for fact-checking video claims.
    Ensures safe response format even if AI or processing fails.
    """
    data = request.json
    video_id = data.get('video_id')

    if not video_id:
        return jsonify({"error": "No video_id provided"}), 400

    # 1. Setup Paths
    folder_path = os.path.join(DOWNLOAD_FOLDER, video_id)
    summary_path = os.path.join(
        folder_path, f"{video_id}_segmented_summary.json")
    fact_check_path = os.path.join(folder_path, f"{video_id}_factcheck.json")

    # 2. Check if video folder exists
    if not os.path.exists(folder_path):
        return jsonify({"error": "Video not found. Please run extraction first."}), 404

    # 3. Check Cache
    # CRUD GET 5: Try to get the fact check result from Valkey with the key "VIDEO_ID_fact_check.json"
    fact_check_json = valkey_get(video_id + "_fact_check.json")

    try:
        if fact_check_json is None:
            # 4. Check Prerequisites
            if not os.path.exists(summary_path):
                return jsonify({
                    "error": "Segmented summary missing. Video likely has no subtitles or summarization failed.",
                    "status": "missing_prerequisite"
                }), 404

            # 5. Run Fact Checker
            checker = FactChecker()
            fact_check_json = checker.process_video(
                summary_path, fact_check_path, video_id)

        if fact_check_json is not None:
            return jsonify(fact_check_json), 200
        else:
            raise Exception("Output file not created")

    except Exception as e:
        print(f"[CRITICAL] Fact check endpoint failed: {e}")
        # Return Safe Empty Response so frontend doesn't crash
        safe_response = {
            "fact_checks": [],
            "alternative_perspectives": [],
            "bias_distribution": {"left_count": 0, "center_count": 0, "right_count": 0},
            "status": "error",
            "reason": f"Server Error: {str(e)}"
        }
        return jsonify(safe_response), 500


if __name__ == '__main__':
    # Run the server
    app.run(debug=True, port=5002)
