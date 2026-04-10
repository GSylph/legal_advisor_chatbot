import React, { useState } from 'react';

/**
 * ReasoningTrace component displays the EALAI reasoning chain.
 * Collapsible panel showing applicable law, rule engine results,
 * retrieved sources, reasoning chain, consistency status, and audit hash.
 *
 * Props are identical to the original — only styling has changed
 * to match the light theme redesign.
 */
export default function ReasoningTrace({
  applicableLaw,
  ruleMatched,
  ruleStatute,
  ruleSection,
  sources,
  reasoning,
  consistencyFlag,
  auditHash,
  warning,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const toggleOpen = () => setIsOpen(!isOpen);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="mt-3 border-t border-zinc-200 pt-2.5 text-xs">
      {/* Toggle button */}
      <button
        onClick={toggleOpen}
        aria-expanded={isOpen}
        className="
          flex items-center gap-1.5 text-zinc-400 hover:text-zinc-700
          font-medium transition-colors duration-150
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-300 rounded
        "
      >
        {/* Chevron */}
        <svg
          width="12" height="12" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
          className={`transition-transform duration-200 ${isOpen ? "rotate-90" : "rotate-0"}`}
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
        View Reasoning Trace
      </button>

      {/* Expandable content */}
      {isOpen && (
        <div className="animate-trace-expand mt-2.5 rounded-xl border border-zinc-200/80 bg-zinc-50 p-3.5 space-y-3.5">

          {/* 1. Applicable Statute */}
          <div>
            <span className="text-[10px] uppercase tracking-wider text-zinc-400 font-semibold block mb-1.5">
              Applicable Statute
            </span>
            <span className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 border border-blue-200 px-2.5 py-1 rounded-lg font-semibold text-xs">
              {applicableLaw || 'Not specified'}
            </span>
          </div>

          {/* 2. Symbolic Rule Engine */}
          <div>
            <span className="text-[10px] uppercase tracking-wider text-zinc-400 font-semibold block mb-1.5">
              Symbolic Rule Engine
            </span>
            {ruleMatched ? (
              <span className="inline-flex items-center gap-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-lg text-xs font-medium">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Rule matched: {ruleStatute} {ruleSection ? `(${ruleSection})` : ''}
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 bg-zinc-100 text-zinc-500 border border-zinc-200 px-2.5 py-1 rounded-lg text-xs">
                No symbolic rule matched
              </span>
            )}
          </div>

          {/* 3. Retrieved Sources */}
          <div>
            <span className="text-[10px] uppercase tracking-wider text-zinc-400 font-semibold block mb-1.5">
              Retrieved Sources
            </span>
            <ul className="space-y-1">
              {sources && sources.length > 0 ? (
                sources.map((src, idx) => (
                  <li key={idx} className="flex items-start gap-1.5 text-zinc-600">
                    <span className="mt-0.5 text-zinc-400 flex-shrink-0">·</span>
                    <span className="truncate">{src}</span>
                  </li>
                ))
              ) : (
                <li className="text-zinc-400 italic">No sources retrieved</li>
              )}
            </ul>
          </div>

          {/* 4. Reasoning Chain */}
          <div>
            <span className="text-[10px] uppercase tracking-wider text-zinc-400 font-semibold block mb-1.5">
              Reasoning Chain
            </span>
            <div
              className="
                rounded-lg border border-zinc-200 bg-white px-3 py-2
                font-mono text-[11px] text-zinc-500 leading-relaxed
                whitespace-pre-wrap max-h-36 overflow-y-auto
              "
            >
              {reasoning || 'No reasoning steps provided.'}
            </div>
          </div>

          {/* 5. Consistency Status */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase tracking-wider text-zinc-400 font-semibold">
              Consistency:
            </span>
            {consistencyFlag === true ? (
              <span className="flex items-center gap-1 text-emerald-600 font-medium">
                <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Consistent
              </span>
            ) : consistencyFlag === false ? (
              <span className="flex items-center gap-1 text-amber-600 font-medium" title={warning}>
                <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Inconsistent
              </span>
            ) : (
              <span className="text-zinc-400">Not verified</span>
            )}
          </div>

          {/* 6. Audit Hash */}
          <div className="pt-0.5">
            <span className="text-[10px] uppercase tracking-wider text-zinc-400 font-semibold block mb-1.5">
              Audit Hash (Tamper-evident)
            </span>
            <div
              onClick={() => copyToClipboard(auditHash)}
              className="
                font-mono text-[10px] text-zinc-400 hover:text-zinc-700
                cursor-pointer transition-colors duration-150 break-all
                bg-white border border-zinc-200 rounded-lg px-2.5 py-1.5
              "
              title="Click to copy full hash"
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === "Enter" && copyToClipboard(auditHash)}
              aria-label="Copy audit hash to clipboard"
            >
              {copied ? 'Copied!' : (auditHash ? `${auditHash.substring(0, 16)}…` : 'N/A')}
            </div>
          </div>

          {/* 7. Footer disclaimer */}
          <p className="text-[10px] text-zinc-400 italic border-t border-zinc-200 pt-2.5 leading-relaxed">
            This trace shows the internal reasoning logic used to generate the answer above.
          </p>
        </div>
      )}
    </div>
  );
}
