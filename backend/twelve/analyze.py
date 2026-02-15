"""
TwelveLabs Video Analysis Script
Reads video_extract.json and analyzes video
Outputs: result.json
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIGURATION ==========
API_KEY = os.getenv("TWELVELABS_API_KEY")
BASE_URL = "https://api.twelvelabs.io/v1.3"

# ========== VALIDATION ==========
if not API_KEY:
    print("❌ Error: TWELVELABS_API_KEY not found in .env file!")
    exit(1)

# ========== LOAD VIDEO EXTRACT DATA ==========
if not os.path.exists('video_extract.json'):
    print("❌ Error: video_extract.json not found!")
    print("Please run upload.py first.")
    exit(1)

print("📖 Loading video extract data...")
with open('video_extract.json', 'r', encoding='utf-8') as f:
    video_extract = json.load(f)

video_id = video_extract.get('video_id')
VIDEO_TITLE = video_extract.get('video_title')
THUMBNAIL_TEXT = video_extract.get('thumbnail_data_in_text_form')

if not video_id:
    print("❌ Error: video_id not found in video_extract.json!")
    print("Please run upload.py first to get video_id.")
    exit(1)


# ========== GET ADDITIONAL CONTEXT ==========
VIDEO_DESCRIPTION = video_extract.get('video_description', '')
VIDEO_TAGS = video_extract.get('tags', [])

print(f"📝 Title: {VIDEO_TITLE}")
print(f"📄 Description: {VIDEO_DESCRIPTION[:100]}..." if VIDEO_DESCRIPTION else "None")
print(f"🏷️  Tags: {', '.join(VIDEO_TAGS[:5])}..." if VIDEO_TAGS else "None")
print(f"🖼️  Thumbnail: {THUMBNAIL_TEXT[:50]}..." if THUMBNAIL_TEXT else "None")

# ========== CUSTOM ANALYSIS PROMPT ==========
ANALYSIS_PROMPT = f"""
You are an expert video content analyzer specializing in detecting misinformation, clickbait, and assessing credibility.

YOUTUBE METADATA PROVIDED:
- Title: "{VIDEO_TITLE}"
- Description: "{VIDEO_DESCRIPTION}"
- Tags: {', '.join(VIDEO_TAGS) if VIDEO_TAGS else 'None'}
- Thumbnail Visual Description: "{THUMBNAIL_TEXT}"

YOUR TASK:
Analyze the actual video content and compare it against the provided metadata (title, description, tags, thumbnail).

Return a JSON response with EXACTLY these fields:

{{
  "summary": "A 2-sentence summary of what the video actually contains and discusses",
  "misinformation_score": <integer 0-100, where 0=completely factual, 100=completely false>,
  "credibility_score": <integer 0-100, where 0=not credible at all, 100=highly credible>,
  "content_tags": ["category1", "category2", "category3"],
  "clickbait_score": <integer 0-100, where 0=not clickbait at all, 100=extreme clickbait>,
  "key_insights": [
    {{"text": "insight text here", "severity": "positive"}},
    {{"text": "another insight", "severity": "caution"}},
    {{"text": "final insight", "severity": "negative"}}
  ]
}}

SCORING GUIDELINES:
- misinformation_score: Rate how much false/misleading information is present. Consider if claims match reality.
- credibility_score: Rate based on source quality, fact accuracy, presentation style, bias.
- content_tags: Choose 2-4 from: ["News", "Politics", "Health", "Technology", "Science", "Sports", "Entertainment", "Education", "Finance", "Weather", "Opinion", "Tutorial", "Review", "Documentary", "Advertisement"]
- clickbait_score: Rate the level of sensationalism and misleading elements (0=accurate title/thumbnail, 100=extremely misleading)
- key_insights: List 2-4 key observations about the video. Each insight must have:
  - "text": Brief insight statement
  - "severity": One of ["positive", "negative", "caution"]

