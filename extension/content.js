// content.js - injects a simple overlay and sends ANALYZE_VIDEO messages to background
(function () {
    // Only run on YouTube watch pages
    if (!window.location.href.includes('watch')) return;
    if (document.getElementById('yta-overlay-root')) return;

    const root = document.createElement('div');
    root.id = 'yta-overlay-root';
    root.style.position = 'absolute';
    root.style.top = '80px';
    root.style.right = '20px';
    root.style.zIndex = 999999;
    root.style.background = 'rgba(0,0,0,0.65)';
    root.style.color = '#fff';
    root.style.padding = '10px';
    root.style.borderRadius = '8px';
    root.style.maxWidth = '320px';
    root.innerHTML = `
    <div id="yta-ui">
      <button id="yta-analyze">Analyze</button>
      <div id="yta-status"></div>
      <div id="yta-metrics" style="margin-top:8px"></div>
    </div>
  `;

    requestAnimationFrame(() => {
        // NOW the element exists
        const container = root.querySelector("#yta-status");
        container.style.margin = "20px";
        container.style.width = "180px";
        container.style.height = "100px";
        console.log('Container for progress bar:', document.body.contains(container));
        console.log(ProgressBar);

        var bar = new ProgressBar.SemiCircle(container, {
            strokeWidth: 6,
            color: '#FFEA82',
            trailColor: '#eee',
            trailWidth: 1,
            easing: 'easeInOut',
            duration: 1400,
            svgStyle: null,
            text: {
                value: '',
                alignToBottom: false
            },
            from: { color: '#FFEA82' },
            to: { color: '#ED6A5A' },
            // Set default step function for all animate calls
            step: (state, bar) => {
                bar.path.setAttribute('stroke', state.color);
                var value = Math.round(bar.value() * 100);
                if (value === 0) {
                    bar.setText('');
                } else {
                    bar.setText(value);
                }

                bar.text.style.color = state.color;
            }
        });
        bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
        bar.text.style.fontSize = '2rem';

        bar.animate(1.0);  // Number from 0.0 to 1.0
    });

    document.body.appendChild(root);

    document.getElementById('yta-analyze').addEventListener('click', () => {
        try {
            const status = document.getElementById('yta-status');

            // Extract canonical watch link (youtube.com/watch?v=VIDEO_ID)
            var videoLink = window.location.href;
            try {
                const url = new URL(window.location.href);
                console.log('Extracted window location:', videoLink);

                const v = url.searchParams.get('v');
                if (v) {
                    videoLink = `https://www.youtube.com/watch?v=${v}`;
                }
            } catch (e) {
                // If URL parsing fails, fall back to full href
                videoLink = window.location.href;
            }

            // Log the extracted link for debugging
            console.log('Extracted video link for analysis:', videoLink);

            status.textContent = 'Sending...';

            // Send message to extension background/service worker in a runtime-compatible way
            (function sendRuntimeMessage(message, callback) {
                try {
                    // Prefer chrome.runtime (Chromium-based browsers)
                    if (typeof chrome !== 'undefined' && chrome.runtime && typeof chrome.runtime.sendMessage === 'function') {
                        try {
                            // Some implementations accept a callback, others return a Promise.
                            const result = chrome.runtime.sendMessage(message, callback);
                            // If a Promise is returned and no callback was provided, attach handlers to avoid unhandled rejection
                            if (result && typeof result.then === 'function' && !callback) {
                                result.then(() => { }).catch(err => console.error('Background sendMessage promise rejected:', err));
                            }
                            return;
                        } catch (e) {
                            // fallback below
                            console.warn('chrome.runtime.sendMessage threw, trying browser.runtime if available', e);
                        }
                    }

                    // Support Firefox-style browser.runtime that returns a Promise
                    if (typeof browser !== 'undefined' && browser.runtime && typeof browser.runtime.sendMessage === 'function') {
                        const p = browser.runtime.sendMessage(message);
                        if (callback && p && typeof p.then === 'function') {
                            p.then(callback).catch(err => {
                                console.error('browser.runtime.sendMessage rejected:', err);
                                callback(null);
                            });
                        }
                        return;
                    }

                    console.error('No extension runtime available to send message');
                    if (typeof callback === 'function') callback(null);
                } catch (err) {
                    console.error('sendRuntimeMessage error:', err);
                    if (typeof callback === 'function') callback(null);
                }
            })({ type: 'ANALYZE_VIDEO', videoUrl: videoLink }, (response) => {
                try {
                    if (!response) {
                        status.textContent = 'No response from background.';
                        return;
                    }
                    if (response.success) {
                        status.textContent = 'Analysis complete';
                        const metrics = response.data;
                        const metricsEl = document.getElementById('yta-metrics');
                        metricsEl.innerHTML = '';
                        ['engagement_score', 'misinformation_score', 'quality_score'].forEach(k => {
                            if (metrics[k] !== undefined) {
                                metricsEl.innerHTML += `<div style="margin-bottom:6px">
                  <div style="font-size:12px">${k.replace('_', ' ')}: ${metrics[k]}</div>
                  <div style="background:#444;height:8px;border-radius:4px">
                    <div style="width:${Math.round(metrics[k] * 100)}%;height:8px;background:#4caf50;border-radius:4px"></div>
                  </div>
                </div>`;
                            }
                        });
                    } else {
                        status.textContent = 'Error: ' + (response.error || 'Unknown');
                    }
                } catch (innerErr) {
                    console.error('Error handling analyze response:', innerErr, innerErr.stack);
                    status.textContent = 'Error processing response';
                }
            });
        } catch (err) {
            console.error('Analyze click handler error:', err, err && err.stack);
        }
    });
})();
