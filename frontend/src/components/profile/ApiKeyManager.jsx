import { useState } from "react";

export default function ApiKeyManager() {
  const [revealed, setRevealed] = useState(false);
  const [copied,   setCopied]   = useState(false);

  const DISPLAY = "gsk_••• (configured server-side in .env)";
  const MASKED  = "gsk_●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●";

  function copyKey() {
    navigator.clipboard.writeText(DISPLAY).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div className="bg-white rounded-2xl shadow-card border border-zinc-100 p-7">
      <h2 className="font-semibold text-zinc-800 text-base mb-1.5">API Key</h2>
      <p className="text-xs text-zinc-400 mb-5">
        API keys are stored server-side in <code className="bg-zinc-100 px-1.5 py-0.5 rounded text-[11px]">.env</code> and
        are not accessible from the browser for security reasons.
      </p>

      <div className="flex items-center gap-2">
        <div className="flex-1 bg-zinc-50 border border-zinc-200 rounded-xl px-4 py-2.5 font-mono text-xs text-zinc-500 overflow-hidden text-ellipsis whitespace-nowrap">
          {revealed ? DISPLAY : MASKED}
        </div>
        <button
          onClick={() => setRevealed((v) => !v)}
          className="px-4 py-2.5 rounded-xl border border-zinc-200 text-xs font-medium text-zinc-600 hover:border-zinc-400 hover:text-zinc-900 transition-colors duration-150 whitespace-nowrap focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-300"
        >
          {revealed ? "Hide" : "Reveal"}
        </button>
        <button
          onClick={copyKey}
          className="px-4 py-2.5 rounded-xl border border-zinc-200 text-xs font-medium text-zinc-600 hover:border-zinc-400 hover:text-zinc-900 transition-colors duration-150 whitespace-nowrap focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-300"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>

      <p className="text-[11px] text-zinc-400 mt-4">
        To update keys, edit the <code className="bg-zinc-100 px-1 rounded">.env</code> file at the project root
        and restart the backend. Multiple keys are supported for daily limit rotation.
      </p>
    </div>
  );
}
