// POST /analyze 실제 연동

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

export async function analyzeText(rawText, baseDate) {
    const res = await fetch(`${API_URL}/analyze/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ raw_text: rawText, base_date: baseDate }),
    });
    if (!res.ok) throw new Error("분석 요청 실패");
    return res.json();
}

export async function analyzeFeedback(sessionId, original, modified) {
    const res = await fetch(`${API_URL}/feedback/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, original, modified }),
    });
    if (!res.ok) throw new Error("피드백 분석 실패");
    return res.json();
}

export async function confirmFeedback(sessionId, logId, action, candidates) {
    const res = await fetch(`${API_URL}/feedback/confirm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, log_id: logId, action, candidates }),
    });
    if (!res.ok) throw new Error("선호 저장 실패");
    return res.json();
}
