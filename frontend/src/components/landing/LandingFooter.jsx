import { useNavigate } from "react-router-dom";

export default function LandingFooter() {
  const navigate = useNavigate();

  return (
    <footer className="py-24 px-6 border-t border-zinc-200">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="font-display text-4xl sm:text-5xl font-black text-zinc-900 mb-4">
          Ready to start?
        </h2>
        <p className="text-zinc-500 mb-10 max-w-md mx-auto">
          Ask your first Singapore law question. No account needed.
        </p>
        <button
          onClick={() => navigate("/app")}
          className="px-10 py-4 rounded-full bg-zinc-900 text-white font-semibold text-base hover:bg-zinc-700 transition-colors duration-200 shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-zinc-700"
        >
          Start a consultation →
        </button>
        <p className="mt-12 text-[11px] text-zinc-400 max-w-sm mx-auto leading-relaxed">
          EALAI is a research prototype. Responses are AI-generated and do not constitute
          legal advice. Always consult a qualified Singapore lawyer for your situation.
        </p>
        <div className="mt-8 flex items-center justify-center gap-6 text-[11px] text-zinc-400">
          <span>EALAI · JURIX 2025</span>
          <span>·</span>
          <span>Singapore Law Only</span>
          <span>·</span>
          <button onClick={() => navigate("/app")} className="hover:text-zinc-700 transition-colors">
            Open App
          </button>
        </div>
      </div>
    </footer>
  );
}
