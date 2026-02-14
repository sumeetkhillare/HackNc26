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
      <div id="yta-status" style="margin-top:8px;font-size:12px"></div>
      <div id="yta-metrics" style="margin-top:8px"></div>
    </div>
  `;

    document.body.appendChild(root);

    document.getElementById('yta-analyze').addEventListener('click', () => {
        const status = document.getElementById('yta-status');
        status.textContent = 'Sending...';

        chrome.runtime.sendMessage({ type: 'ANALYZE_VIDEO', videoUrl: window.location.href }, (response) => {
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
        });
    });
})();
