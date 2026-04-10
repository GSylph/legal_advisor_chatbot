import { useNavigate } from "react-router-dom";

const QUESTIONS = [
  "Can my employer terminate me without notice?",
  "What does the PDPA say about data consent?",
  "Is my rental contract legally enforceable?",
  "What are my rights under Singapore employment law?",
  "How does the Personal Data Protection Act apply to me?",
];

import { useEffect, useState } from "react";

function TypewriterLoop() {
  const [idx, setIdx] = useState(0);
  const [displayed, setDisplayed] = useState("");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const current = QUESTIONS[idx];
    let timeout;

    if (!deleting && displayed.length < current.length) {
      timeout = setTimeout(() => setDisplayed(current.slice(0, displayed.length + 1)), 38);
    } else if (!deleting && displayed.length === current.length) {
      timeout = setTimeout(() => setDeleting(true), 2200);
    } else if (deleting && displayed.length > 0) {
      timeout = setTimeout(() => setDisplayed(displayed.slice(0, -1)), 18);
    } else if (deleting && displayed.length === 0) {
      setDeleting(false);
      setIdx((i) => (i + 1) % QUESTIONS.length);
    }

    return () => clearTimeout(timeout);
  }, [displayed, deleting, idx]);

  return (
    <span className="text-zinc-500 font-ui text-base sm:text-lg font-normal">
      &ldquo;{displayed}
      <span className="inline-block w-[2px] h-[1.1em] bg-zinc-400 ml-0.5 animate-blink align-text-bottom" aria-hidden="true" />
      &rdquo;
    </span>
  );
}

export default function HeroSection() {
  const navigate = useNavigate();

  return (
    <section className="min-h-screen flex flex-col items-center justify-center px-6 text-center relative overflow-hidden">
      {/* Subtle grid background */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(rgba(0,0,0,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0,0,0,0.04) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
        }}
        aria-hidden="true"
      />

      <div className="relative z-10 max-w-4xl mx-auto">
        {/* Badge */}
        <div className="animate-hero-fade inline-flex items-center gap-2 bg-white border border-zinc-200 rounded-full px-4 py-1.5 text-xs font-medium text-zinc-500 mb-8 shadow-sm">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Targeting JURIX 2025 · Singapore Law
        </div>

        {/* Main heading */}
        <h1 className="animate-hero-fade-2 font-display text-[3.2rem] sm:text-[4.5rem] lg:text-[5.5rem] font-black text-zinc-900 leading-[1.05] tracking-tight mb-6">
          Legal AI that
          <br />
          <span className="text-zinc-400">shows its work.</span>
        </h1>

        {/* Subheading */}
        <p className="animate-hero-fade-3 font-ui text-lg sm:text-xl text-zinc-500 max-w-2xl mx-auto mb-4 leading-relaxed">
          EALAI combines retrieval-augmented generation, symbolic rule checking,
          and cryptographic audit logging to deliver explainable legal guidance
          on Singapore law.
        </p>

        {/* Typewriter */}
        <div className="animate-hero-fade-3 mb-10 min-h-[2rem]">
          <TypewriterLoop />
        </div>

        {/* CTAs */}
        <div className="animate-hero-fade-3 flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            onClick={() => navigate("/app")}
            className="px-7 py-3 rounded-full bg-zinc-900 text-white font-semibold text-sm hover:bg-zinc-700 transition-colors duration-200 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-700"
          >
            Try it now →
          </button>
          <a
            href="#research"
            className="px-7 py-3 rounded-full border border-zinc-300 text-zinc-600 font-semibold text-sm hover:border-zinc-500 hover:text-zinc-900 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-400"
          >
            Read the research
          </a>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1.5 text-zinc-400" aria-hidden="true">
        <span className="text-[11px] font-medium tracking-widest uppercase">Scroll</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="animate-bounce">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </div>
    </section>
  );
}
