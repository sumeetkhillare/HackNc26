import React from 'react';

export default function App({ videoUrl }) {
    const [loading, setLoading] = React.useState(false);
    const [metrics, setMetrics] = React.useState(null);
    const [error, setError] = React.useState(null);

    const analyze = async () => {
        setLoading(true);
        setError(null);
        try {
            chrome.runtime.sendMessage({ type: 'ANALYZE_VIDEO', videoUrl }, (res) => {
                setLoading(false);
                if (res && res.success) setMetrics(res.data);
                else setError(res ? res.error : 'No response');
            });
        } catch (e) {
            setLoading(false);
            setError(e.message);
        }
    };

    return (
        <div className="yta-overlay">
            <button onClick={analyze} disabled={loading}>{loading ? 'Analyzing...' : 'Analyze'}</button>
            {error && <div className="error">{error}</div>}
            {metrics && <div className="metrics">
                {Object.entries(metrics).map(([k, v]) => (
                    <div key={k} className="metric">
                        <div className="label">{k}</div>
                        <div className="value">{v}</div>
                        <div className="bar"><div style={{ width: `${v * 100}%` }} className="bar-fill" /></div>
                    </div>
                ))}
            </div>}
        </div>
    );
}
