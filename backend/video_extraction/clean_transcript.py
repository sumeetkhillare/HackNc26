import re
import os
import json

import valkey_rest

def clean_vtt(file_path, video_id):
    """
    Cleans a VTT file, saves the result as a JSON file in the same directory,
    and returns True if successful, False otherwise.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        clean_lines = []
        
        # Regex patterns
        timestamp_pattern = re.compile(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}')
        tag_pattern = re.compile(r'<[^>]*>')

        for line in lines:
            line = line.strip()
            
            # Skip header, timestamps, and empty lines
            if not line or line == "WEBVTT" or line.startswith("Kind:") or line.startswith("Language:"):
                continue
            if timestamp_pattern.search(line):
                continue
                
            # Remove tags
            clean_text = tag_pattern.sub('', line)
            if clean_text:
                clean_lines.append(clean_text)

        # Deduplicate lines (fix for rolling captions)
        final_text = []
        for line in clean_lines:
            if not final_text or line != final_text[-1]:
                final_text.append(line)

        transcript_string = " ".join(final_text)

        # --- Save to JSON ---
        # Create output path with .json extension in the same folder
        base_path = os.path.splitext(file_path)[0]
        json_path = f"{base_path}_clean_transcript.json"

        output_data = {
            "source_file": os.path.basename(file_path),
            "transcript": transcript_string
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
            
        # CRUD PUT 3. Save the clean trascript data to Valkey with the key "VIDEO_ID_clean_transcript.json"
        valkey_rest.crud.valkey_set(video_id + "_clean_transcript.json", json.dump(output_data, indent=4, ensure_ascii=False))

        print(f"Transcript saved to: {json_path}")
        return True

    except Exception as e:
        print(f"Error cleaning VTT: {e}")
        return False