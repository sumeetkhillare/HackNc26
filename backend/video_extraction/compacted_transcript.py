#!/usr/bin/env python3
"""
Video Transcript Segmenter & Summarizer
Parses .vtt files, splits them into 5-minute segments, and uses Gemini AI 
to generate structured summaries for each segment.

Features:
- VTT Parsing: Extracts clean text while preserving timeline flow.
- Smart Segmentation: Chunks transcript into 5-minute blocks.
- AI Summarization: Uses Gemini (via google-genai SDK) to summarize segments.
- Fallback Mode: Preserves raw text segments if AI is unavailable/fails.
"""

import json
import sys
import os
import re
import argparse
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# --- Configuration ---
# Using the model specified in your reference
DEFAULT_MODEL = "gemini-3-flash-preview" 

# Check for the new Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class TranscriptSegmenter:
    """Parses VTT, segments by time, and summarizes using Gemini"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.use_ai = False
        self.client = None

        if GEMINI_AVAILABLE and self.api_key:
            try:
                # NEW SDK Initialization based on your reference
                self.client = genai.Client(api_key=self.api_key)
                self.use_ai = True
                print(f"[OK] AI mode enabled ({DEFAULT_MODEL})")
            except Exception as e:
                self.use_ai = False
                print(f"[!] AI initialization failed: {e}. Switching to text-only segmentation.")
        else:
            if not GEMINI_AVAILABLE:
                print("[!] 'google-genai' library not installed. Using text-only segmentation.")
            elif not self.api_key:
                print("[!] No API key provided. Using text-only segmentation.")

    def parse_timestamp(self, timestamp_str: str) -> float:
        """Converts VTT timestamp (00:00:00.000) to total seconds"""
        try:
            parts = timestamp_str.split(':')
            seconds = 0.0
            if len(parts) == 3: # HH:MM:SS.mmm
                seconds += float(parts[0]) * 3600
                seconds += float(parts[1]) * 60
                seconds += float(parts[2])
            elif len(parts) == 2: # MM:SS.mmm
                seconds += float(parts[0]) * 60
                seconds += float(parts[1])
            return seconds
        except ValueError:
            return 0.0

    def clean_vtt_text(self, raw_lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parses raw VTT lines, removing duplicates caused by rolling captions.
        """
        parsed_entries = []
        
        # Regex patterns
        timestamp_pattern = re.compile(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})')
        tag_pattern = re.compile(r'<[^>]*>')
        
        current_start_time = 0.0
        current_text_buffer = []
        
        for line in raw_lines:
            line = line.strip()
            
            # Skip header info
            if not line or line == "WEBVTT" or line.startswith("Kind:") or line.startswith("Language:"):
                continue
            
            # Check for timestamp line
            ts_match = timestamp_pattern.search(line)
            if ts_match:
                # 1. Process the previous buffer before starting a new block
                if current_text_buffer:
                    full_text = " ".join(current_text_buffer).strip()
                    
                    # --- DEDUPLICATION LOGIC ---
                    # Check if this text is identical to the last one we saved.
                    if full_text and (not parsed_entries or parsed_entries[-1]['text'] != full_text):
                        parsed_entries.append({'start': current_start_time, 'text': full_text})
                    
                    current_text_buffer = [] # Clear buffer for the new block
                
                # 2. Update start time for the NEW block
                current_start_time = self.parse_timestamp(ts_match.group(1))
                continue
            
            # Process text lines
            clean_line = tag_pattern.sub('', line)
            
            # Unescape HTML entities
            clean_line = clean_line.replace('&nbsp;', ' ').replace('&gt;', '>').replace('&lt;', '<')
            clean_line = clean_line.strip()
            
            if clean_line:
                # Add to buffer if it's not a repeat of the line immediately above it
                if not current_text_buffer or clean_line != current_text_buffer[-1]:
                    current_text_buffer.append(clean_line)

        # Handle any remaining text after the loop ends
        if current_text_buffer:
            full_text = " ".join(current_text_buffer).strip()
            if full_text and (not parsed_entries or parsed_entries[-1]['text'] != full_text):
                parsed_entries.append({'start': current_start_time, 'text': full_text})
                
        return parsed_entries

    def create_segments(self, parsed_entries: List[Dict], interval_minutes: int = 5) -> List[Dict]:
        """Groups parsed entries into fixed time chunks"""
        interval_seconds = interval_minutes * 60
        segments = []
        current_segment_text = []
        current_segment_index = 0
        
        for entry in parsed_entries:
            start_time = entry['start']
            text = entry['text']
            
            # Determine which segment index this entry belongs to
            segment_index = int(start_time // interval_seconds)
            
            # If we moved to a new segment, save the old one
            while len(segments) <= segment_index:
                segments.append({
                    "segment_id": len(segments) + 1,
                    "start_time_seconds": len(segments) * interval_seconds,
                    "end_time_seconds": (len(segments) + 1) * interval_seconds,
                    "text": ""
                })
            
            # Append text to the correct segment
            segments[segment_index]["text"] += text + " "

        # Clean up empty segments and whitespace
        final_segments = []
        for seg in segments:
            seg['text'] = seg['text'].strip()
            if seg['text']: # Only keep segments with content
                # Format timestamps for display
                start_str = str(timedelta(seconds=int(seg['start_time_seconds'])))
                end_str = str(timedelta(seconds=int(seg['end_time_seconds'])))
                seg['timestamp_range'] = f"{start_str} - {end_str}"
                final_segments.append(seg)
                
        return final_segments

    def generate_ai_summary(self, segment_text: str, timestamp_range: str) -> Dict[str, Any]:
        """Uses Gemini to summarize the text segment with STRICT schema validation"""
        
        prompt = f"""
        Analyze the following transcript segment from a video ({timestamp_range}).
        TRANSCRIPT TEXT: {segment_text[:15000]} 
        """

        # Define the strict schema for the output
        # This forces the model to return exactly these keys with these types.
        summary_schema = types.Schema(
            type=types.Type.OBJECT,
            properties={
                "topic": types.Schema(type=types.Type.STRING),
                "summary": types.Schema(type=types.Type.STRING),
                "key_points": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING)
                ),
                "sentiment": types.Schema(
                    type=types.Type.STRING,
                    enum=["Positive", "Neutral", "Negative", "Controversial"] # Enforce specific values
                ),
                "entities_mentioned": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING)
                )
            },
            required=["topic", "summary", "key_points", "sentiment", "entities_mentioned"]
        )

        try:
            response = self.client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=summary_schema  # <--- THIS ENFORCES THE STRUCTURE
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[!] AI Generation failed for segment {timestamp_range}: {e}")
            return self._create_fallback_summary()

    def _create_fallback_summary(self) -> Dict[str, Any]:
        """Fallback JSON if AI fails or is disabled"""
        return {
            "topic": "Analysis Unavailable",
            "summary": "AI summarization could not be completed for this segment.",
            "key_points": [],
            "sentiment": "Unknown",
            "entities_mentioned": []
        }

    def process_file(self, input_path: str, output_path: Optional[str] = None):
        """Main processing pipeline"""
        print(f"Processing: {input_path}")
        
        # 1. Read File
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                raw_lines = f.readlines()
        except FileNotFoundError:
            print(f"[!] Error: File not found: {input_path}")
            sys.exit(1)

        # 2. Parse & Segment
        print(" -> Parsing VTT...")
        parsed_entries = self.clean_vtt_text(raw_lines)
        print(" -> Segmenting into 5-minute chunks...")
        segments = self.create_segments(parsed_entries, interval_minutes=5)
        print(f" -> Created {len(segments)} segments.")

        # 3. Analyze each segment
        processed_data = []
        
        for seg in segments:
            print(f"    Analyzing Segment {seg['segment_id']} ({seg['timestamp_range']})...")
            
            ai_data = {}
            include_raw_text = False # Default to False (don't show raw text if AI works)

            if self.use_ai:
                ai_data = self.generate_ai_summary(seg['text'], seg['timestamp_range'])
                
                # Check if the AI returned our fallback error message
                if ai_data.get("topic") == "Analysis Unavailable":
                    include_raw_text = True
            else:
                # AI is disabled, so we must include raw text
                ai_data = self._create_fallback_summary()
                include_raw_text = True
            
            # Combine structural data with AI analysis
            segment_result = {
                "segment_id": seg['segment_id'],
                "timestamps": {
                    "start_sec": seg['start_time_seconds'],
                    "end_sec": seg['end_time_seconds'],
                    "display": seg['timestamp_range']
                },
                "analysis": ai_data
            }

            # Only add the massive raw text block if AI failed or is off
            if include_raw_text:
                segment_result["raw_transcript"] = seg['text']

            processed_data.append(segment_result)

        # 4. Final Output Construction
        final_output = {
            "source_file": os.path.basename(input_path),
            "processed_at": datetime.now().isoformat(),
            "total_segments": len(processed_data),
            "segments": processed_data
        }

        # 5. Save
        if not output_path:
            output_path = input_path.replace(".vtt", "_segmented_summary.json")
            if output_path == input_path: # safety if extension didn't match
                output_path += ".json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
            
        print(f"\n[Success] JSON saved to: {output_path}")

if __name__ == "__main__":
    input_file = r"C:\Users\Admin\Desktop\Personal\mlh2026\HackNc26\backend\video_extraction\downloaded_content\mqXovE-n9EA\mqXovE-n9EA.en.vtt" # Change this to your file path
    output_file = "mqXovE-n9EA_segmented_summary.json"
    segmenter = TranscriptSegmenter(api_key="AIzaSyBw7jgmMmbYy_4L0ErQqgtaozkbcii_DY8")
    segmenter.process_file(input_file, output_file)