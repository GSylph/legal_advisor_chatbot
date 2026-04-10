import useIntersectionObserver from "../../hooks/useIntersectionObserver.js";

const PILLARS = [
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 19.5A2.5 2.5 0 016.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" />
        <line x1="9" y1="7" x2="15" y2="7" />
        <line x1="9" y1="11" x2="15" y2="11" />
      </svg>
    ),
    title: "Retrieval-Augmented",
    subtitle: "Grounded in statute",
    description:
      "Hybrid BM25 + dense vector search over 48 Singapore statute PDFs. Every answer is grounded in retrieved text — the model cannot hallucinate references it was never given.",
    stat: "72.5% Hit@5",
    statLabel: "Hybrid retrieval",
  },
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        <polyline points="9 12 11 14 15 10" />
      </svg>
    ),
    title: "Symbolic Rules",
    subtitle: "20 IF-THEN checks",
    description:
      "A deterministic rule engine with 20 Singapore legal rules (Employment Act, Contract Law, PDPA) cross-checks every LLM answer for statutory consistency. Flags contradictions instantly.",
    stat: "20 rules",
    statLabel: "Employment · Contract · PDPA",
  },
  {
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
        <path d="M7 11V7a5 5 0 0110 0v4" />
        <circle cx="12" cy="16" r="1" fill="currentColor" />
      </svg>
    ),
    title: "Cryptographic Audit",
    subtitle: "SHA-256 tamper-evident log",
    description:
      "Every interaction is SHA-256 hashed and appended to an append-only JSONL audit log. Tamper detection is built in — each entry is verifiable against its hash at any time.",
    stat: "SHA-256",
    statLabel: "Per-interaction hash",
  },
];

export default function FeaturePillars() {
  const [ref, visible] = useIntersectionObserver();

  return (
    <section className="py-28 px-6">
      <div className="max-w-5xl mx-auto">
        {/* Section label */}
        <div ref={ref} className={`reveal ${visible ? "visible" : ""} text-center mb-16`}>
          <p className="text-[11px] uppercase tracking-widest font-semibold text-zinc-400 mb-3">
            What makes it different
          </p>
          <h2 className="font-display text-4xl sm:text-5xl font-black text-zinc-900 leading-tight">
            Three layers of trust.
          </h2>
        </div>

        {/* Pillars */}
        <ul ref={ref} className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {PILLARS.map((p, i) => (
            <li
              key={p.title}
              style={{ "--i": i }}
              className={`reveal-child ${visible ? "visible" : ""} bg-white rounded-2xl p-7 shadow-card border border-zinc-100 flex flex-col gap-5`}
            >
              <div className="w-12 h-12 rounded-xl bg-zinc-50 border border-zinc-100 flex items-center justify-center text-zinc-700">
                {p.icon}
              </div>
              <div>
                <h3 className="font-display text-xl font-bold text-zinc-900 mb-1">{p.title}</h3>
                <p className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-3">{p.subtitle}</p>
                <p className="text-sm text-zinc-500 leading-relaxed">{p.description}</p>
              </div>
              <div className="mt-auto pt-4 border-t border-zinc-100">
                <span className="font-display text-2xl font-black text-zinc-900">{p.stat}</span>
                <p className="text-[11px] text-zinc-400 mt-0.5">{p.statLabel}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
