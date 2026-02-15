#!/usr/bin/env python3
"""
Flask server with 3 independent API endpoints for YouTube video analysis
Each endpoint can be called independently and returns specific data
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time

app = Flask(__name__)

# Configure CORS properly - ONLY ONE CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Allow all origins (or specify ["https://www.youtube.com"] for specific)
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== ENDPOINT 0: VIDEO INFO EXTRACTION ====================
@app.route('/extract_video_info', methods=['POST', 'OPTIONS'])
def extract_video_info():
    """
    Extract basic video information
    
    Request: {"url": "https://www.youtube.com/watch?v=..."}
    
    Response: {
        "status": "success",
        "video_id": "..."
    }
    """
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 204
        
    try:
        data = request.get_json()
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({'status': 'error', 'error': 'url is required'}), 400
        
        # Extract video ID from URL
        video_id = None
        if 'v=' in video_url:
            video_id = video_url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in video_url:
            video_id = video_url.split('youtu.be/')[1].split('?')[0]
        
        if not video_id:
            return jsonify({'status': 'error', 'error': 'Could not extract video ID'}), 400
        
        logger.info(f'[EXTRACT] Video ID: {video_id}')
        
        return jsonify({
            'status': 'success',
            'video_id': video_id
        }), 200
        
    except Exception as e:
        logger.error(f'[EXTRACT] Error: {str(e)}', exc_info=True)
        return jsonify({'status': 'error', 'error': str(e)}), 500


# ==================== ENDPOINT 1: COMMENTS ANALYSIS ====================
@app.route('/analyze_comments', methods=['POST', 'OPTIONS'])
def analyze_comments():
    """
    Analyze video comments for sentiment, engagement, and community insights
    
    Request: {"video_id": "..."}
    
    Response: {
        "analysis": {
            "sentiment_counts": {"positive": 55, "negative": 25, "neutral": 13},
            "engagement_metrics": {"engagement_score": 92, "bot_activity_percentage": 2},
            "community_insights": {"dominant_topic": "...", "controversy_level": "High"},
            "summary_of_vibe": "..."
        }
    }
    """
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 204
        
    try:
        time.sleep(2)  # Simulate processing
        data = request.get_json()
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({'error': 'video_id is required'}), 400
        
        logger.info(f'[COMMENTS] Analyzing: {video_id}')
        
        # TODO: Replace with your actual comment analysis code
        result = {
            "analysis": {
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
                    "dominant_topic": "Main discussion topic from comments",
                    "controversy_level": "High"
                },
                "summary_of_vibe": "Community sentiment summary..."
            }
        }
        
        logger.info('[COMMENTS] Analysis complete')
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'[COMMENTS] Error: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINT 2: FACT-CHECKING & PERSPECTIVES ====================
@app.route('/analyze/facts', methods=['POST', 'OPTIONS'])
def analyze_facts():
    """
    Fact-check video claims and find alternative perspectives
    
    Request: {"video_id": "..."}
    
    Response: {
        "analysis": {
            "fact_checks": [...],
            "alternative_perspectives": [...],
            "bias_distribution": {"left_count": 3, "center_count": 18, "right_count": 2}
        }
    }
    """
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 204
        
    try:
        time.sleep(3)  # Simulate processing
        data = request.get_json()
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({'error': 'video_id is required'}), 400
        
        logger.info(f'[FACTS] Analyzing: {video_id}')
        
        # TODO: Replace with your fact-checking code
        result = {
            "analysis": {
                "fact_checks": [
                    {
                        "claim": "Example claim from video",
                        "verdict": "true",
                        "explanation": "Verified through sources..."
                    },
                    {
                        "claim": "Another claim",
                        "verdict": "false",
                        "explanation": "Contradicted by evidence..."
                    }
                ],
                "alternative_perspectives": [
                    {
                        "source": "BBC News",
                        "type": "Mainstream Media",
                        "description": "Alternative coverage...",
                        "url": "https://bbc.com/news/example"
                    },
                    {
                        "source": "The Guardian",
                        "type": "Left-Center",
                        "description": "Another perspective...",
                        "url": "https://theguardian.com/example"
                    }
                ],
                "bias_distribution": {
                    "left_count": 3,
                    "center_count": 18,
                    "right_count": 2
                }
            }
        }
        
        logger.info('[FACTS] Analysis complete')
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'[FACTS] Error: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINT 3: QUALITY METRICS ====================
@app.route('/analyze/quality', methods=['POST', 'OPTIONS'])
def analyze_quality():
    """
    Calculate video quality metrics
    
    Request: {"video_id": "..."}
    
    Response: {
        "analysis": {
            "credibility_score": 0.75,
            "clickbait_score": 35,
            "key_insights": [...],
            "misinformation_score": 0.3,
            "quality_score": 0.9,
            "content_tags": [...],
            "summary": "..."
        }
    }
    """
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 204
        
    try:
        time.sleep(2)  # Simulate processing
        data = request.get_json()
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({'error': 'video_id is required'}), 400
        
        logger.info(f'[QUALITY] Analyzing: {video_id}')
        
        # TODO: Replace with your quality analysis code
        result = {
            "analysis": {
                "credibility_score": 0.75,
                "clickbait_score": 35,
                "key_insights": [
                    {"text": "High production quality", "severity": "positive"},
                    {"text": "Some claims need verification", "severity": "caution"},
                    {"text": "Well-researched content", "severity": "positive"}
                ],
                "misinformation_score": 0.3,
                "quality_score": 0.9,
                "content_tags": ["technology", "computer science", "artificial intelligence"],
                "summary": "This video provides a comprehensive overview of artificial intelligence with high production quality and well-researched content."
            }
        }
        
        logger.info('[QUALITY] Analysis complete')
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'[QUALITY] Error: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 500


# ==================== HEALTH CHECK ====================
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'endpoints': [
            '/extract_video_info',
            '/analyze_comments',
            '/analyze/facts',
            '/analyze/quality'
        ]
    }), 200


if __name__ == '__main__':
    logger.info('='*60)
    logger.info('Starting Flask server with 4 endpoints:')
    logger.info('  0. POST /extract_video_info - Extract video ID')
    logger.info('  1. POST /analyze_comments - Comment sentiment & engagement')
    logger.info('  2. POST /analyze/facts - Fact-checking & perspectives')
    logger.info('  3. POST /analyze/quality - Quality metrics & insights')
    logger.info('='*60)
    logger.info('Server running on http://localhost:5002')
    
    app.run(host='0.0.0.0', port=5002, debug=True, threaded=True)