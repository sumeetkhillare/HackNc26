// utils/api.js - helper to call backend (for future use from UI code)
export async function analyze(url) {
    const resp = await fetch('https://your-backend.com/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
    });
    if (!resp.ok) throw new Error(`Network response was not ok: ${resp.status}`);
    return resp.json();
}
