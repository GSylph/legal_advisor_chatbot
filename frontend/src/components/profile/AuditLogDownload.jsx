import { useState } from "react";

export default function AuditLogDownload() {
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const sessionId = localStorage.getItem("ealai_session_id");

  async function download() {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/audit/${sessionId}`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `audit_log_${sessionId.slice(0, 8)}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-card border border-zinc-100 p-7">
      <h2 className="font-semibold text-zinc-800 text-base mb-1.5">Audit Log</h2>
      <p className="text-sm text-zinc-500 mb-5 leading-relaxed max-w-lg">
        Download a complete tamper-evident audit log for your current session.
        Each entry is SHA-256 hashed and verifiable.
      </p>

      {!sessionId ? (
        <div className="flex items-center gap-2 text-sm text-zinc-400">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          Start a chat session first to generate an audit log.
        </div>
      ) : (
        <button
          onClick={download}
          disabled={loading}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-zinc-900 text-white text-sm font-semibold hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-700"
        >
          {loading ? (
            <span className="w-3.5 h-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin" />
          ) : (
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
          )}
          {loading ? "Downloading…" : "Download Audit Log"}
        </button>
      )}

      {error && (
        <p className="mt-3 text-xs text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
          {error}
        </p>
      )}

      <p className="text-[11px] text-zinc-400 mt-4">
        Session: <code className="bg-zinc-100 px-1 rounded">{sessionId ? `${sessionId.slice(0, 16)}…` : "none"}</code>
      </p>
    </div>
  );
}
