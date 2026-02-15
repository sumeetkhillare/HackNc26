"""
YouTube Comment Analyzer - Context Aware Version
Analyzes video comments for Sentiment, Engagement Quality, and Bot Activity.
Uses Transcript Context to distinguish between Spam and Community Culture.
"""

import json
import sys
import os
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any

from valkey_rest.crud import valkey_get

# --- Configuration ---
# We use Gemini 2.0 Flash as it is the current standard for new API keys
DEFAULT_MODEL = "gemini-3-flash-preview" 

# Check for the new Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class CommentAnalyzer:
    """Analyzes YouTube comments for manipulation and credibility"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.use_ai = False
        self.client = None
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                # NEW SDK Initialization
                self.client = genai.Client(api_key=self.api_key)
                self.use_ai = True
                print(f"[OK] AI mode enabled ({DEFAULT_MODEL})")
            except Exception as e:
                self.use_ai = False
                print(f"[!] AI initialization failed: {e}. Switching to fallback.")
        else:
            if not GEMINI_AVAILABLE:
                print("[!] 'google-genai' library not installed. Using fallback.")
            elif not self.api_key:
                print("[!] No API key provided. Using fallback.")

    def load_json_file(self, json_path: str) -> Dict[str, Any]:
        """Generic JSON loader with error handling"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[!] Error: File not found: {json_path}")
            return {}
        except json.JSONDecodeError:
            print(f"[!] Error: Invalid JSON file: {json_path}")
            return {}

    def _format_transcript_context(self, transcript_data: Dict[str, Any]) -> str:
        """Extracts summaries from the segmented transcript JSON"""
        if not transcript_data or 'segments' not in transcript_data:
            return "No transcript context available."

        context_str = "VIDEO TRANSCRIPT SUMMARY (Timeline):\n"
        for seg in transcript_data.get('segments', []):
            time_range = seg.get('timestamps', {}).get('display', 'Unknown')
            # Handle cases where analysis might have failed
            analysis = seg.get('analysis', {})
            summary = analysis.get('summary', 'No summary provided.')
            topic = analysis.get('topic', 'Topic Unknown')
            
            context_str += f"- [{time_range}] {topic}: {summary}\n"
        
        return context_str

    def analyze_with_ai(self, video_data: Dict[str, Any], transcript_context: str) -> Dict[str, Any]:
        """Use Gemini AI for advanced analysis with Transcript Context"""
        comments = video_data.get('comments', [])
        title = video_data.get('title', 'Unknown Video')
        description = video_data.get('description', '')[:500]
        
        if not comments:
            return self._create_empty_analysis("No comments to analyze")

        # Analyze a larger sample since we are summarizing metrics
        comments_text = self._format_comments_for_prompt(comments[:200]) 
        
        prompt = f"""
        Act as an expert Social Media Analyst. Analyze these YouTube comments in the context of the video transcript provided.

        === VIDEO CONTEXT ===
        Title: "{title}"
        Description: "{description}"
        TRANSCRIPT SUMMARY: 
        {transcript_context}

        === COMMENTS TO ANALYZE ===
        {comments_text}

        === ANALYSIS INSTRUCTIONS ===
        1. **Detect Community Culture vs. Spam:**
           - Identify recurring phrases. If a phrase (e.g., "Petition to...", "Bro really...", "Who is here in 2026") matches the *tone* or *content* of the transcript,or is persent in multiple comments but has received good engagement, since bot comments are not well liked or get much replies other than the ones that mention bots classify it as "Meme/Culture" (Positive Engagement), NOT "Bot/Spam".
           - Only flag repetitive text as "Bot" if it is generic and irrelevant to the specific video topic (e.g., "Great video check my channel", "Promo smm panel").

        2. **Contextual Sentiment Analysis:**
           - If the video discusses a negative topic (e.g., a tragedy, a scam, or bad weather), comments expressing anger/disgust are likely *agreeing* with the video (Positive/Supportive alignment), not attacking the creator. Use the transcript to determine this alignment.

        === REQUIRED OUTPUT FORMAT (JSON) ===
        Strictly output JSON with no markdown formatting.
        {{
          "sentiment_counts": {{
            "positive": <int count>,
            "negative": <int count>,
            "neutral": <int count>
          }},
          "engagement_metrics": {{
            "engagement_score": <int 0-100 based on genuine discussion depth and relevance>,
            "bot_activity_percentage": <int 0-100>
          }},
          "community_insights": {{
            "dominant_topic": "<The main subject the comments are discussing>",
            "controversy_level": "<Low/Medium/High>"
          }},
          "summary_of_vibe": "<2 sentences summarizing how the audience feels about the video content>"
        }}
        """

        try:
            # NEW SDK Call Structure
            response = self.client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[!] AI Analysis failed ({e}). Falling back to rule-based.")
            return self._analyze_fallback(video_data)

    def _analyze_fallback(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based analysis (No AI required) - Matches new Output Structure"""
        comments = video_data.get('comments', [])
        
        if not comments:
            return self._create_empty_analysis("No comments available")

        # 1. Keywords
        bot_keywords = ['great video', 'nice', 'love it', 'amazing', 'cool', 'wow', 'best', 'promo', 'check my channel']
        skeptic_keywords = ['fake', 'scam', 'lie', 'false', 'debunk', 'clickbait']
        positive_keywords = ['love', 'agree', 'good', 'thanks', 'informative', 'lol', 'funny']
        
        # 2. Counters
        total = len(comments)
        metrics = {
            'positive': 0, 'negative': 0, 'neutral': 0,
            'bot': 0, 'total_len': 0
        }

        for c in comments:
            text = c.get('text', '').lower()
            t_len = len(text)
            metrics['total_len'] += t_len

            # Bot Detection (Simple Heuristic: Short + Generic)
            if t_len < 25 and any(k in text for k in bot_keywords):
                metrics['bot'] += 1
            
            # Sentiment (Simple Keyword Matching)
            elif any(k in text for k in positive_keywords):
                metrics['positive'] += 1
            elif any(k in text for k in skeptic_keywords):
                metrics['negative'] += 1
            else:
                metrics['neutral'] += 1
            
        # 3. Calculate Scores
        p_bot = round((metrics['bot'] / total) * 100) if total > 0 else 0
        
        # Engagement Score: Based on length (proxy for depth) and lack of bots
        avg_len = metrics['total_len'] / total if total > 0 else 0
        base_score = 50
        if avg_len > 50: base_score += 20
        if avg_len > 100: base_score += 10
        score = max(0, min(100, base_score - p_bot))

        return {
            "sentiment_counts": {
                "positive": metrics['positive'],
                "negative": metrics['negative'],
                "neutral": metrics['neutral']
            },
            "engagement_metrics": {
                "engagement_score": score,
                "bot_activity_percentage": p_bot
            },
            "community_insights": {
                "dominant_topic": "Unable to determine (AI Unavailable)",
                "controversy_level": "High" if metrics['negative'] > metrics['positive'] else "Low"
            },
            "summary_of_vibe": "Rule-based analysis performed. Sentiment derived from keywords only."
        }

    def _format_comments_for_prompt(self, comments: List[Dict]) -> str:
        """Helper to format comments into a readable string for AI"""
        out = ""
        for i, c in enumerate(comments):
            out += f"{i+1}. [{c.get('likes', 0)} likes] {c.get('author')}: {c.get('text')}\n"
            if c.get('replies'):
                for r in c.get('replies')[:2]:
                    out += f"    -> Reply: {r.get('text')}\n"
        return out

    def _create_empty_analysis(self, reason: str) -> Dict[str, Any]:
        return {
            "sentiment_counts": {"positive": 0, "negative": 0, "neutral": 0},
            "engagement_metrics": {"engagement_score": 0, "bot_activity_percentage": 0},
            "community_insights": {"dominant_topic": "None", "controversy_level": "Unknown"},
            "summary_of_vibe": reason
        }

    def run(self, video_id: str, output_path: Optional[str] = None, input_path: Optional[str] = None):
        """Main execution flow"""

        # 1. Load Video Data (Comments)
        metadata_key = video_id + "_summary.json"
        print(f"Starting Analysis for: {metadata_key}")

        # CRUD GET 1. Fetch the summary JSON data from Valkey with the key "VIDEO_ID_summary.json"
        video_data = valkey_get(metadata_key)

        
        # --- NEW ROBUST CHECK ---
        if not video_data or not isinstance(video_data, dict) or 'comments' not in video_data:
            print(f"[!] Warning: Data format issue in {metadata_key}. Normalizing...")
            # If it's a list, we wrap it; if empty, we provide defaults
            comments = video_data if isinstance(video_data, list) else []
            video_data = {'id': video_id, 'comments': comments}
        # ------------------------

        print(f"   Loaded {len(video_data.get('comments', []))} comments.")

        # 2. Load Transcript Context (if provided)
        # CRUD GET 4. Fetch the segmented summary data From Valkey with the key "VIDEO_ID_segmented_summary.json"
        transcript_key = video_id + "_segmented_summary.json"
        transcript_data = valkey_get(transcript_key)

        if transcript_data is None:
            print("   No Transcript Context provided (running in Context-Blind mode)")
        else:
            print(f"   Formatting Transcript Context: {transcript_key}")
            transcript_context = self._format_transcript_context(transcript_data)

        # 3. Analyze
        if self.use_ai:
            print("   Running AI Analysis (Context-Aware)...")
            result = self.analyze_with_ai(video_data, transcript_context)
        else:
            print("   Running Fallback Analysis (Rule-Based)...")
            result = self._analyze_fallback(video_data)

        # 4. Save Output
        final_output = {
            "video_id": video_data.get('id', 'unknown'),
            "analyzed_at": datetime.now().isoformat(),
            "context_source": "Transcript + Metadata" if transcript_data else "Metadata Only",
            "analysis": result # This now contains the clean 4 keys requested
        }

        if not output_path:
            output_path = input_path.replace(".json", "_analysis.json")
            if output_path == input_path:
                output_path += "_analysis.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)

        print(f"Analysis saved to: {output_path}\n")