// background.js - Service worker that handles API calls to Flask backend

console.log('YouTube Video Analysis Extension - Background service worker loaded');

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'ANALYZE_VIDEO') {
        console.log('Received ANALYZE_VIDEO request for:', request.videoUrl);
        
        // Call Flask backend
        analyzeVideo(request.videoUrl)
            .then(data => {
                console.log('Analysis complete:', data);
                sendResponse({
                    success: true,
                    data: data
                });
            })
            .catch(error => {
                console.error('Analysis failed:', error);
                sendResponse({
                    success: false,
                    error: error.message || 'Analysis failed'
                });
            });
        
        // Return true to indicate we'll send response asynchronously
        return true;
    }
});

// Function to call Flask backend
async function analyzeVideo(videoUrl) {
    // IMPORTANT: Change this to your Flask server URL
    const FLASK_API_URL = 'http://localhost:5002/analyze';
    
    try {
        console.log('Calling Flask API:', FLASK_API_URL);
        console.log('Video URL:', videoUrl);
        
        const response = await fetch(FLASK_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                video_url: videoUrl
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Flask server error response:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Flask response received:', data);
        
        // Return the analysis data
        // Expected format: { credibility_score, clickbait_score, sentiment_counts, etc. }
        return data;
        
    } catch (error) {
        console.error('Error calling Flask API:', error);
        
        // Provide helpful error messages
        if (error.message.includes('Failed to fetch')) {
            throw new Error('Cannot connect to Flask server. Make sure it is running on http://localhost:5002');
        }
        
        throw error;
    }
}