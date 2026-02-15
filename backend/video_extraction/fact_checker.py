#!/usr/bin/env python3
"""
Video Fact Checker & Perspective Analyzer (DuckDuckGo Version)
1. Extracts verifiable claims (skips non-news content safely).
2. Searches the ENTIRE WEB using DuckDuckGo (No Google API Key needed).
3. Verifies claims, finds perspectives, and calculates media bias.
"""

import json
import os
import argparse
from typing import List, Dict, Any

# --- Configuration ---
# Only Gemini Key is needed now!
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3-flash-preview" 

# --- Imports ---
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[!] Warning: 'google-genai' library not installed. pip install google-genai")

try:
    from duckduckgo_search import DDGS
    DDG_AVAILABLE = True
except ImportError:
    DDG_AVAILABLE = False
    print("[!] Warning: 'duckduckgo-search' library not installed. pip install duckduckgo-search")

class FactChecker:
    def __init__(self):
        self.gemini_client = None
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        
    def _load_json(self, path: str) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error loading file: {e}")
            return {}

    def _create_safe_empty_response(self, reason: str = "Content not verifiable") -> Dict:
        """Returns a constant format JSON that won't crash the frontend."""
        return {
            "fact_checks": [],
            "alternative_perspectives": [],
            "bias_distribution": {
                "left_count": 0,
                "center_count": 0,
                "right_count": 0
            },
            "status": "skipped",
            "reason": reason
        }

    # --- Step 1: Extract Claims (Smart Filter) ---
    def extract_claims(self, transcript_data: Dict) -> Dict:
        print(" -> Analyzing content type and extracting claims...")
        segments = transcript_data.get("segments", [])
        if not segments:
            return {"is_news": False, "claims": []}

        # Prepare context
        segments_text = ""
        for seg in segments:
            analysis = seg.get("analysis", {})
            points = analysis.get("key_points", [])
            summary = analysis.get("summary", "")
            segments_text += f"Segment {seg['segment_id']}: {summary}. Key Points: {'; '.join(points)}\n\n"

        prompt = f"""
        You are a Content Triage Bot. Analyze these video summaries.
        
        TASK 1: CLASSIFY CONTENT
        Determine if this content is "Fact-Checkable News/Information" or "Subjective Entertainment".
        - Set 'is_checkable' to FALSE for gaming, music, vlogs, or pure opinion.
        - Set 'is_checkable' to TRUE for news, politics, science, or educational content.

        TASK 2: EXTRACT CLAIMS (Only if True)
        If True, extract verifiable factual claims (names, events, stats).
        
        INPUT DATA:
        {segments_text}
        """

        extraction_schema = types.Schema(
            type=types.Type.OBJECT,
            properties={
                "is_checkable": types.Schema(type=types.Type.BOOLEAN),
                "claims": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "claim_text": types.Schema(type=types.Type.STRING),
                            "segment_id": types.Schema(type=types.Type.INTEGER)
                        },
                        required=["claim_text", "segment_id"]
                    )
                )
            },
            required=["is_checkable", "claims"]
        )

        try:
            response = self.gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=extraction_schema
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[!] Extraction failed: {e}")
            return {"is_checkable": False, "claims": []}

    # --- Step 2: Search Evidence (DuckDuckGo) ---
    def search_duckduckgo(self, query: str) -> List[Dict]:
        """Searches DuckDuckGo News and Web"""
        if not DDG_AVAILABLE:
            return []

        results = []
        try:
            with DDGS() as ddgs:
                # 1. Try News Search first (better for fact checking)
                news_gen = ddgs.news(query, max_results=3)
                if news_gen:
                    for r in news_gen:
                        results.append({
                            "title": r.get('title'),
                            "snippet": r.get('body'), # DDG uses 'body' for news snippets
                            "source": r.get('source'),
                            "url": r.get('url')
                        })
                
                # 2. Fallback to Web Search if news is empty or sparse
                if len(results) < 2:
                    web_gen = ddgs.text(query, max_results=3)
                    if web_gen:
                        for r in web_gen:
                            results.append({
                                "title": r.get('title'),
                                "snippet": r.get('body'),
                                "source": r.get('href'), # Web search doesn't always have source name
                                "url": r.get('href')
                            })
                            
            return results[:5] # Return top 5 combined
        except Exception as e:
            print(f"[!] DDG Search failed for '{query}': {e}")
            return []

    # --- Step 3: Verify & Synthesize ---
    def verify_and_synthesize(self, claims_with_evidence: List[Dict]) -> Dict:
        print(" -> Verifying claims and calculating media bias...")
        
        input_context = ""
        for item in claims_with_evidence:
            input_context += f"""
            CLAIM: "{item['claim']}"
            SEARCH RESULTS:
            {json.dumps(item['search_results'], indent=2)}
            ------------------------------------------------
            """

        prompt = f"""
        Act as a Fact Checker and Media Bias Analyst.
        
        TASKS:
        1. FACT CHECK: Verdict (True/False/Unverified) based on evidence.
        2. PERSPECTIVES: Identify varied news sources.
        3. BIAS DISTRIBUTION: Count Left/Center/Right leaning sources found in the evidence.
        
        INPUT DATA:
        {input_context}
        """

        final_schema = types.Schema(
            type=types.Type.OBJECT,
            properties={
                "fact_checks": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "claim": types.Schema(type=types.Type.STRING),
                            "verdict": types.Schema(
                                type=types.Type.STRING, 
                                enum=["True", "False", "Unverified", "Context Missing"]
                            ),
                            "explanation": types.Schema(type=types.Type.STRING)
                        },
                        required=["claim", "verdict", "explanation"]
                    )
                ),
                "alternative_perspectives": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "source": types.Schema(type=types.Type.STRING),
                            "type": types.Schema(type=types.Type.STRING),
                            "description": types.Schema(type=types.Type.STRING),
                            "url": types.Schema(type=types.Type.STRING)
                        },
                        required=["source", "type", "description", "url"]
                    )
                ),
                "bias_distribution": types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "left_count": types.Schema(type=types.Type.INTEGER),
                        "center_count": types.Schema(type=types.Type.INTEGER),
                        "right_count": types.Schema(type=types.Type.INTEGER)
                    },
                    required=["left_count", "center_count", "right_count"]
                )
            },
            required=["fact_checks", "alternative_perspectives", "bias_distribution"]
        )

        try:
            response = self.gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=final_schema
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[!] Verification failed: {e}")
            return self._create_safe_empty_response("AI Processing Failed")

    def process_video(self, input_path: str, output_path: str):
        print(f"Starting Fact Check for: {input_path}")
        data = self._load_json(input_path)
        if not data: return

        extraction_result = self.extract_claims(data)
        
        if not extraction_result.get("is_checkable", False):
            print(" -> Video identified as Non-News. Skipping.")
            final_result = self._create_safe_empty_response("Non-News Content")
        else:
            claims = extraction_result.get("claims", [])
            print(f" -> Found {len(claims)} verifiable claims.")
            
            claims_with_evidence = []
            for item in claims:
                claim_txt = item['claim_text']
                print(f"    Searching: {claim_txt[:50]}...")
                
                # DuckDuckGo Search (No "news verification" suffix needed, DDG is smart)
                results = self.search_duckduckgo(claim_txt)
                claims_with_evidence.append({"claim": claim_txt, "search_results": results})

            final_result = self.verify_and_synthesize(claims_with_evidence)
            final_result["status"] = "processed"

        final_output = {
            "video_source": data.get("source_file"),
            "checked_at": "2026-02-14", 
            "analysis": final_result
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        print(f"\n[Success] Fact Check saved to: {output_path}")