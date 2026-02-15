#!/usr/bin/env python3
"""
YouTube Video Fact Checker & Alternative Perspectives Finder
Uses Gemini with Google Search grounding to verify claims and find related sources.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Check for the new Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# DEFAULT_MODEL = "gemini-1.5-flash"  # Stable model that works with most API keys
DEFAULT_MODEL = "gemini-3-flash-preview"
class FactCheckerAndPerspectives:
    """Analyzes video transcript for factual claims and finds alternative perspectives"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.use_ai = False
        self.client = None
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.use_ai = True
                print(f"[OK] Fact Checker AI mode enabled ({DEFAULT_MODEL})")
            except Exception as e:
                self.use_ai = False
                print(f"[!] AI initialization failed: {e}. Using fallback.")
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

    def _extract_transcript_text(self, transcript_data: Dict[str, Any]) -> str:
        """Extract full transcript text from either segmented or simple transcript JSON"""
        
        # Format 1: Simple text format - {"transcript": "full text here..."}
        if 'transcript' in transcript_data:
            transcript_text = transcript_data.get('transcript', '')
            if isinstance(transcript_text, str):
                print("   [Loaded simple transcript format]")
                return transcript_text.strip()
        
        # Format 2: Segmented format - {"segments": [...]}
        if 'segments' in transcript_data:
            full_text = ""
            for seg in transcript_data.get('segments', []):
                text = seg.get('text', '')
                if text:
                    full_text += text + " "
            
            if full_text:
                print("   [Loaded segmented transcript format]")
                return full_text.strip()
        
        # No valid format found
        print("   [!] Warning: No valid transcript format found")
        return "No transcript available."

    def _extract_video_metadata(self, video_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract key metadata from video data"""
        return {
            "title": video_data.get('title', 'Unknown'),
            "description": video_data.get('description', '')[:800],
            "channel": video_data.get('channel', 'Unknown Channel'),
            "video_id": video_data.get('id', 'unknown')
        }

    def combined_analysis_with_ai(self, transcript_text: str, video_metadata: Dict[str, str], transcript_summary: str) -> Dict[str, Any]:
        """COMBINED fact-checking and perspectives in ONE API call to save rate limits"""
        
        if not transcript_text or len(transcript_text) < 50:
            return {"fact_checks": [], "alternative_perspectives": []}

        # Truncate if too long
        if len(transcript_text) > 8000:
            transcript_text = transcript_text[:8000] + "..."
        
        # Truncate summary to reduce tokens
        if len(transcript_summary) > 500:
            transcript_summary = transcript_summary[:500] + "..."

        prompt = f"""
You are an expert fact-checker and research assistant. Analyze this YouTube video and provide TWO things:

=== VIDEO METADATA ===
Title: "{video_metadata['title']}"
Channel: "{video_metadata['channel']}"
Description: "{video_metadata['description']}"

=== TRANSCRIPT ===
{transcript_text}

=== SUMMARY ===
{transcript_summary}

=== TASK 1: FACT-CHECK CLAIMS ===
1. Identify 3-5 specific FACTUAL CLAIMS (not opinions or predictions)
2. Use Google Search to verify if TRUE, FALSE, or PARTIALLY TRUE
3. Provide brief explanation with sources

Focus on: Scientific claims, statistics, historical facts, news events
Ignore: Opinions ("I think..."), predictions, subjective statements

=== TASK 2: FIND ALTERNATIVE PERSPECTIVES ===
Use Google Search to find 3-5 credible sources covering this topic:
- Mainstream media (BBC, Reuters, NYT, WSJ)
- Academic/Scientific sources
- Fact-checking organizations
- Alternative viewpoints

Prioritize recent (last 6 months), credible sources that ADD different angles.

=== OUTPUT FORMAT (JSON) ===
Return ONLY valid JSON, no markdown:
{{
  "fact_checks": [
    {{
      "claim": "Exact quote or paraphrased claim",
      "verdict": "true|false|partial",
      "explanation": "Brief verification with source"
    }}
  ],
  "alternative_perspectives": [
    {{
      "source": "Source name (e.g., BBC News)",
      "type": "Perspective type (e.g., Mainstream Media)",
      "description": "How this differs (1-2 sentences)",
      "url": "https://actual-url-found.com"
    }}
  ]
}}

If no results, return: {{"fact_checks": [], "alternative_perspectives": []}}
"""

        try:
            print("   [Combined API call - fact-checking + perspectives...]")
            response = self.client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            
            result = json.loads(response.text)
            return {
                "fact_checks": result.get('fact_checks', []),
                "alternative_perspectives": result.get('alternative_perspectives', [])
            }
            
        except Exception as e:
            print(f"[!] Combined analysis failed: {e}")
            return {"fact_checks": [], "alternative_perspectives": []}

    def combined_analysis_with_ai(self, transcript_text: str, video_metadata: Dict[str, str], transcript_summary: str) -> Dict[str, Any]:
        """COMBINED fact-checking and perspectives in ONE API call to save rate limits"""
        
        if not transcript_text or len(transcript_text) < 50:
            return {"fact_checks": [], "alternative_perspectives": []}

        # Truncate if too long
        if len(transcript_text) > 8000:
            transcript_text = transcript_text[:8000] + "..."
        
        # Truncate summary to reduce tokens
        if len(transcript_summary) > 500:
            transcript_summary = transcript_summary[:500] + "..."

        prompt = f"""
You are an expert fact-checker and research assistant. Analyze this YouTube video and provide TWO things:

=== VIDEO METADATA ===
Title: "{video_metadata['title']}"
Channel: "{video_metadata['channel']}"
Description: "{video_metadata['description']}"

=== TRANSCRIPT ===
{transcript_text}

=== SUMMARY ===
{transcript_summary}

=== TASK 1: FACT-CHECK CLAIMS ===
1. Identify 3-5 specific FACTUAL CLAIMS (not opinions or predictions)
2. Use Google Search to verify if TRUE, FALSE, or PARTIALLY TRUE
3. Provide brief explanation with sources

Focus on: Scientific claims, statistics, historical facts, news events
Ignore: Opinions ("I think..."), predictions, subjective statements

=== TASK 2: FIND ALTERNATIVE PERSPECTIVES ===
Use Google Search to find 3-5 credible sources covering this topic:
- Mainstream media (BBC, Reuters, NYT, WSJ)
- Academic/Scientific sources
- Fact-checking organizations
- Alternative viewpoints

Prioritize recent (last 6 months), credible sources that ADD different angles.

=== OUTPUT FORMAT (JSON) ===
Return ONLY valid JSON, no markdown:
{{
  "fact_checks": [
    {{
      "claim": "Exact quote or paraphrased claim",
      "verdict": "true|false|partial",
      "explanation": "Brief verification with source"
    }}
  ],
  "alternative_perspectives": [
    {{
      "source": "Source name (e.g., BBC News)",
      "type": "Perspective type (e.g., Mainstream Media)",
      "description": "How this differs (1-2 sentences)",
      "url": "https://actual-url-found.com"
    }}
  ]
}}

If no results, return: {{"fact_checks": [], "alternative_perspectives": []}}
"""

        try:
            print("   [Combined API call - fact-checking + perspectives in ONE request...]")
            print(prompt)
            
            # Enable Google Search grounding
            response = self.client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            
            result = json.loads(response.text)
            return {
                "fact_checks": result.get('fact_checks', []),
                "alternative_perspectives": result.get('alternative_perspectives', [])
            }
            
        except Exception as e:
            print(f"[!] Combined analysis failed: {e}")
            return {"fact_checks": [], "alternative_perspectives": []}

    def fact_check_with_ai(self, transcript_text: str, video_metadata: Dict[str, str]) -> List[Dict[str, str]]:
        """Use Gemini with Google Search to fact-check claims in the transcript"""
        
        if not transcript_text or len(transcript_text) < 50:
            return []

        # Truncate if too long (Gemini has token limits)
        if len(transcript_text) > 8000:
            transcript_text = transcript_text[:8000] + "..."

        prompt = f"""
You are an expert fact-checker. Analyze this YouTube video transcript and identify factual claims that can be verified.

=== VIDEO METADATA ===
Title: "{video_metadata['title']}"
Channel: "{video_metadata['channel']}"
Description: "{video_metadata['description']}"

=== TRANSCRIPT ===
{transcript_text}

=== TASK ===
1. Identify 3-5 specific FACTUAL CLAIMS made in this video (not opinions or predictions)
2. For each claim, use Google Search to verify if it's TRUE, FALSE, or PARTIALLY TRUE
3. Provide a clear explanation with sources

Focus on:
- Scientific claims
- Historical facts
- Statistical data
- News events
- Technical specifications

Ignore:
- Opinions ("I think...", "In my view...")
- Future predictions
- Subjective statements

=== OUTPUT FORMAT (JSON) ===
Return ONLY valid JSON, no markdown:
{{
  "fact_checks": [
    {{
      "claim": "Exact quote or paraphrased claim from transcript",
      "verdict": "true|false|partial",
      "explanation": "Brief explanation with verification source if available"
    }}
  ]
}}

If no verifiable factual claims are found, return: {{"fact_checks": []}}
"""

        try:
            # Enable Google Search grounding
            response = self.client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    # Enable search grounding for fact-checking
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            
            result = json.loads(response.text)
            return result.get('fact_checks', [])
            
        except Exception as e:
            print(f"[!] Fact-checking failed: {e}")
            return []

    def find_alternative_perspectives_with_ai(self, video_metadata: Dict[str, str], transcript_summary: str) -> List[Dict[str, str]]:
        """Use Gemini with Google Search to find alternative perspectives and related sources"""
        
        prompt = f"""
You are a research assistant finding alternative perspectives on a YouTube video topic.

=== VIDEO METADATA ===
Title: "{video_metadata['title']}"
Channel: "{video_metadata['channel']}"
Description: "{video_metadata['description']}"

=== VIDEO SUMMARY ===
{transcript_summary[:1000]}

=== TASK ===
Use Google Search to find 3-5 credible alternative sources covering this same topic from different perspectives:

1. Mainstream media (e.g., BBC, Reuters, NYT, WSJ)
2. Academic/Scientific sources (if applicable)
3. Investigative journalism or fact-checking organizations
4. Alternative viewpoints (different political/ideological angles if relevant)

For each source:
- Provide the actual source name
- Categorize the perspective type
- Describe how their coverage differs or complements this video
- Include the URL if found via search

Prioritize:
- Recent articles (within last 6 months if topic is current)
- Credible, well-known sources
- Sources that ADD different angles, not just repeat the same info

=== OUTPUT FORMAT (JSON) ===
Return ONLY valid JSON, no markdown:
{{
  "alternative_perspectives": [
    {{
      "source": "Source name (e.g., BBC News, Nature Journal)",
      "type": "Perspective type (e.g., Mainstream Media, Academic Research, Fact-Check)",
      "description": "How this source covers the topic differently (1-2 sentences)",
      "url": "https://actual-url-found-via-search.com"
    }}
  ]
}}

If no relevant sources found, return: {{"alternative_perspectives": []}}
"""

        try:
            # Enable Google Search grounding
            response = self.client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    tools=[types.Tool(google_search=types.GoogleSearch())]
                )
            )
            
            result = json.loads(response.text)
            return result.get('alternative_perspectives', [])
            
        except Exception as e:
            print(f"[!] Alternative perspectives search failed: {e}")
            return []

    def _fallback_fact_check(self, transcript_text: str) -> List[Dict[str, str]]:
        """Fallback fact-checking without AI (very basic)"""
        # Simple keyword detection for common fact-checkable claims
        fact_indicators = [
            'study shows', 'research found', 'scientists say', 'data shows',
            'statistics', 'according to', 'percent', '%', 'billion', 'million',
            'year', 'discovered', 'proven', 'evidence'
        ]
        
        text_lower = transcript_text.lower()
        
        # If transcript contains fact-like keywords, return a placeholder
        if any(keyword in text_lower for keyword in fact_indicators):
            return [{
                "claim": "AI fact-checking unavailable - Manual verification recommended",
                "verdict": "partial",
                "explanation": "This video contains factual claims that should be verified. AI analysis is unavailable."
            }]
        
        return []

    def _fallback_perspectives(self, video_metadata: Dict[str, str]) -> List[Dict[str, str]]:
        """Fallback alternative perspectives without AI"""
        # Generic suggestions based on video topic keywords
        title_lower = video_metadata['title'].lower()
        
        suggestions = []
        
        # Science/Health topics
        if any(word in title_lower for word in ['science', 'health', 'medical', 'study', 'research']):
            suggestions.append({
                "source": "PubMed / Scientific Journals",
                "type": "Academic Research",
                "description": "Search academic databases for peer-reviewed research on this topic.",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={video_metadata['title'].replace(' ', '+')}"
            })
        
        # News/Current Events
        if any(word in title_lower for word in ['news', 'breaking', 'report', 'crisis', 'event']):
            suggestions.append({
                "source": "Google News",
                "type": "News Aggregation",
                "description": "Check multiple news sources for comprehensive coverage.",
                "url": f"https://news.google.com/search?q={video_metadata['title'].replace(' ', '+')}"
            })
        
        # Add fact-checking resources
        suggestions.append({
            "source": "Fact-Checking Organizations",
            "type": "Fact-Check",
            "description": "Verify claims through Snopes, FactCheck.org, or PolitiFact.",
            "url": "https://www.snopes.com"
        })
        
        return suggestions if suggestions else []

    def analyze(self, video_data: Dict[str, Any], transcript_data: Dict[str, Any], use_combined: bool = True) -> Dict[str, Any]:
        """Main analysis function combining fact-checking and alternative perspectives
        
        Args:
            video_data: Video metadata dictionary
            transcript_data: Transcript data dictionary
            use_combined: If True, makes 1 API call instead of 2 (recommended to avoid rate limits)
        """
        
        # Extract data
        video_metadata = self._extract_video_metadata(video_data)
        transcript_text = self._extract_transcript_text(transcript_data)
        
        # Get summary from transcript for context
        transcript_summary = ""
        
        # Try to get summary from segmented format
        if transcript_data and 'segments' in transcript_data:
            summaries = [seg.get('analysis', {}).get('summary', '') 
                        for seg in transcript_data['segments'][:3]]  # First 3 segments
            transcript_summary = ' '.join(filter(None, summaries))
        
        # If no summary from segments, use first 1000 chars of transcript text
        if not transcript_summary:
            transcript_summary = transcript_text[:1000] if transcript_text else ""
        
        print(f"   Analyzing video: {video_metadata['title']}")
        print(f"   Transcript length: {len(transcript_text)} characters")
        
        result = {
            "fact_checks": [],
            "alternative_perspectives": []
        }
        
        if self.use_ai and transcript_text and len(transcript_text) > 50:
            # AI-powered analysis
            
            if use_combined:
                # ============ COMBINED API CALL (RECOMMENDED) ============
                # Makes 1 API call instead of 2 - saves rate limits!
                print("   [Using combined API call to save rate limits]")
                result = self.combined_analysis_with_ai(transcript_text, video_metadata, transcript_summary)
                
            else:
                # ============ SEPARATE API CALLS (ORIGINAL) ============
                # Makes 2 API calls - may hit rate limits faster
                print("   [Using separate API calls]")
                print("   Running AI fact-checking with Google Search...")
                result['fact_checks'] = self.fact_check_with_ai(transcript_text, video_metadata)
                
                print("   Finding alternative perspectives with Google Search...")
                result['alternative_perspectives'] = self.find_alternative_perspectives_with_ai(
                    video_metadata, 
                    transcript_summary
                )
        else:
            # Fallback
            print("   Using fallback analysis (AI unavailable or transcript too short)...")
            result['fact_checks'] = self._fallback_fact_check(transcript_text)
            result['alternative_perspectives'] = self._fallback_perspectives(video_metadata)
        
        print(f"   Found {len(result['fact_checks'])} fact-checks")
        print(f"   Found {len(result['alternative_perspectives'])} alternative sources")
        
        return result

    def run(self, video_path: str, transcript_path: str, output_path: Optional[str] = None, use_combined: bool = True):
        """Run fact-checking and perspective analysis
        
        Args:
            video_path: Path to video metadata JSON
            transcript_path: Path to transcript JSON
            output_path: Path to save output (optional)
            use_combined: If True, uses 1 API call instead of 2 (default: True)
        """
        
        print("Starting Fact-Checking & Alternative Perspectives Analysis...")
        print(f"   Mode: {'COMBINED (1 API call)' if use_combined else 'SEPARATE (2 API calls)'}")
        
        # Load data
        video_data = self.load_json_file(video_path)
        transcript_data = self.load_json_file(transcript_path)
        
        if not video_data:
            print("[!] Error: Could not load video data")
            return
        
        if not transcript_data:
            print("[!] Warning: No transcript data - results may be limited")
        
        # Analyze (with use_combined flag)
        result = self.analyze(video_data, transcript_data, use_combined=use_combined)
        
        # Save output
        final_output = {
            "video_id": video_data.get('id', 'unknown'),
            "analyzed_at": datetime.now().isoformat(),
            "fact_checks": result['fact_checks'],
            "alternative_perspectives": result['alternative_perspectives']
        }
        
        if not output_path:
            output_path = video_path.replace(".json", "_fact_check.json")
            if output_path == video_path:
                output_path += "_fact_check.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Analysis saved to: {output_path}")
        return final_output


if __name__ == "__main__":
    # import argparse
    
    # parser = argparse.ArgumentParser(description="YouTube Video Fact Checker & Alternative Perspectives")
    # parser.add_argument("video_file", help="Path to video metadata JSON file")
    # parser.add_argument("transcript_file", help="Path to segmented transcript JSON file")
    # parser.add_argument("-o", "--output", help="Path to output JSON file", default=None)
    # parser.add_argument("--key", help="Gemini API Key", default=None)
    
    # args = parser.parse_args()
    
    # Run
    # analyzer = FactCheckerAndPerspectives(api_key=args.key)
    key = "AIzaSyBw7jgmMmbYy_4L0ErQqgtaozkbcii_DY8"
    analyzer = FactCheckerAndPerspectives(api_key=key)
    analyzer.run("./vidmeta.json", "./transcript.json", "op.json")
    # analyzer.run(args.video_file, args.transcript_file, args.output)