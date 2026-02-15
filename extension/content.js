// content.js - injects a simple overlay and sends ANALYZE_VIDEO messages to background
(function () {
  // Only run on YouTube watch pages
  if (!window.location.href.includes('watch')) return;
  if (document.getElementById('yta-overlay-root')) return;

  // Add custom scrollbar styles
  const styleSheet = document.createElement('style');
  styleSheet.textContent = `
        #yta-content::-webkit-scrollbar {
            width: 8px;
        }
        #yta-content::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
        }
        #yta-content::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.3);
            border-radius: 4px;
        }
        #yta-content::-webkit-scrollbar-thumb:hover {
            background: rgba(255,255,255,0.5);
        }
        
        /* Clear button styles */
        #yta-clear {
            display: none;
            width: 100%;
            padding: 10px;
            background: #f44336;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: bold;
            margin-top: 8px;
            transition: background 0.2s ease;
        }
        
        #yta-clear:hover {
            background: #d32f2f;
        }
        
        #yta-clear:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            background: #f44336;
        }
    `;
  document.head.appendChild(styleSheet);

  const root = document.createElement('div');
  root.id = 'yta-overlay-root';
  root.style.position = 'fixed';
  root.style.top = '80px';
  root.style.right = '20px';
  root.style.zIndex = 999999;
  root.style.background = 'rgba(0,0,0,0.85)';
  root.style.color = '#fff';
  root.style.padding = '16px';
  root.style.borderRadius = '12px';
  root.style.width = '380px';  // Default width
  root.style.maxHeight = 'calc(100vh - 100px)';
  root.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
  root.style.fontFamily = 'Arial, sans-serif';
  root.style.transition = 'all 0.3s ease';
  root.style.display = 'flex';
  root.style.flexDirection = 'column';
  root.style.resize = 'horizontal';  // Allow horizontal resize
  root.style.overflow = 'hidden';  // Needed for resize
  root.style.minWidth = '320px';  // Minimum width
  root.style.maxWidth = '800px';  // Maximum width
  root.innerHTML = `
    <div id="yta-ui" style="display: flex; flex-direction: column; height: 100%; min-height: 0;">
      <!-- Header with Width Controls and Minimize Button -->
      <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        flex-shrink: 0;
      ">
        <span style="font-weight: bold; font-size: 16px;">Video Analysis</span>
        <div style="display: flex; gap: 6px;">
          <button id="yta-decrease" style="
            background: rgba(255,255,255,0.1);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
            font-weight: bold;
          " title="Decrease Width">◄</button>
          <button id="yta-increase" style="
            background: rgba(255,255,255,0.1);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
            font-weight: bold;
          " title="Increase Width">►</button>
          <button id="yta-minimize" style="
            background: rgba(255,255,255,0.1);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 18px;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
          " title="Minimize">−</button>
        </div>
      </div>

      <!-- Scrollable Content Area -->
      <div id="yta-content" style="
        overflow-y: auto;
        overflow-x: hidden;
        flex: 1;
        min-height: 0;
        padding-right: 4px;
        scrollbar-width: thin;
        scrollbar-color: rgba(255,255,255,0.3) rgba(255,255,255,0.1);
      ">
        <button id="yta-analyze" style="
          width: 100%;
          padding: 12px;
          background: #065fd4;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: bold;
          margin-bottom: 16px;
        ">Analyze Video</button>
        
        <!-- Clear Analysis Button - Hidden by default -->
        <button id="yta-clear">Clear Analysis</button>
        
        <!-- Tags Section - MOVED TO TOP -->
        <div id="tags-section" style="margin-top: 16px; display: none;">
          <div style="
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
          ">Video Tags</div>
          <div id="tags-content">
            <!-- Will be populated dynamically -->
          </div>
        </div>
        
        <!-- Summary Section - NEW, RIGHT BELOW TAGS -->
        <div id="summary-section" style="margin-top: 16px; display: none;">
          <div style="
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
          ">Video Summary</div>
          <div id="summary-content">
            <!-- Will be populated dynamically -->
          </div>
        </div>
        
        <!-- Credibility Score Section - Hidden by default -->
        <div id="credibility-score-section" style="display: none;">
          <div style="
            font-weight: bold;
            font-size: 14px;
            margin-top: 14px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
          ">Credibility Score</div>
          <div id="credibility-score"></div>
        </div>
        
        <!-- Clickbait Meter Section -->
        <div id="clickbait-meter-section" style="margin-top: 16px; display: none;">
          <div style="
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
          ">Clickbait Meter</div>
          <div id="clickbait-meter-container" style="
            background: rgba(255,255,255,0.05);
            padding: 16px;
            border-radius: 6px;
          ">
            <!-- Clickbait Score Display -->
            <div style="text-align: center; margin-bottom: 12px;">
              <div id="clickbait-score-value" style="
                font-size: 36px;
                font-weight: bold;
                color: #4caf50;
              ">0<span style="font-size: 20px; opacity: 0.7;">/100</span></div>
              <div id="clickbait-label" style="font-size: 11px; opacity: 0.7; margin-top: 4px;">Low Clickbait</div>
            </div>
            
            <!-- Visual Progress Bar -->
            <div style="
              position: relative;
              width: 100%;
              height: 24px;
              background: linear-gradient(to right, #4caf50 0%, #4caf50 33%, #ff9800 33%, #ff9800 66%, #f44336 66%, #f44336 100%);
              border-radius: 12px;
              overflow: hidden;
              margin-bottom: 8px;
            ">
              <div id="clickbait-indicator" style="
                position: absolute;
                top: 50%;
                left: 0%;
                transform: translate(-50%, -50%);
                width: 12px;
                height: 12px;
                background: white;
                border: 2px solid #000;
                border-radius: 50%;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                z-index: 1;
              "></div>
            </div>
            
            <!-- Labels -->
            <div style="
              display: flex;
              justify-content: space-between;
              font-size: 10px;
              opacity: 0.7;
            ">
              <span>Low</span>
              <span>Medium</span>
              <span>High</span>
            </div>
          </div>
        </div>
        
        <!-- Comments Analysis Section -->
        <div id="comments-analysis-section" style="margin-top: 16px; display: none;">
          <div style="
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
          ">Comments Analysis</div>
          <div id="comments-analysis-container" style="
            background: rgba(255,255,255,0.05);
            padding: 16px;
            border-radius: 6px;
          ">
            <!-- Sentiment Distribution (will be populated dynamically) -->
            <div id="comments-analysis-content"></div>
          </div>
        </div>
        
        <!-- Fact-Check Section -->
        <div id="fact-check-section" style="margin-top: 16px; display: none;">
          <div style="
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
          ">Fact-Check Results</div>
          <div id="fact-check-results">
            <!-- Will be populated dynamically -->
          </div>
        </div>
        
        <!-- Key Insights Section -->
        <div id="key-insights-section" style="margin-top: 16px; display: none;">
          <div style="
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
          ">Key Insights</div>
          <div id="key-insights-results">
            <!-- Will be populated dynamically -->
          </div>
        </div>
        
        <!-- Alternative Perspectives Section -->
        <div id="alternative-perspectives-section" style="margin-top: 16px; display: none;">
          <div style="
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
          ">Alternative Perspectives</div>
          <div id="alternative-perspectives-results">
            <!-- Will be populated dynamically -->
          </div>
        </div>

        <!-- Bias Distribution Section -->
        <div id="bias-distribution-section" style="margin-top: 16px; display: none;">
          <div style="
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
          ">Source Bias Distribution</div>
          <div id="bias-distribution-content">
            <!-- Will be populated dynamically -->
          </div>
        </div>
        
        <!-- Community Insights Section -->
        <div id="community-insights-section" style="margin-top: 16px; display: none;">
          <div style="
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
          ">Community Insights</div>
          <div id="community-insights-content">
            <!-- Will be populated dynamically -->
          </div>
        </div>
        
        <!-- Community Vibe Section -->
        <div id="community-vibe-section" style="margin-top: 16px; display: none;">
          <div style="
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
          ">Community Vibe</div>
          <div id="community-vibe-content">
            <!-- Will be populated dynamically -->
          </div>
        </div>
        
        <div id="yta-metrics" style="margin-top:16px; padding-bottom: 16px;"></div>
      </div>
    </div>
  `;

  requestAnimationFrame(() => {
    const container = root.querySelector("#credibility-score");
    container.style.margin = "20px auto";
    container.style.width = "180px";
    container.style.height = "100px";

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
      from: { color: '#4caf50' },
      to: { color: '#ED6A5A' },
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

    window.ytaProgressBar = bar;
    bar.animate(0.0);
  });

  document.body.appendChild(root);

  // Prevent scroll propagation to YouTube page when scrolling inside the overlay
  const contentDiv = document.getElementById('yta-content');
  contentDiv.addEventListener('wheel', (e) => {
    const isScrollable = contentDiv.scrollHeight > contentDiv.clientHeight;
    const isAtTop = contentDiv.scrollTop === 0;
    const isAtBottom = contentDiv.scrollTop + contentDiv.clientHeight >= contentDiv.scrollHeight - 1;

    if (isScrollable) {
      if ((e.deltaY < 0 && !isAtTop) || (e.deltaY > 0 && !isAtBottom)) {
        e.stopPropagation();
      }
    }
  }, { passive: true });

  // Width control functionality
  const increaseBtn = document.getElementById('yta-increase');
  const decreaseBtn = document.getElementById('yta-decrease');

  const STEP_SIZE = 200;
  const MIN_WIDTH = 320;

  function getMaxWidth() {
    return window.innerWidth - 40;
  }

  function updateButtonStates() {
    const currentWidth = parseInt(root.style.width) || 380;
    const maxWidth = getMaxWidth();

    if (currentWidth <= MIN_WIDTH) {
      decreaseBtn.disabled = true;
      decreaseBtn.style.opacity = '0.3';
      decreaseBtn.style.cursor = 'not-allowed';
    } else {
      decreaseBtn.disabled = false;
      decreaseBtn.style.opacity = '1';
      decreaseBtn.style.cursor = 'pointer';
    }

    if (currentWidth >= maxWidth) {
      increaseBtn.disabled = true;
      increaseBtn.style.opacity = '0.3';
      increaseBtn.style.cursor = 'not-allowed';
    } else {
      increaseBtn.disabled = false;
      increaseBtn.style.opacity = '1';
      increaseBtn.style.cursor = 'pointer';
    }
  }

  function setWidth(newWidth) {
    const maxWidth = getMaxWidth();
    const finalWidth = Math.min(Math.max(newWidth, MIN_WIDTH), maxWidth);
    root.style.width = finalWidth + 'px';
    updateButtonStates();
  }

  increaseBtn.addEventListener('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    if (this.disabled) return;
    const currentWidth = parseInt(root.style.width) || 380;
    const newWidth = currentWidth + STEP_SIZE;
    setWidth(newWidth);
  });

  decreaseBtn.addEventListener('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    if (this.disabled) return;
    const currentWidth = parseInt(root.style.width) || 380;
    const newWidth = currentWidth - STEP_SIZE;
    setWidth(newWidth);
  });

  setWidth(380);

  increaseBtn.addEventListener('mouseenter', function () {
    if (!this.disabled) this.style.background = 'rgba(255,255,255,0.2)';
  });
  increaseBtn.addEventListener('mouseleave', function () {
    this.style.background = 'rgba(255,255,255,0.1)';
  });

  decreaseBtn.addEventListener('mouseenter', function () {
    if (!this.disabled) this.style.background = 'rgba(255,255,255,0.2)';
  });
  decreaseBtn.addEventListener('mouseleave', function () {
    this.style.background = 'rgba(255,255,255,0.1)';
  });

  window.addEventListener('resize', function () {
    const currentWidth = parseInt(root.style.width) || 380;
    setWidth(currentWidth);
  });

  // Minimize/Maximize functionality
  let isMinimized = false;
  let previousWidth = 380;
  const minimizeBtn = document.getElementById('yta-minimize');

  minimizeBtn.addEventListener('click', () => {
    isMinimized = !isMinimized;

    if (isMinimized) {
      previousWidth = parseInt(root.style.width) || 380;
      contentDiv.style.display = 'none';
      minimizeBtn.textContent = '+';
      minimizeBtn.title = 'Expand';
      root.style.width = '200px';
      root.style.padding = '12px 16px';
    } else {
      contentDiv.style.display = 'block';
      minimizeBtn.textContent = '−';
      minimizeBtn.title = 'Minimize';
      root.style.padding = '16px';
      setWidth(previousWidth);
    }
  });

  minimizeBtn.addEventListener('mouseenter', () => {
    minimizeBtn.style.background = 'rgba(255,255,255,0.2)';
  });
  minimizeBtn.addEventListener('mouseleave', () => {
    minimizeBtn.style.background = 'rgba(255,255,255,0.1)';
  });

  const analyzeBtn = document.getElementById('yta-analyze');
  analyzeBtn.addEventListener('mouseenter', () => {
    analyzeBtn.style.background = '#0551c5';
  });
  analyzeBtn.addEventListener('mouseleave', () => {
    analyzeBtn.style.background = '#065fd4';
  });

  document.getElementById('yta-analyze').addEventListener('click', () => {
    try {
      const metricsEl = document.getElementById('yta-metrics');
      const analyzeBtn = document.getElementById('yta-analyze');
      const clearBtn = document.getElementById('yta-clear');

      clearBtn.style.display = 'none';
      analyzeBtn.disabled = true;
      analyzeBtn.style.opacity = '0.6';
      analyzeBtn.style.cursor = 'not-allowed';
      analyzeBtn.textContent = 'Analyzing...';

      metricsEl.innerHTML = `
                <div style="text-align:center;padding:20px;">
                    <div style="
                        display: inline-block;
                        width: 40px;
                        height: 40px;
                        border: 4px solid rgba(255,255,255,0.1);
                        border-top-color: #065fd4;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                    "></div>
                    <div style="
                        margin-top: 12px;
                        font-size: 12px;
                        opacity: 0.7;
                    ">Extracting video data...</div>
                </div>
                <style>
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                </style>
            `;

      var videoLink = window.location.href;
      try {
        const url = new URL(window.location.href);
        const v = url.searchParams.get('v');
        if (v) {
          videoLink = `https://www.youtube.com/watch?v=${v}`;
        }
      } catch (e) {
        videoLink = window.location.href;
      }

      console.log('Extracted video link for analysis:', videoLink);

      extractVideoInfo(videoLink, (extractionResponse) => {
        if (!extractionResponse || !extractionResponse.success) {
          const errorMsg = extractionResponse?.error || 'Video extraction failed';
          console.error('Video extraction error:', errorMsg);

          metricsEl.innerHTML = `
                        <div style="
                            text-align: center;
                            padding: 20px;
                            background: rgba(244, 67, 54, 0.1);
                            border: 1px solid #f44336;
                            border-radius: 6px;
                        ">
                            <div style="color: #f44336; font-size: 14px; font-weight: bold; margin-bottom: 8px;">
                                ✗ Extraction Failed
                            </div>
                            <div style="font-size: 12px; opacity: 0.8;">
                                ${escapeHtml(errorMsg)}
                            </div>
                        </div>
                    `;

          analyzeBtn.disabled = false;
          analyzeBtn.style.opacity = '1';
          analyzeBtn.style.cursor = 'pointer';
          analyzeBtn.textContent = 'Analyze Video';
          return;
        }

        const videoId = extractionResponse.data.video_id;
        console.log('Video extraction successful. Video ID:', videoId);

        let completedCalls = 0;
        let totalCalls = 3;

        function updateLoadingMessage(message) {
          const loadingDiv = metricsEl.querySelector('div[style*="margin-top: 12px"]');
          if (loadingDiv) {
            loadingDiv.textContent = message;
          }
        }

        function checkCompletion() {
          completedCalls++;
          console.log(`API call completed (${completedCalls}/${totalCalls})`);
          if (completedCalls === totalCalls) {
            analyzeBtn.style.display = 'none';
            clearBtn.style.display = 'block';
            metricsEl.innerHTML = '<div style="text-align:center;padding:12px;font-size:12px;opacity:0.7">✓ Analysis complete</div>';
            console.log('All analyses completed successfully');
          }
        }

        console.log('Launching 3 parallel API calls...');

        // API CALL 1: Comments Analysis
        console.log('[PARALLEL] Starting Comments Analysis...');
        updateLoadingMessage('Analyzing comments...');
        sendCommentsAnalysisRequest(videoId, (response) => {
          console.log('[PARALLEL] Comments Analysis response received');
          if (response && response.success) {
            const data = response.data.analysis || response.data;
            console.log('Comments analysis received:', data);

            if (data.sentiment_counts) {
              updateCommentsAnalysis(
                data.sentiment_counts.positive || 0,
                data.sentiment_counts.neutral || 0,
                data.sentiment_counts.negative || 0
              );
              document.getElementById('comments-analysis-section').style.display = 'block';
            }

            if (data.engagement_metrics) {
              metricsEl.innerHTML = '';

              const engagementScore = data.engagement_metrics.engagement_score;
              const percentage = Math.round(engagementScore);
              const scoreForColor = engagementScore / 100;

              metricsEl.innerHTML += `
                            <div style="margin-bottom:10px">
                              <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                                <span>Engagement Score</span>
                                <span style="font-weight:bold">${percentage}%</span>
                              </div>
                              <div style="background: #333; height: 6px; border-radius: 3px; overflow: hidden;">
                                <div style="width: ${percentage}%; height: 6px; background: ${getScoreColor(scoreForColor)}; border-radius: 3px; transition: width 0.5s ease;"></div>
                              </div>
                            </div>`;

              if (data.engagement_metrics.bot_activity_percentage !== undefined) {
                const botPercent = data.engagement_metrics.bot_activity_percentage;
                const botColor = botPercent > 10 ? '#f44336' : botPercent > 5 ? '#ff9800' : '#4caf50';

                metricsEl.innerHTML += `
                                <div style="margin-bottom:10px">
                                  <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                                    <span>Bot Activity</span>
                                    <span style="font-weight:bold;color:${botColor}">${botPercent}%</span>
                                  </div>
                                  <div style="background: #333; height: 6px; border-radius: 3px; overflow: hidden;">
                                    <div style="width: ${botPercent}%; height: 6px; background: ${botColor}; border-radius: 3px; transition: width 0.5s ease;"></div>
                                  </div>
                                </div>`;
              }
            }

            if (data.community_insights) {
              renderCommunityInsights(data.community_insights);
              document.getElementById('community-insights-section').style.display = 'block';
            }

            if (data.summary_of_vibe) {
              renderCommunityVibe(data.summary_of_vibe);
              document.getElementById('community-vibe-section').style.display = 'block';
            }
          } else {
            console.error('Comments analysis failed:', response);
          }
          checkCompletion();
        });

        // API CALL 2: Fact Checks & Alternative Perspectives
        console.log('[PARALLEL] Starting Facts Analysis...');
        sendAnalysisRequest('ANALYZE_FACTS', videoId, (response) => {
          console.log('[PARALLEL] Facts Analysis response received');
          if (response && response.success) {
            const data = response.data.analysis || response.data;
            console.log('Fact-check analysis received:', data);

            if (data.fact_checks && data.fact_checks.length > 0) {
              renderFactChecks(data.fact_checks);
              document.getElementById('fact-check-section').style.display = 'block';
            }

            if (data.alternative_perspectives && data.alternative_perspectives.length > 0) {
              renderAlternativePerspectives(data.alternative_perspectives);
              document.getElementById('alternative-perspectives-section').style.display = 'block';
            }

            if (data.bias_distribution) {
              renderBiasDistribution(data.bias_distribution);
              document.getElementById('bias-distribution-section').style.display = 'block';
            }
          } else {
            console.error('Fact-check analysis failed:', response);
          }
          checkCompletion();
        });

        // API CALL 3: Quality Metrics
        console.log('[PARALLEL] Starting Quality Analysis...');
        sendQualityAnalysisRequest(videoId, (response) => {
          console.log('[PARALLEL] Quality Analysis response received');
          if (response && response.success) {
            const data = response.data.analysis;
            console.log('Quality analysis received:', data);

            // Load tags FIRST (moved to top)
            if (data.content_tags && data.content_tags.length > 0) {
              renderTags(data.content_tags);
              document.getElementById('tags-section').style.display = 'block';
            }

            // Load summary SECOND (new field, right after tags)
            if (data.summary) {
              renderSummary(data.summary);
              document.getElementById('summary-section').style.display = 'block';
            }

            // Load credibility score
            if (window.ytaProgressBar && data.credibility_score !== undefined) {
              window.ytaProgressBar.animate(data.credibility_score);
              document.getElementById('credibility-score-section').style.display = 'block';
            }

            // Load clickbait meter
            if (data.clickbait_score !== undefined) {
              const clickbaitScore = typeof data.clickbait_score === 'number' && data.clickbait_score <= 1
                ? Math.round(data.clickbait_score * 100)
                : data.clickbait_score;
              updateClickbaitMeter(clickbaitScore);
              document.getElementById('clickbait-meter-section').style.display = 'block';
            }

            // Load key insights
            if (data.key_insights && data.key_insights.length > 0) {
              renderKeyInsights(data.key_insights);
              document.getElementById('key-insights-section').style.display = 'block';
            }

            // Load misinformation and quality scores
            const metricsContainer = document.getElementById('yta-metrics');
            if (data.misinformation_score !== undefined) {
              const score = data.misinformation_score;
              const percentage = Math.round(score * 100);

              metricsContainer.innerHTML += `
                            <div style="margin-bottom:10px">
                              <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                                <span>Misinformation Score</span>
                                <span style="font-weight:bold">${percentage}%</span>
                              </div>
                              <div style="background: #333; height: 6px; border-radius: 3px; overflow: hidden;">
                                <div style="width: ${percentage}%; height: 6px; background: ${getScoreColor(score)}; border-radius: 3px; transition: width 0.5s ease;"></div>
                              </div>
                            </div>`;
            }

            if (data.quality_score !== undefined) {
              const score = data.quality_score;
              const percentage = Math.round(score * 100);

              metricsContainer.innerHTML += `
                            <div style="margin-bottom:10px">
                              <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                                <span>Quality Score</span>
                                <span style="font-weight:bold">${percentage}%</span>
                              </div>
                              <div style="background: #333; height: 6px; border-radius: 3px; overflow: hidden;">
                                <div style="width: ${percentage}%; height: 6px; background: ${getScoreColor(score)}; border-radius: 3px; transition: width 0.5s ease;"></div>
                              </div>
                            </div>`;
            }
          } else {
            console.error('Quality analysis failed:', response);
          }
          checkCompletion();
        });

        console.log('All 3 API calls launched in parallel');
      });

    } catch (err) {
      console.error('Analyze click handler error:', err, err && err.stack);
      const analyzeBtn = document.getElementById('yta-analyze');
      analyzeBtn.disabled = false;
      analyzeBtn.style.opacity = '1';
      analyzeBtn.style.cursor = 'pointer';
      analyzeBtn.textContent = 'Analyze Video';
    }
  });

  // Clear Analysis functionality
  const clearBtn = document.getElementById('yta-clear');

  clearBtn.addEventListener('click', () => {
    if (!confirm('Are you sure you want to clear the current analysis?')) {
      return;
    }

    clearBtn.style.display = 'none';
    analyzeBtn.style.display = 'block';
    analyzeBtn.disabled = false;
    analyzeBtn.style.opacity = '1';
    analyzeBtn.style.cursor = 'pointer';
    analyzeBtn.textContent = 'Analyze Video';

    // Clear all sections
    document.getElementById('tags-section').style.display = 'none';
    document.getElementById('summary-section').style.display = 'none';
    document.getElementById('credibility-score-section').style.display = 'none';
    document.getElementById('clickbait-meter-section').style.display = 'none';
    document.getElementById('comments-analysis-section').style.display = 'none';
    document.getElementById('fact-check-section').style.display = 'none';
    document.getElementById('key-insights-section').style.display = 'none';
    document.getElementById('alternative-perspectives-section').style.display = 'none';
    document.getElementById('bias-distribution-section').style.display = 'none';
    document.getElementById('community-insights-section').style.display = 'none';
    document.getElementById('community-vibe-section').style.display = 'none';

    // Clear content
    document.getElementById('tags-content').innerHTML = '';
    document.getElementById('summary-content').innerHTML = '';
    document.getElementById('fact-check-results').innerHTML = '';
    document.getElementById('key-insights-results').innerHTML = '';
    document.getElementById('alternative-perspectives-results').innerHTML = '';
    document.getElementById('bias-distribution-content').innerHTML = '';
    document.getElementById('community-insights-content').innerHTML = '';
    document.getElementById('community-vibe-content').innerHTML = '';
    document.getElementById('comments-analysis-content').innerHTML = '';
    document.getElementById('yta-metrics').innerHTML = '';

    // Reset credibility score
    if (window.ytaProgressBar) {
      window.ytaProgressBar.animate(0.0);
    }

    // Reset clickbait meter
    const scoreValue = document.getElementById('clickbait-score-value');
    const scoreLabel = document.getElementById('clickbait-label');
    const indicator = document.getElementById('clickbait-indicator');
    if (scoreValue && scoreLabel && indicator) {
      scoreValue.style.color = '#4caf50';
      scoreValue.innerHTML = '0<span style="font-size: 20px; opacity: 0.7;">/100</span>';
      scoreLabel.textContent = 'Low Clickbait';
      indicator.style.left = '0%';
    }

    console.log('Analysis cleared - ready for new analysis');
  });

  // Helper functions
  function sendAnalysisRequest(type, videoId, callback) {
    try {
      if (typeof chrome !== 'undefined' && chrome.runtime && typeof chrome.runtime.sendMessage === 'function') {
        try {
          const result = chrome.runtime.sendMessage({ type: type, videoId: videoId }, callback);
          if (result && typeof result.then === 'function' && !callback) {
            result.then(() => { }).catch(err => console.error('Background sendMessage promise rejected:', err));
          }
          return;
        } catch (e) {
          console.warn('chrome.runtime.sendMessage threw, trying browser.runtime if available', e);
        }
      }

      if (typeof browser !== 'undefined' && browser.runtime && typeof browser.runtime.sendMessage === 'function') {
        const p = browser.runtime.sendMessage({ type: type, videoId: videoId });
        if (callback && p && typeof p.then === 'function') {
          p.then(callback).catch(err => {
            console.error('browser.runtime.sendMessage rejected:', err);
            callback(null);
          });
        }
        return;
      }

      console.error('No extension runtime available');
      if (typeof callback === 'function') callback(null);
    } catch (err) {
      console.error('sendAnalysisRequest error:', err);
      if (typeof callback === 'function') callback(null);
    }
  }

  function extractVideoInfo(videoUrl, callback) {
    console.log('Sending EXTRACT_VIDEO_INFO message to background');

    try {
      if (typeof chrome !== 'undefined' && chrome.runtime && typeof chrome.runtime.sendMessage === 'function') {
        try {
          chrome.runtime.sendMessage({ type: 'EXTRACT_VIDEO_INFO', url: videoUrl }, callback);
          return;
        } catch (e) {
          console.warn('chrome.runtime.sendMessage threw, trying browser.runtime if available', e);
        }
      }

      if (typeof browser !== 'undefined' && browser.runtime && typeof browser.runtime.sendMessage === 'function') {
        const p = browser.runtime.sendMessage({ type: 'EXTRACT_VIDEO_INFO', url: videoUrl });
        if (p && typeof p.then === 'function') {
          p.then(callback).catch(err => {
            console.error('browser.runtime.sendMessage rejected:', err);
            callback(null);
          });
        }
        return;
      }

      console.error('No extension runtime available');
      callback(null);
    } catch (err) {
      console.error('extractVideoInfo error:', err);
      callback(null);
    }
  }

  function sendCommentsAnalysisRequest(videoId, callback) {
    console.log('Sending ANALYZE_COMMENTS message to background with video_id:', videoId);

    try {
      if (typeof chrome !== 'undefined' && chrome.runtime && typeof chrome.runtime.sendMessage === 'function') {
        try {
          chrome.runtime.sendMessage({ type: 'ANALYZE_COMMENTS', videoId: videoId }, callback);
          return;
        } catch (e) {
          console.warn('chrome.runtime.sendMessage threw, trying browser.runtime if available', e);
        }
      }

      if (typeof browser !== 'undefined' && browser.runtime && typeof browser.runtime.sendMessage === 'function') {
        const p = browser.runtime.sendMessage({ type: 'ANALYZE_COMMENTS', videoId: videoId });
        if (p && typeof p.then === 'function') {
          p.then(callback).catch(err => {
            console.error('browser.runtime.sendMessage rejected:', err);
            callback(null);
          });
        }
        return;
      }

      console.error('No extension runtime available');
      callback(null);
    } catch (err) {
      console.error('sendCommentsAnalysisRequest error:', err);
      callback(null);
    }
  }

  function sendQualityAnalysisRequest(videoId, callback) {
    console.log('Sending ANALYZE_QUALITY message to background with video_id:', videoId);

    try {
      if (typeof chrome !== 'undefined' && chrome.runtime && typeof chrome.runtime.sendMessage === 'function') {
        try {
          chrome.runtime.sendMessage({ type: 'ANALYZE_QUALITY', videoId: videoId }, callback);
          return;
        } catch (e) {
          console.warn('chrome.runtime.sendMessage threw, trying browser.runtime if available', e);
        }
      }

      if (typeof browser !== 'undefined' && browser.runtime && typeof browser.runtime.sendMessage === 'function') {
        const p = browser.runtime.sendMessage({ type: 'ANALYZE_QUALITY', videoId: videoId });
        if (p && typeof p.then === 'function') {
          p.then(callback).catch(err => {
            console.error('browser.runtime.sendMessage rejected:', err);
            callback(null);
          });
        }
        return;
      }

      console.error('No extension runtime available');
      callback(null);
    } catch (err) {
      console.error('sendQualityAnalysisRequest error:', err);
      callback(null);
    }
  }

  function updateClickbaitMeter(score) {
    const scoreValue = document.getElementById('clickbait-score-value');
    const scoreLabel = document.getElementById('clickbait-label');
    const indicator = document.getElementById('clickbait-indicator');

    let color, label;
    if (score <= 33) {
      color = '#4caf50';
      label = 'Low Clickbait';
    } else if (score <= 66) {
      color = '#ff9800';
      label = 'Medium Clickbait';
    } else {
      color = '#f44336';
      label = 'High Clickbait';
    }

    scoreValue.style.color = color;
    scoreValue.innerHTML = `${score}<span style="font-size: 20px; opacity: 0.7;">/100</span>`;
    scoreLabel.textContent = label;
    indicator.style.left = `${score}%`;
  }

  function updateCommentsAnalysis(positive, neutral, negative) {
    const container = document.getElementById('comments-analysis-content');

    const total = positive + neutral + negative;
    const positivePercent = total > 0 ? Math.round((positive / total) * 100) : 0;
    const neutralPercent = total > 0 ? Math.round((neutral / total) * 100) : 0;
    const negativePercent = total > 0 ? Math.round((negative / total) * 100) : 0;

    container.innerHTML = `
            <div style="margin-bottom: 16px;">
              <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
              ">
                <span style="font-size: 12px;">Positive</span>
                <span style="font-size: 12px; font-weight: bold; color: #4caf50;">${positivePercent}%</span>
              </div>
              <div style="
                width: 100%;
                height: 8px;
                background: rgba(255,255,255,0.1);
                border-radius: 4px;
                overflow: hidden;
              ">
                <div style="
                  width: ${positivePercent}%;
                  height: 100%;
                  background: #4caf50;
                  border-radius: 4px;
                  transition: width 0.5s ease;
                "></div>
              </div>
            </div>
            
            <div style="margin-bottom: 16px;">
              <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
              ">
                <span style="font-size: 12px;">Neutral</span>
                <span style="font-size: 12px; font-weight: bold; color: #ff9800;">${neutralPercent}%</span>
              </div>
              <div style="
                width: 100%;
                height: 8px;
                background: rgba(255,255,255,0.1);
                border-radius: 4px;
                overflow: hidden;
              ">
                <div style="
                  width: ${neutralPercent}%;
                  height: 100%;
                  background: #ff9800;
                  border-radius: 4px;
                  transition: width 0.5s ease;
                "></div>
              </div>
            </div>
            
            <div style="margin-bottom: 0;">
              <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
              ">
                <span style="font-size: 12px;">Negative</span>
                <span style="font-size: 12px; font-weight: bold; color: #f44336;">${negativePercent}%</span>
              </div>
              <div style="
                width: 100%;
                height: 8px;
                background: rgba(255,255,255,0.1);
                border-radius: 4px;
                overflow: hidden;
              ">
                <div style="
                  width: ${negativePercent}%;
                  height: 100%;
                  background: #f44336;
                  border-radius: 4px;
                  transition: width 0.5s ease;
                "></div>
              </div>
            </div>
        `;
  }

  function renderFactChecks(factChecks) {
    const container = document.getElementById('fact-check-results');
    container.innerHTML = '';

    factChecks.forEach((claim, index) => {
      const badge = getFactCheckBadge(claim.verdict);
      const badgeColor = getFactCheckColor(claim.verdict);

      container.innerHTML += `
            <div style="
              background: rgba(255,255,255,0.05);
              padding: 10px;
              border-radius: 6px;
              margin-bottom: 8px;
              border-left: 3px solid ${badgeColor};
            ">
              <div style="
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 6px;
              ">
                <span style="
                  background: ${badgeColor};
                  color: white;
                  padding: 3px 8px;
                  border-radius: 12px;
                  font-size: 10px;
                  font-weight: bold;
                  text-transform: uppercase;
                ">${badge}</span>
                <span style="font-size: 11px; opacity: 0.7;">Claim ${index + 1}</span>
              </div>
              <div style="
                font-size: 12px;
                line-height: 1.4;
                margin-bottom: 6px;
              ">${escapeHtml(claim.claim)}</div>
              ${claim.explanation ? `
              <div style="
                font-size: 11px;
                opacity: 0.8;
                font-style: italic;
                margin-top: 6px;
                padding-top: 6px;
                border-top: 1px solid rgba(255,255,255,0.1);
              ">${escapeHtml(claim.explanation)}</div>
              ` : ''}
            </div>`;
    });
  }

  function renderKeyInsights(insights) {
    const container = document.getElementById('key-insights-results');
    container.innerHTML = '<div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 6px;"><ul style="margin: 0; padding-left: 20px; list-style: none;">';

    insights.forEach((insight, index) => {
      const insightText = typeof insight === 'string' ? insight : insight.text;
      const severity = typeof insight === 'object' ? insight.severity : 'neutral';
      const bulletColor = getInsightColor(severity);
      const isLast = index === insights.length - 1;

      container.innerHTML += `
            <li style="
              position: relative;
              margin-bottom: ${isLast ? '0' : '10px'};
              padding-left: 0;
              font-size: 12px;
              line-height: 1.5;
            ">
              <span style="
                color: ${bulletColor};
                margin-right: 8px;
                font-weight: bold;
              ">•</span>
              ${escapeHtml(insightText)}
            </li>`;
    });

    container.innerHTML += '</ul></div>';
  }

  function renderAlternativePerspectives(perspectives) {
    const container = document.getElementById('alternative-perspectives-results');
    container.innerHTML = '';

    const colors = ['#2196f3', '#9c27b0', '#ff5722', '#00bcd4', '#ff9800'];

    perspectives.forEach((perspective, index) => {
      const borderColor = colors[index % colors.length];

      container.innerHTML += `
            <div style="
              background: rgba(255,255,255,0.05);
              padding: 12px;
              border-radius: 6px;
              margin-bottom: 8px;
              border-left: 3px solid ${borderColor};
            ">
              <div style="
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                margin-bottom: 8px;
              ">
                <div style="flex: 1;">
                  <div style="
                    font-weight: bold;
                    font-size: 12px;
                    margin-bottom: 4px;
                  ">${escapeHtml(perspective.source || 'Unknown Source')}</div>
                  <div style="
                    font-size: 11px;
                    opacity: 0.7;
                    margin-bottom: 6px;
                  ">${escapeHtml(perspective.type || 'Alternative View')}</div>
                  <div style="
                    font-size: 12px;
                    line-height: 1.4;
                  ">${escapeHtml(perspective.description || '')}</div>
                </div>
              </div>
              ${perspective.url ? `
              <a href="${escapeHtml(perspective.url)}" target="_blank" style="
                display: inline-block;
                font-size: 11px;
                color: ${borderColor};
                text-decoration: none;
                margin-top: 6px;
              ">View Source →</a>
              ` : ''}
            </div>`;
    });
  }

  function renderCommunityInsights(insights) {
    const container = document.getElementById('community-insights-content');

    const controversyLevel = (insights.controversy_level || '').toLowerCase();
    let controversyColor, controversyBg;
    if (controversyLevel === 'low') {
      controversyColor = '#4caf50';
      controversyBg = 'rgba(76, 175, 80, 0.1)';
    } else if (controversyLevel === 'medium') {
      controversyColor = '#ff9800';
      controversyBg = 'rgba(255, 152, 0, 0.1)';
    } else {
      controversyColor = '#f44336';
      controversyBg = 'rgba(244, 67, 54, 0.1)';
    }

    container.innerHTML = `
            <div style="
              background: rgba(255,255,255,0.05);
              padding: 12px;
              border-radius: 6px;
              margin-bottom: 8px;
            ">
              <div style="margin-bottom: 12px;">
                <div style="
                  display: inline-block;
                  background: ${controversyBg};
                  border: 1px solid ${controversyColor};
                  color: ${controversyColor};
                  padding: 4px 12px;
                  border-radius: 12px;
                  font-size: 11px;
                  font-weight: bold;
                  text-transform: uppercase;
                ">
                  ${insights.controversy_level || 'Unknown'} Controversy
                </div>
              </div>
              
              <div style="margin-bottom: 8px;">
                <div style="
                  font-size: 11px;
                  opacity: 0.7;
                  margin-bottom: 4px;
                  text-transform: uppercase;
                  letter-spacing: 0.5px;
                ">Dominant Topic</div>
                <div style="
                  font-size: 12px;
                  line-height: 1.5;
                ">${escapeHtml(insights.dominant_topic || 'No dominant topic identified')}</div>
              </div>
            </div>
        `;
  }

  function renderCommunityVibe(vibeText) {
    const container = document.getElementById('community-vibe-content');

    container.innerHTML = `
            <div style="
              background: rgba(255,255,255,0.05);
              padding: 14px;
              border-radius: 6px;
              border-left: 3px solid #9c27b0;
            ">
              <div style="
                font-size: 12px;
                line-height: 1.6;
                color: rgba(255,255,255,0.9);
              ">${escapeHtml(vibeText)}</div>
            </div>
        `;
  }

  function renderTags(tags) {
    const container = document.getElementById('tags-content');

    function stringToColor(str) {
      let hash = 0;
      for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
      }

      const hue = Math.abs(hash % 360);
      const saturation = 65 + (Math.abs(hash) % 20);
      const lightness = 45 + (Math.abs(hash >> 8) % 15);

      return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    }

    let tagsHtml = '<div style="display: flex; flex-wrap: wrap; gap: 8px;">';

    tags.forEach((tag) => {
      const color = stringToColor(tag.toLowerCase());
      tagsHtml += `
                <span style="
                  display: inline-block;
                  background: ${color}22;
                  border: 1px solid ${color};
                  color: ${color};
                  padding: 6px 12px;
                  border-radius: 16px;
                  font-size: 11px;
                  font-weight: 500;
                  text-transform: capitalize;
                  white-space: nowrap;
                ">${escapeHtml(tag)}</span>
            `;
    });

    tagsHtml += '</div>';
    container.innerHTML = tagsHtml;
  }

  // NEW FUNCTION: Render Summary
  function renderSummary(summaryText) {
    const container = document.getElementById('summary-content');

    container.innerHTML = `
            <div style="
              background: rgba(255,255,255,0.05);
              padding: 14px;
              border-radius: 6px;
              border-left: 3px solid #2196f3;
            ">
              <div style="
                font-size: 12px;
                line-height: 1.6;
                color: rgba(255,255,255,0.95);
              ">${escapeHtml(summaryText)}</div>
            </div>
        `;
  }

  function renderBiasDistribution(biasData) {
    const container = document.getElementById('bias-distribution-content');

    const total = (biasData.left_count || 0) + (biasData.center_count || 0) + (biasData.right_count || 0);

    if (total === 0) {
      container.innerHTML = `
                <div style="
                  background: rgba(255,255,255,0.05);
                  padding: 12px;
                  border-radius: 6px;
                  text-align: center;
                  font-size: 12px;
                  opacity: 0.7;
                ">No bias data available</div>
            `;
      return;
    }

    const leftPercent = Math.round((biasData.left_count / total) * 100);
    const centerPercent = Math.round((biasData.center_count / total) * 100);
    const rightPercent = Math.round((biasData.right_count / total) * 100);

    container.innerHTML = `
            <div style="
              background: rgba(255,255,255,0.05);
              padding: 16px;
              border-radius: 6px;
            ">
              <div style="margin-bottom: 16px;">
                <div style="
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                  margin-bottom: 8px;
                ">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 12px;">Left Leaning</span>
                    <span style="
                      background: rgba(33, 150, 243, 0.2);
                      color: #2196f3;
                      padding: 2px 8px;
                      border-radius: 10px;
                      font-size: 10px;
                      font-weight: bold;
                    ">${biasData.left_count}</span>
                  </div>
                  <span style="font-size: 12px; font-weight: bold; color: #2196f3;">${leftPercent}%</span>
                </div>
                <div style="
                  width: 100%;
                  height: 8px;
                  background: rgba(255,255,255,0.1);
                  border-radius: 4px;
                  overflow: hidden;
                ">
                  <div style="
                    width: ${leftPercent}%;
                    height: 100%;
                    background: #2196f3;
                    border-radius: 4px;
                    transition: width 0.5s ease;
                  "></div>
                </div>
              </div>
              
              <div style="margin-bottom: 16px;">
                <div style="
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                  margin-bottom: 8px;
                ">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 12px;">Center/Neutral</span>
                    <span style="
                      background: rgba(156, 39, 176, 0.2);
                      color: #9c27b0;
                      padding: 2px 8px;
                      border-radius: 10px;
                      font-size: 10px;
                      font-weight: bold;
                    ">${biasData.center_count}</span>
                  </div>
                  <span style="font-size: 12px; font-weight: bold; color: #9c27b0;">${centerPercent}%</span>
                </div>
                <div style="
                  width: 100%;
                  height: 8px;
                  background: rgba(255,255,255,0.1);
                  border-radius: 4px;
                  overflow: hidden;
                ">
                  <div style="
                    width: ${centerPercent}%;
                    height: 100%;
                    background: #9c27b0;
                    border-radius: 4px;
                    transition: width 0.5s ease;
                  "></div>
                </div>
              </div>
              
              <div style="margin-bottom: 0;">
                <div style="
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                  margin-bottom: 8px;
                ">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 12px;">Right Leaning</span>
                    <span style="
                      background: rgba(255, 87, 34, 0.2);
                      color: #ff5722;
                      padding: 2px 8px;
                      border-radius: 10px;
                      font-size: 10px;
                      font-weight: bold;
                    ">${biasData.right_count}</span>
                  </div>
                  <span style="font-size: 12px; font-weight: bold; color: #ff5722;">${rightPercent}%</span>
                </div>
                <div style="
                  width: 100%;
                  height: 8px;
                  background: rgba(255,255,255,0.1);
                  border-radius: 4px;
                  overflow: hidden;
                ">
                  <div style="
                    width: ${rightPercent}%;
                    height: 100%;
                    background: #ff5722;
                    border-radius: 4px;
                    transition: width 0.5s ease;
                  "></div>
                </div>
              </div>
              
              <div style="
                margin-top: 12px;
                padding-top: 12px;
                border-top: 1px solid rgba(255,255,255,0.1);
                font-size: 11px;
                opacity: 0.7;
                text-align: center;
              ">
                Based on ${total} source${total !== 1 ? 's' : ''} analyzed
              </div>
            </div>
        `;

    document.getElementById('bias-distribution-section').style.display = 'block';
  }

  function getScoreColor(score) {
    if (score >= 0.7) return '#4caf50';
    if (score >= 0.4) return '#ff9800';
    return '#f44336';
  }

  function getInsightColor(severity) {
    const severityLower = (severity || '').toLowerCase();
    if (severityLower.includes('positive') || severityLower.includes('good')) {
      return '#4caf50';
    } else if (severityLower.includes('negative') || severityLower.includes('bad') || severityLower.includes('warning')) {
      return '#f44336';
    } else if (severityLower.includes('caution') || severityLower.includes('moderate')) {
      return '#ff9800';
    }
    return '#4caf50';
  }

  function getFactCheckBadge(verdict) {
    const verdictLower = (verdict || '').toLowerCase();

    if (verdictLower.includes('true') || verdictLower.includes('accurate') || verdictLower.includes('verified')) {
      return 'True';
    } else if (verdictLower.includes('false') || verdictLower.includes('misleading') || verdictLower.includes('debunked')) {
      return 'False';
    } else if (verdictLower.includes('partial') || verdictLower.includes('mixed') || verdictLower.includes('unverified')) {
      return 'Partial';
    }

    return 'Unclear';
  }

  function getFactCheckColor(verdict) {
    const verdictLower = (verdict || '').toLowerCase();

    if (verdictLower.includes('true') || verdictLower.includes('accurate') || verdictLower.includes('verified')) {
      return '#4caf50';
    } else if (verdictLower.includes('false') || verdictLower.includes('misleading') || verdictLower.includes('debunked')) {
      return '#f44336';
    } else if (verdictLower.includes('partial') || verdictLower.includes('mixed') || verdictLower.includes('unverified')) {
      return '#ff9800';
    }

    return '#9e9e9e';
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
})();