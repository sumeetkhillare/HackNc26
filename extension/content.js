// content.js - injects a simple overlay and sends ANALYZE_VIDEO messages to background
(function () {
    // Only run on YouTube watch pages
    if (!window.location.href.includes('watch')) return;
    if (document.getElementById('yta-overlay-root')) return;

    // ==================== MOCK DATA - REPLACE WITH BACKEND DATA ====================
    const MOCK_DATA = {
        // Core metrics
        credibility_score: 0.75,
        clickbait_score: 35, // 0-100
        
        // Sentiment (from backend: sentiment_counts)
        sentiment_counts: {
            positive: 55,
            negative: 25,
            neutral: 13
        },
        
        // Engagement (from backend: engagement_metrics)
        engagement_metrics: {
            engagement_score: 92, // 0-100 scale
            bot_activity_percentage: 2
        },
        
        // Community insights (from backend: community_insights)
        community_insights: {
            dominant_topic: "The dynamic between host Dylan and editor Alex, interspersed with reactions to the Epstein files and the school shooter's identity.",
            controversy_level: "High" // Low, Medium, High
        },
        
        // Community vibe (from backend: summary_of_vibe)
        summary_of_vibe: "The audience is deeply invested in the channel's meta-humor, specifically praising the editor Alex and participating in 'Petition' memes. While the news content regarding Epstein and the school shooting sparks intense and often polarized debate, the core community remains highly supportive of the creator's personality and production style.",
        
        // Existing fields
        fact_checks: [
            {
                claim: "The Earth orbits around the Sun",
                verdict: "true",
                explanation: "This is scientifically verified and has been proven through astronomical observations."
            },
            {
                claim: "5G networks cause health problems",
                verdict: "false",
                explanation: "Multiple scientific studies have found no evidence linking 5G to health issues."
            },
            {
                claim: "Coffee is healthy for everyone",
                verdict: "partial",
                explanation: "Coffee has health benefits for most people, but can be harmful for those with certain conditions."
            }
        ],
        key_insights: [
            { text: "Video demonstrates high production quality with professional editing", severity: "positive" },
            { text: "Content creator has established credibility in this topic area", severity: "positive" },
            { text: "Some claims lack supporting sources or citations", severity: "caution" },
            { text: "Engagement metrics suggest authentic audience interaction", severity: "positive" },
            { text: "Video contains one potentially misleading statement about statistics", severity: "negative" },
            { text: "Channel has a history of accurate reporting", severity: "positive" },
            { text: "Viewer discretion advised for sensitive content", severity: "caution" }
        ],
        alternative_perspectives: [
            {
                source: "BBC News",
                type: "Mainstream Media Perspective",
                description: "Covers similar topic with emphasis on expert analysis and peer-reviewed studies.",
                url: "https://bbc.com/news/example"
            },
            {
                source: "Scientific American",
                type: "Academic Perspective",
                description: "Provides in-depth scientific analysis with citations from recent research publications.",
                url: "https://scientificamerican.com/article/example"
            },
            {
                source: "The Guardian",
                type: "Investigative Journalism",
                description: "Investigative piece exploring counter-arguments and alternative viewpoints on this topic.",
                url: "https://theguardian.com/article/example"
            }
        ],
        misinformation_score: 0.3,
        quality_score: 0.9
    };
    // ==================== END MOCK DATA ====================

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
    root.style.width = '380px';
    root.style.maxHeight = 'calc(100vh - 100px)';
    root.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
    root.style.fontFamily = 'Arial, sans-serif';
    root.style.transition = 'all 0.3s ease';
    root.style.display = 'flex';
    root.style.flexDirection = 'column';
    root.innerHTML = `
    <div id="yta-ui" style="display: flex; flex-direction: column; height: 100%; min-height: 0;">
      <!-- Header with Minimize Button -->
      <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        flex-shrink: 0;
      ">
        <span style="font-weight: bold; font-size: 16px;">Video Analysis</span>
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
        
        <div id="credibility-score"></div>
        
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
              ">35<span style="font-size: 20px; opacity: 0.7;">/100</span></div>
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
                left: 35%;
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

    // Minimize/Maximize functionality
    let isMinimized = false;
    const minimizeBtn = document.getElementById('yta-minimize');
    
    minimizeBtn.addEventListener('click', () => {
        isMinimized = !isMinimized;
        
        if (isMinimized) {
            contentDiv.style.display = 'none';
            minimizeBtn.textContent = '+';
            minimizeBtn.title = 'Expand';
            root.style.width = '200px';
            root.style.padding = '12px 16px';
        } else {
            contentDiv.style.display = 'block';
            minimizeBtn.textContent = '−';
            minimizeBtn.title = 'Minimize';
            root.style.width = '380px';
            root.style.padding = '16px';
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

            // Disable button and show loading state
            analyzeBtn.disabled = true;
            analyzeBtn.style.opacity = '0.6';
            analyzeBtn.style.cursor = 'not-allowed';
            analyzeBtn.textContent = 'Analyzing...';
            
            // Show loading spinner in metrics area
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
                    ">Analyzing video...</div>
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

            // ==================== BACKEND INTEGRATION ====================
            // Send message to background script (which calls Flask server)
            (function sendRuntimeMessage(message, callback) {
                try {
                    if (typeof chrome !== 'undefined' && chrome.runtime && typeof chrome.runtime.sendMessage === 'function') {
                        try {
                            const result = chrome.runtime.sendMessage(message, callback);
                            if (result && typeof result.then === 'function' && !callback) {
                                result.then(() => { }).catch(err => console.error('Background sendMessage promise rejected:', err));
                            }
                            return;
                        } catch (e) {
                            console.warn('chrome.runtime.sendMessage threw, trying browser.runtime if available', e);
                        }
                    }

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

                    console.error('No extension runtime available');
                    if (typeof callback === 'function') callback(null);
                } catch (err) {
                    console.error('sendRuntimeMessage error:', err);
                    if (typeof callback === 'function') callback(null);
                }
            })({ type: 'ANALYZE_VIDEO', videoUrl: videoLink }, (response) => {
                // Re-enable button
                analyzeBtn.disabled = false;
                analyzeBtn.style.opacity = '1';
                analyzeBtn.style.cursor = 'pointer';
                analyzeBtn.textContent = 'Analyze Video';
                
                try {
                    if (!response) {
                        metricsEl.innerHTML = '<div style="text-align:center;color:#f44336;font-size:12px;padding:12px;">No response from server. Please check if the Flask server is running.</div>';
                        return;
                    }
                    
                    if (response.success) {
                        const metrics = response.data;
                        
                        console.log('Received backend response:', metrics);
                        
                        // ==================== LOAD ALL METRICS FROM BACKEND ====================
                        
                        // 1. Update credibility score
                        if (window.ytaProgressBar && metrics.credibility_score !== undefined) {
                            window.ytaProgressBar.animate(metrics.credibility_score);
                        }

                        // 2. Update clickbait meter
                        if (metrics.clickbait_score !== undefined) {
                            const clickbaitScore = typeof metrics.clickbait_score === 'number' && metrics.clickbait_score <= 1 
                                ? Math.round(metrics.clickbait_score * 100) 
                                : metrics.clickbait_score;
                            updateClickbaitMeter(clickbaitScore);
                            document.getElementById('clickbait-meter-section').style.display = 'block';
                        }

                        // 3. Update comments analysis (from sentiment_counts)
                        if (metrics.sentiment_counts) {
                            updateCommentsAnalysis(
                                metrics.sentiment_counts.positive || 0,
                                metrics.sentiment_counts.neutral || 0,
                                metrics.sentiment_counts.negative || 0
                            );
                            document.getElementById('comments-analysis-section').style.display = 'block';
                        }

                        // 4. Render fact checks
                        if (metrics.fact_checks && metrics.fact_checks.length > 0) {
                            renderFactChecks(metrics.fact_checks);
                            document.getElementById('fact-check-section').style.display = 'block';
                        }

                        // 5. Render key insights
                        if (metrics.key_insights && metrics.key_insights.length > 0) {
                            renderKeyInsights(metrics.key_insights);
                            document.getElementById('key-insights-section').style.display = 'block';
                        }

                        // 6. Render alternative perspectives
                        if (metrics.alternative_perspectives && metrics.alternative_perspectives.length > 0) {
                            renderAlternativePerspectives(metrics.alternative_perspectives);
                            document.getElementById('alternative-perspectives-section').style.display = 'block';
                        }

                        // 7. Render community insights
                        if (metrics.community_insights) {
                            renderCommunityInsights(metrics.community_insights);
                            document.getElementById('community-insights-section').style.display = 'block';
                        }

                        // 8. Render community vibe
                        if (metrics.summary_of_vibe) {
                            renderCommunityVibe(metrics.summary_of_vibe);
                            document.getElementById('community-vibe-section').style.display = 'block';
                        }
                        
                        // 9. Display metrics section
                        metricsEl.innerHTML = '';
                        
                        // 9a. Add engagement score from engagement_metrics
                        if (metrics.engagement_metrics && metrics.engagement_metrics.engagement_score !== undefined) {
                            const engagementScore = metrics.engagement_metrics.engagement_score / 100; // Convert 0-100 to 0-1
                            const percentage = Math.round(engagementScore * 100);
                            
                            metricsEl.innerHTML += `
                            <div style="margin-bottom:10px">
                              <div style="
                                display: flex;
                                justify-content: space-between;
                                font-size: 12px;
                                margin-bottom: 4px;
                              ">
                                <span>Engagement Score</span>
                                <span style="font-weight:bold">${percentage}%</span>
                              </div>
                              <div style="
                                background: #333;
                                height: 6px;
                                border-radius: 3px;
                                overflow: hidden;
                              ">
                                <div style="
                                  width: ${percentage}%;
                                  height: 6px;
                                  background: ${getScoreColor(engagementScore)};
                                  border-radius: 3px;
                                  transition: width 0.5s ease;
                                "></div>
                              </div>
                            </div>`;
                            
                            // 9b. Add bot activity indicator if available
                            if (metrics.engagement_metrics.bot_activity_percentage !== undefined) {
                                const botPercent = metrics.engagement_metrics.bot_activity_percentage;
                                const botColor = botPercent > 10 ? '#f44336' : botPercent > 5 ? '#ff9800' : '#4caf50';
                                
                                metricsEl.innerHTML += `
                                <div style="margin-bottom:10px">
                                  <div style="
                                    display: flex;
                                    justify-content: space-between;
                                    font-size: 12px;
                                    margin-bottom: 4px;
                                  ">
                                    <span>Bot Activity</span>
                                    <span style="font-weight:bold;color:${botColor}">${botPercent}%</span>
                                  </div>
                                  <div style="
                                    background: #333;
                                    height: 6px;
                                    border-radius: 3px;
                                    overflow: hidden;
                                  ">
                                    <div style="
                                      width: ${botPercent}%;
                                      height: 6px;
                                      background: ${botColor};
                                      border-radius: 3px;
                                      transition: width 0.5s ease;
                                    "></div>
                                  </div>
                                </div>`;
                            }
                        }
                        
                        // 9c. Add other metrics (misinformation and quality scores)
                        const otherMetrics = ['misinformation_score', 'quality_score'];
                        otherMetrics.forEach(k => {
                            if (metrics[k] !== undefined) {
                                const score = metrics[k];
                                const percentage = Math.round(score * 100);
                                
                                metricsEl.innerHTML += `
                                <div style="margin-bottom:10px">
                                  <div style="
                                    display: flex;
                                    justify-content: space-between;
                                    font-size: 12px;
                                    margin-bottom: 4px;
                                  ">
                                    <span>${k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                                    <span style="font-weight:bold">${percentage}%</span>
                                  </div>
                                  <div style="
                                    background: #333;
                                    height: 6px;
                                    border-radius: 3px;
                                    overflow: hidden;
                                  ">
                                    <div style="
                                      width: ${percentage}%;
                                      height: 6px;
                                      background: ${getScoreColor(score)};
                                      border-radius: 3px;
                                      transition: width 0.5s ease;
                                    "></div>
                                  </div>
                                </div>`;
                            }
                        });
                        
                        // If no metrics were rendered, show a message
                        if (metricsEl.innerHTML === '') {
                            metricsEl.innerHTML = '<div style="text-align:center;padding:12px;font-size:12px;opacity:0.7">✓ Analysis complete</div>';
                        }
                        
                        // ==================== END LOAD ALL METRICS ====================
                        
                    } else {
                        metricsEl.innerHTML = `<div style="text-align:center;color:#f44336;font-size:12px;padding:12px;">Error: ${escapeHtml(response.error || 'Unknown error occurred')}</div>`;
                    }
                } catch (innerErr) {
                    console.error('Error handling analyze response:', innerErr, innerErr.stack);
                    metricsEl.innerHTML = '<div style="text-align:center;color:#f44336;font-size:12px;padding:12px;">Error processing response</div>';
                }
            });
            // ==================== END BACKEND INTEGRATION ====================
            
        } catch (err) {
            console.error('Analyze click handler error:', err, err && err.stack);
            const analyzeBtn = document.getElementById('yta-analyze');
            analyzeBtn.disabled = false;
            analyzeBtn.style.opacity = '1';
            analyzeBtn.style.cursor = 'pointer';
            analyzeBtn.textContent = 'Analyze Video';
        }
    });

    // Helper function to update clickbait meter
    function updateClickbaitMeter(score) {
        const scoreValue = document.getElementById('clickbait-score-value');
        const scoreLabel = document.getElementById('clickbait-label');
        const indicator = document.getElementById('clickbait-indicator');
        
        // Update score display
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
        
        // Update indicator position
        indicator.style.left = `${score}%`;
    }

    // Helper function to update comments analysis
    function updateCommentsAnalysis(positive, neutral, negative) {
        const container = document.getElementById('comments-analysis-content');
        
        // Ensure percentages add up to 100
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

    // Helper function to render fact checks
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

    // Helper function to render key insights
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

    // Helper function to render alternative perspectives
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

    // Helper function to render community insights
    function renderCommunityInsights(insights) {
        const container = document.getElementById('community-insights-content');
        
        // Get controversy level color
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
              <!-- Controversy Level Badge -->
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
              
              <!-- Dominant Topic -->
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

    // Helper function to render community vibe
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