YouTube Video Analysis Chrome Extension - scaffold

This folder contains a starter scaffold for a Chrome Manifest V3 extension that injects an overlay on YouTube watch pages and sends the video URL to a backend for analysis.

Files:
- `manifest.json` - MV3 manifest.
- `background.js` - service worker that forwards analysis requests to backend.
- `content.js` - injects a simple overlay UI and wires the Analyze button to the background.
- `overlay/` - React-based overlay source stubs (requires bundling with Vite or similar to use in production).
- `utils/api.js` - helper wrapper for backend calls.

Load the extension for development:
1. Build the overlay bundle if you use React/Vite (not included here). For quick testing, `content.js` provides a DOM-based UI.
2. Open Chrome -> Extensions -> Load unpacked -> select this `extension/` folder.
3. Open a YouTube watch page and click Analyze (the button will call the placeholder backend URL in `background.js`).

Security note: Do NOT put secret API keys in client-side code. Configure the backend URL and secrets on your server.
