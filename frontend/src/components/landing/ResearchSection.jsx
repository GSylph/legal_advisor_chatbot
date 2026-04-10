import useIntersectionObserver from "../../hooks/useIntersectionObserver.js";

export default function ResearchSection() {
  const [ref, visible] = useIntersectionObserver({ threshold: 0.1 });

  return (
    <section id="research" className="py-28 px-6 bg-white">
      <div className="max-w-3xl mx-auto">
        <div ref={ref} className={`reveal ${visible ? "visible" : ""}`}>
          <div className="inline-flex items-center gap-2 bg-zinc-900 text-white rounded-full px-4 py-1.5 text-xs font-semibold mb-8">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
            </svg>
            Targeting JURIX 2025 · LNCS Springer
          </div>

          <h2 className="font-display text-4xl sm:text-5xl font-black text-zinc-900 leading-tight mb-8">
            Research contribution.
          </h2>

          <div className="space-y-5 text-zinc-600 text-base leading-relaxed">
            <p>
              This work addresses a gap in legal AI: most systems are opaque, producing answers without
              verifiable reasoning chains or accountability mechanisms. EALAI introduces a three-layer
              architecture where every answer can be traced, checked, and audited.
            </p>
            <p>
              The <strong className="text-zinc-900 font-semibold">symbolic rule engine</strong> provides
              deterministic cross-checking of LLM outputs against 20 Singapore-law IF-THEN rules.
              The <strong className="text-zinc-900 font-semibold">cryptographic audit log</strong> creates
              an immutable record of every interaction — query, retrieved context, rule match result,
              and LLM reasoning — hashed with SHA-256 for tamper detection.
            </p>
            <p>
              Evaluated on a 200-question benchmark dataset spanning Employment Act 1968, PDPA, and
              Contract/Consumer law. The hybrid retrieval system achieves 72.5% Hit@5 and the
              recommended refusal threshold of 0.45 yields 11% out-of-scope refusal with only 3% false
              positive rate.
            </p>
          </div>

          <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { label: "200 QA pairs",        sub: "74 employment · 62 contract · 64 PDPA" },
              { label: "44 open questions",   sub: "Awaiting experimental results" },
              { label: "6 experiments",       sub: "T12 · T22 · T23 + 3 pending" },
            ].map((item) => (
              <div key={item.label} className="rounded-xl border border-zinc-100 p-4 bg-zinc-50">
                <p className="font-semibold text-zinc-800 text-sm">{item.label}</p>
                <p className="text-[11px] text-zinc-400 mt-0.5">{item.sub}</p>
              </div>
            ))}
          </div>

          <div className="mt-10 flex flex-col sm:flex-row gap-3">
            <a
              href="#"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-zinc-900 text-white text-sm font-semibold hover:bg-zinc-700 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-700"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Download paper draft
            </a>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full border border-zinc-300 text-zinc-600 text-sm font-semibold hover:border-zinc-500 hover:text-zinc-900 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
