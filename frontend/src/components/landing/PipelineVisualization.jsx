import { useState } from "react";
import useIntersectionObserver from "../../hooks/useIntersectionObserver.js";

const STEPS = [
  { id: 1, label: "User Input",        sublabel: "React UI",            emoji: "💬", detail: "The user's natural-language legal question enters via the chat interface." },
  { id: 2, label: "Intent Classifier", sublabel: "spaCy NLP",           emoji: "🎯", detail: "Classifies the domain: employment, contract, PDPA, or out-of-scope." },
  { id: 3, label: "Entity Extractor",  sublabel: "spaCy NER",           emoji: "🔍", detail: "Extracts parties, dates, monetary values, and statute references." },
  { id: 4, label: "KB Retriever",      sublabel: "ChromaDB Hybrid",     emoji: "📚", detail: "BM25 Okapi + dense vector search over 48 Singapore statute PDFs. Returns top-3 chunks." },
  { id: 5, label: "Prompt Builder",    sublabel: "Jinja2",              emoji: "📝", detail: "Assembles a structured prompt from retrieved chunks, entities, and history." },
  { id: 6, label: "LLM",              sublabel: "Llama-3.1-8b · Groq", emoji: "🤖", detail: "Generates structured output: Applicable Law → Reasoning → Answer → Limitations." },
  { id: 7, label: "Rule Engine",       sublabel: "20 IF-THEN rules",    emoji: "⚖️",  detail: "Checks LLM statute citations against 20 symbolic Singapore legal rules." },
  { id: 8, label: "Audit Logger",      sublabel: "SHA-256 JSONL",       emoji: "🔐", detail: "Appends a tamper-evident log entry and returns the SHA-256 audit hash." },
];

export default function PipelineVisualization() {
  const [active, setActive] = useState(null);
  const [ref, visible] = useIntersectionObserver({ threshold: 0.1 });

  return (
    <section className="py-28 px-6 bg-white">
      <div className="max-w-6xl mx-auto">
        <div className={`reveal ${visible ? "visible" : ""} text-center mb-16`} ref={ref}>
          <p className="text-[11px] uppercase tracking-widest font-semibold text-zinc-400 mb-3">
            Under the hood
          </p>
          <h2 className="font-display text-4xl sm:text-5xl font-black text-zinc-900 leading-tight mb-4">
            The 8-step pipeline.
          </h2>
          <p className="text-sm text-zinc-400">Hover a step to learn more</p>
        </div>

        {/* Scrollable on small screens */}
        <div className="overflow-x-auto pb-4">
          <div className="flex items-start gap-0 min-w-[860px]">
            {STEPS.map((step, i) => (
              <div key={step.id} className="flex items-center flex-1 min-w-0">
                {/* Step card */}
                <button
                  className={`pipeline-card group flex flex-col items-center text-center rounded-2xl border transition-all duration-300 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400
                    ${active === step.id
                      ? "bg-zinc-900 border-zinc-900 text-white shadow-lg w-44 px-4 py-5"
                      : "bg-zinc-50 border-zinc-200 text-zinc-700 hover:border-zinc-400 hover:shadow-md w-20 px-2 py-4"
                    }`}
                  onMouseEnter={() => setActive(step.id)}
                  onMouseLeave={() => setActive(null)}
                  onClick={() => setActive(active === step.id ? null : step.id)}
                  aria-expanded={active === step.id}
                  aria-label={step.label}
                >
                  <span className="text-xl mb-2">{step.emoji}</span>
                  <span className={`font-semibold text-[11px] leading-tight ${active === step.id ? "text-white" : "text-zinc-700"}`}>
                    {step.label}
                  </span>
                  {active === step.id && (
                    <>
                      <span className="text-[10px] text-zinc-400 mt-1 font-medium">{step.sublabel}</span>
                      <p className="text-[11px] text-zinc-300 leading-snug mt-2.5 text-center">
                        {step.detail}
                      </p>
                    </>
                  )}
                  {/* Step number */}
                  <span className={`text-[9px] font-bold mt-2 ${active === step.id ? "text-zinc-500" : "text-zinc-400"}`}>
                    0{step.id}
                  </span>
                </button>

                {/* Connector arrow */}
                {i < STEPS.length - 1 && (
                  <div className="flex-1 flex items-center justify-center px-1" aria-hidden="true">
                    <div className="h-px bg-zinc-200 flex-1" />
                    <svg width="8" height="8" viewBox="0 0 8 8" fill="none" className="flex-shrink-0 text-zinc-300">
                      <path d="M0 4h7M4 1l3 3-3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Active step detail strip (mobile fallback) */}
        {active && (
          <div className="mt-6 p-4 bg-zinc-900 rounded-xl text-white text-sm md:hidden animate-msg-in">
            <span className="font-semibold">{STEPS[active - 1].label}</span>
            <span className="text-zinc-400 text-xs ml-2">{STEPS[active - 1].sublabel}</span>
            <p className="text-zinc-300 text-xs mt-1 leading-relaxed">{STEPS[active - 1].detail}</p>
          </div>
        )}
      </div>
    </section>
  );
}
