YouTube Video Analysis Chrome Extension – Development Spec
Overview

Build a Chrome Extension (Manifest V3) that:

Displays an overlay on top of YouTube videos.

Extracts the current YouTube video URL.

Sends the video URL to a backend API.

Backend downloads and processes the video.

Extension receives metric scores.

Displays those metric scores in the overlay UI.

Architecture
High-Level Flow

User opens a YouTube video page.

Content script injects overlay UI.

User clicks Analyze button.

Extension sends video URL to backend.

Backend:

Downloads video

Uploads to processing API

Retrieves analysis results

Backend returns JSON response with metrics.

Extension displays metrics in overlay.

Tech Stack
Extension

Manifest V3

React (Vite) OR Vanilla JS

Content Script

Background Service Worker

Axios (for API calls)

Backend (external service)

FastAPI (Python)

yt-dlp for video download

REST API returning JSON

Folder Structure
extension/
│
├── manifest.json
├── background.js
├── content.js
├── overlay/
│   ├── App.jsx
│   ├── index.jsx
│   └── styles.css
└── utils/
    └── api.js

Manifest Requirements (Manifest V3)

The extension must:

Run on: https://www.youtube.com/*

Use:

"content_scripts"

"background": { "service_worker": "background.js" }

"host_permissions" for backend API

Request permissions:

"activeTab"

"scripting"

"storage"

Content Script Responsibilities

File: content.js

Responsibilities

Detect YouTube video page.

Extract video URL:

window.location.href


Inject overlay container into DOM.

Render React overlay inside injected container.

Communicate with background script via:

chrome.runtime.sendMessage()

Overlay UI Requirements

The overlay must:

Be positioned absolute/fixed over video player

Not block video controls

Be draggable (optional enhancement)

Contain:

Analyze Button

Loading State

Metrics Display

Error Display

Example Metrics to Display
{
  "engagement_score": 0.82,
  "misinformation_score": 0.12,
  "quality_score": 0.91
}


Display each metric as:

Label

Numeric value

Progress bar

Background Service Worker

File: background.js

Responsibilities

Listen for messages from content script

Make API request to backend

Return response back to content script

Example message flow:

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "ANALYZE_VIDEO") {
    fetch("https://your-backend.com/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: request.videoUrl })
    })
    .then(res => res.json())
    .then(data => sendResponse({ success: true, data }))
    .catch(error => sendResponse({ success: false, error }));

    return true; // Required for async response
  }
});

Backend API Contract
Endpoint
POST /analyze

Request Body
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}

Response Body
{
  "engagement_score": 0.82,
  "misinformation_score": 0.12,
  "quality_score": 0.91,
  "summary": "Optional summary text"
}

Security Requirements

NEVER expose secret API keys in extension.

All sensitive API calls must go through backend.

Extension only communicates with backend.

Validate backend URL via environment variable.

UI Behavior
States

Idle

Loading

Success (show metrics)

Error (show retry option)

Error Handling

Handle network failure

Handle non-200 responses

Show user-friendly error messages

Development Steps

Create basic Manifest V3 extension.

Inject simple overlay div into YouTube.

Add button to trigger dummy API call.

Mock backend response first.

Replace mock with real backend.

Add styling and polish UI.

MVP Definition

MVP is complete when:

Overlay appears on YouTube videos.

Clicking Analyze sends URL to backend.

Backend response is received.

Metrics are rendered correctly.

Future Enhancements

Auto-trigger analysis when video loads

Caching results per video ID

Authentication

Draggable / collapsible UI

Dark mode styling

Store history in chrome.storage

Non-Goals

Do NOT download YouTube video inside extension.

Do NOT expose third-party API keys in client code.

Acceptance Criteria

Works on all YouTube watch pages

No console errors

Clean UI that does not interfere with video playback

Secure API communication

Handles async responses properly

If you'd like, I can now generate:

A starter Manifest V3 template

A React + Vite Chrome extension boilerplate

Or the FastAPI backend spec file