// background.js - MV3 service worker

const BACKEND_URL = "https://your-backend.com/analyze"; // Replace with your backend URL

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "ANALYZE_VIDEO") {
        sendResponse({ success: true, data: "Dummy" });
        // fetch(BACKEND_URL, {
        //     method: "POST",
        //     headers: { "Content-Type": "application/json" },
        //     body: JSON.stringify({ url: request.videoUrl })
        // })
        //     .then(res => res.json())
        //     .then(data => sendResponse({ success: true, data }))
        //     .catch(error => sendResponse({ success: false, error: error.message }));

        // Keep the message channel open for async response
        return true;
    }
});
