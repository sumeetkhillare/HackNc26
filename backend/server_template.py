#!/usr/bin/env python3
"""
Flask server for YouTube video analysis
This receives video URLs from the Chrome extension and returns analysis results
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_video():
    """
    Analyze a YouTube video and return metrics
    
    Expected request body:
    {
        "video_url": "https://www.youtube.com/watch?v=VIDEO_ID"
    }
    
    Returns:
    {
        "credibility_score": 0.75,
        "clickbait_score": 35,
        "sentiment_counts": { "positive": 55, "neutral": 13, "negative": 25 },
        "engagement_metrics": { "engagement_score": 92, "bot_activity_percentage": 2 },
        "community_insights": { 
            "dominant_topic": "...", 
            "controversy_level": "High" 
        },
        "summary_of_vibe": "...",
        "fact_checks": [...],
        "key_insights": [...],
        "alternative_perspectives": [...],
        "misinformation_score": 0.3,
        "quality_score": 0.9
    }
    """
    try:
        # Get video URL from request
        data = request.get_json()
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({'error': 'video_url is required'}), 400
        
        logger.info(f'Analyzing video: {video_url}')
        
        # ==================== YOUR ANALYSIS LOGIC HERE ====================
        # TODO: Replace this with your actual video analysis code
        # Example:
        # 1. Extract video ID from URL
        # 2. Download/fetch video comments
        # 3. Run sentiment analysis
        # 4. Run fact-checking
        # 5. Generate insights
        # etc.
        
        # For now, return mock data (replace this with your actual analysis)
        analysis_result = perform_video_analysis(video_url)
        
        # ==================== END ANALYSIS LOGIC ====================
        
        logger.info('Analysis complete')
        return jsonify(analysis_result), 200
        
    except Exception as e:
        logger.error(f'Error during analysis: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500


def perform_video_analysis(video_url):
    """
    Main analysis function - replace this with your actual implementation
    
    This should:
    1. Extract video ID from URL
    2. Fetch video metadata and comments
    3. Run your analysis pipeline
    4. Return results in the expected format
    """
    
    # TODO: Replace with your actual analysis code
    # For now, returning mock data as example
    
    return {
        "credibility_score": 0.45,
        "clickbait_score": 35,
        "sentiment_counts": {
            "positive": 55,
            "negative": 25,
            "neutral": 13
        },
        "engagement_metrics": {
            "engagement_score": 92,
            "bot_activity_percentage": 2
        },
        "community_insights": {
            "dominant_topic": "The dynamic between host Dylan and editor Alex, interspersed with reactions to the Epstein files and the school shooter's identity.",
            "controversy_level": "High"
        },
        "summary_of_vibe": "The audience is deeply invested in the channel's meta-humor, specifically praising the editor Alex and participating in 'Petition' memes. While the news content regarding Epstein and the school shooting sparks intense and often polarized debate, the core community remains highly supportive of the creator's personality and production style.",
        "fact_checks": [
            {
                "claim": "The Earth orbits around the Sun",
                "verdict": "true",
                "explanation": "This is scientifically verified and has been proven through astronomical observations."
            },
            {
                "claim": "5G networks cause health problems",
                "verdict": "false",
                "explanation": "Multiple scientific studies have found no evidence linking 5G to health issues."
            }
        ],
        "key_insights": [
            {"text": "Video demonstrates high production quality with professional editing", "severity": "positive"},
            {"text": "Content creator has established credibility in this topic area", "severity": "positive"},
            {"text": "Some claims lack supporting sources or citations", "severity": "caution"}
        ],
        "alternative_perspectives": [
            {
                "source": "BBC News",
                "type": "Mainstream Media Perspective",
                "description": "Covers similar topic with emphasis on expert analysis and peer-reviewed studies.",
                "url": "https://bbc.com/news/example"
            }
        ],
        "misinformation_score": 0.3,
        "quality_score": 0.9
    }


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    logger.info('Starting Flask server on http://localhost:5002')
    app.run(host='0.0.0.0', port=5002, debug=True)