// background.js - Service worker that handles 2 independent API calls to Flask backend
// Note: Comments analysis is now called directly from content.js, not through background.js

console.log('YouTube Video Analysis Extension - Background service worker loaded');

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Received request:', request.type);

    if (request.type === 'EXTRACT_VIDEO_INFO') {
        // API Call: Extract Video Info
        extractVideoInfo(request.url)
            .then(data => {
                console.log('Video extraction complete:', data);
                sendResponse({ success: true, data: data });
            })
            .catch(error => {
                console.error('Video extraction failed:', error);
                sendResponse({ success: false, error: error.message });
            });
        return true; // Keep message channel open
    }

    if (request.type === 'ANALYZE_COMMENTS') {
        // API Call: Comments Analysis
        analyzeComments(request.videoId)
            .then(data => {
                console.log('Comments analysis complete:', data);
                sendResponse({ success: true, data: data });
            })
            .catch(error => {
                console.error('Comments analysis failed:', error);
                sendResponse({ success: false, error: error.message });
            });
        return true;
    }

    if (request.type === 'ANALYZE_FACTS') {
        // API Call 1: Fact-Checking & Alternative Perspectives
        analyzeFactsAndPerspectives(request.videoId)
            .then(data => {
                console.log('Fact-check analysis complete:', data);
                sendResponse({ success: true, data: data });
            })
            .catch(error => {
                console.error('Fact-check analysis failed:', error);
                sendResponse({ success: false, error: error.message });
            });
        return true; // Keep message channel open
    }

    if (request.type === 'ANALYZE_QUALITY') {
        // API Call 2: Quality Metrics
        analyzeQuality(request.videoId)
            .then(data => {
                console.log('Quality analysis complete:', data);
                sendResponse({ success: true, data: data });
            })
            .catch(error => {
                console.error('Quality analysis failed:', error);
                sendResponse({ success: false, error: error.message });
            });
        return true;
    }
});

// API ENDPOINT 1: Fact-Checking & Alternative Perspectives (NOW USES video_id)
async function analyzeFactsAndPerspectives(videoId) {
    const FLASK_API_URL = 'http://localhost:5002/fact_check';

    try {
        console.log('Calling Facts API:', FLASK_API_URL, 'with video_id:', videoId);

        const response = await fetch(FLASK_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_id: videoId })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Facts API response:', data);

        // Expected format:
        // {
        //   fact_checks: [{claim, verdict, explanation}, ...],
        //   alternative_perspectives: [{source, type, description, url}, ...]
        // }

        return data;

    } catch (error) {
        console.error('Error calling Facts API:', error);
        if (error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to Flask server (Facts API). Make sure it is running on http://localhost:5002');
        }
        throw error;
    }
}

// API ENDPOINT 2: Quality Metrics (NOW USES video_id)
async function analyzeQuality(videoId) {
    const FLASK_API_URL = 'http://localhost:5002/analyze/quality';

    try {
        console.log('Calling Quality API:', FLASK_API_URL, 'with video_id:', videoId);

        const response = await fetch(FLASK_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_id: videoId })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Quality API response:', data);

        // Expected format:
        // {
        //   credibility_score: 0.75,
        //   clickbait_score: 35,
        //   key_insights: [{text, severity}, ...],
        //   misinformation_score: 0.3,
        //   quality_score: 0.9,
        //   tags: ["technology", "AI", "science"]
        // }

        return data;

    } catch (error) {
        console.error('Error calling Quality API:', error);
        if (error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to Flask server (Quality API). Make sure it is running on http://localhost:5002');
        }
        throw error;
    }
}

// API ENDPOINT 3: Extract Video Info
async function extractVideoInfo(url) {
    const FLASK_API_URL = 'http://localhost:5002/extract_video_info';

    try {
        console.log('Calling Extract Video Info API:', FLASK_API_URL, 'with url:', url);

        const response = await fetch(FLASK_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Extract Video Info API response:', data);

        return data;

    } catch (error) {
        console.error('Error calling Extract Video Info API:', error);
        if (error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to Flask server. Make sure it is running on http://localhost:5002');
        }
        throw error;
    }
}

// API ENDPOINT 4: Analyze Comments
async function analyzeComments(videoId) {
    const FLASK_API_URL = 'http://localhost:5002/analyze_comments';

    try {
        console.log('Calling Analyze Comments API:', FLASK_API_URL, 'with video_id:', videoId);

        const response = await fetch(FLASK_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_id: videoId })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Analyze Comments API response:', data);

        return data;

    } catch (error) {
        console.error('Error calling Analyze Comments API:', error);
        if (error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to Flask server. Make sure it is running on http://localhost:5002');
        }
        throw error;
    }
}