IMPORTANT: Return ONLY the JSON object, no additional text, explanations, or markdown formatting.
"""


# ========== ANALYZE VIDEO ==========
print("\n🔍 Analyzing video...")

analyze_url = f"{BASE_URL}/analyze"
analyze_headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}
analyze_data = {
    "video_id": video_id,
    "prompt": ANALYSIS_PROMPT,
    "temperature": 0.2,
    "stream": False
}

response = requests.post(analyze_url, headers=analyze_headers, json=analyze_data)

if response.status_code != 200:
    print(f"❌ Analysis failed: {response.status_code}")
    print(response.text)
    exit(1)

result = response.json()
summary = result.get('data')

# ========== DISPLAY RESULTS ==========
print("\n" + "="*60)
print("📝 ANALYSIS RESULTS")
print("="*60)
print(summary)
print("="*60)

# ========== SAVE TO result.json ==========
# ========== PARSE AND SAVE TO result.json ==========
print("\n💾 Parsing and saving analysis results...")

# Try to parse the JSON response
try:
    # Clean the response in case there's markdown formatting
    cleaned_summary = summary.strip()
    if cleaned_summary.startswith("```json"):
        cleaned_summary = cleaned_summary[7:]
    if cleaned_summary.endswith("```"):
        cleaned_summary = cleaned_summary[:-3]
    cleaned_summary = cleaned_summary.strip()
    
    parsed_analysis = json.loads(cleaned_summary)
    
    # Validate required fields
    required_fields = ["summary", "misinformation_score", "credibility_score", "content_tags", "clickbait_score", "key_insights"]
    # required_fields = ["summary", "misinformation", "overall_credibility", "content_tags", "clickbait", "key_claims"]
    missing_fields = [field for field in required_fields if field not in parsed_analysis]
    
    if missing_fields:
        print(f"⚠️  Warning: Missing fields in response: {missing_fields}")
        parsed_analysis['_parsing_warning'] = f"Missing fields: {missing_fields}"
    
except json.JSONDecodeError as e:
    print(f"⚠️  Failed to parse JSON response: {e}")
    print("Raw response will be saved in 'raw_analysis' field")
    parsed_analysis = {
        "summary": "[Parsing failed - see raw_analysis]",
        "misinformation_score": -1,
        "credibility_score": -1,
        "content_tags": [],
        "clickbait_score": -1,
        "key_insights": [],
        "raw_analysis": summary,
        "_parsing_error": str(e)
    }

analysis_results = {
    "video_id": video_id,
    "analysis": parsed_analysis
}

with open('result.json', 'w', encoding='utf-8') as f:
    json.dump(analysis_results, f, indent=2, ensure_ascii=False)

print(f"✅ Results saved to result.json")

# ========== DISPLAY FORMATTED RESULTS ==========
print("\n" + "="*60)
print("📊 ANALYSIS RESULTS")
print("="*60)
if isinstance(parsed_analysis, dict) and 'summary' in parsed_analysis:
    print(f"\n📝 Summary:")
    print(f"   {parsed_analysis.get('summary', 'N/A')}")
    print(f"\n⚠️  Misinformation Score: {parsed_analysis.get('misinformation_score', 'N/A')}/100")
    print(f"✅ Credibility Score: {parsed_analysis.get('credibility_score', 'N/A')}/100")
    print(f"🏷️  Content Tags: {', '.join(parsed_analysis.get('content_tags', []))}")
    print(f"🎣 Clickbait Score: {parsed_analysis.get('clickbait_score', 'N/A')}/100")
    print(f"\n💡 Key Insights:")
    for insight in parsed_analysis.get('key_insights', []):
        severity_icon = {"positive": "✅", "negative": "❌", "caution": "⚠️"}.get(insight.get('severity', ''), "•")
        print(f"   {severity_icon} {insight.get('text', 'N/A')} [{insight.get('severity', 'N/A')}]")
else:
    print(summary)
print("="*60)

print(f"\n🎉 Done!")