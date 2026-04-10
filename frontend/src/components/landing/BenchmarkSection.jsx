import useIntersectionObserver from "../../hooks/useIntersectionObserver.js";
import useCountUp from "../../hooks/useCountUp.js";

function StatCard({ value, decimals = 0, suffix = "", label, sublabel, highlight = false }) {
  const [ref, visible] = useIntersectionObserver({ threshold: 0.3 });
  const [, display] = useCountUp(value, { decimals, suffix, enabled: visible });

  return (
    <div
      ref={ref}
      className={`rounded-2xl p-7 flex flex-col gap-2 ${
        highlight
          ? "bg-zinc-900 text-white"
          : "bg-white border border-zinc-100 shadow-card"
      }`}
    >
      <span className={`font-display text-[3rem] font-black leading-none tabular-nums ${highlight ? "text-white" : "text-zinc-900"}`}>
        {display}
      </span>
      <span className={`text-sm font-semibold ${highlight ? "text-zinc-300" : "text-zinc-700"}`}>{label}</span>
      {sublabel && <span className={`text-[11px] ${highlight ? "text-zinc-500" : "text-zinc-400"}`}>{sublabel}</span>}
    </div>
  );
}

const RETRIEVAL_ROWS = [
  { retriever: "BM25",   p3: "0.279", hit3: "50.7%", p5: "0.249", hit5: "56.3%" },
  { retriever: "Dense",  p3: "0.289", hit3: "57.8%", p5: "0.249", hit5: "65.5%" },
  { retriever: "Hybrid", p3: "0.322", hit3: "58.5%", p5: "0.293", hit5: "72.5%", best: true },
];

export default function BenchmarkSection() {
  const [headRef, headVisible] = useIntersectionObserver();
  const [tableRef, tableVisible] = useIntersectionObserver({ threshold: 0.1 });

  return (
    <section className="py-28 px-6">
      <div className="max-w-5xl mx-auto">
        <div ref={headRef} className={`reveal ${headVisible ? "visible" : ""} text-center mb-16`}>
          <p className="text-[11px] uppercase tracking-widest font-semibold text-zinc-400 mb-3">
            Evaluation results
          </p>
          <h2 className="font-display text-4xl sm:text-5xl font-black text-zinc-900 leading-tight">
            Numbers that matter.
          </h2>
        </div>

        {/* Big stat grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-14">
          <StatCard value={72.5}  decimals={1} suffix="%" label="Hybrid Hit@5"          sublabel="T12 retrieval" highlight />
          <StatCard value={80}    decimals={0} suffix="%" label="Citation Accuracy"      sublabel="Dense retrieval · T22" />
          <StatCard value={36}    decimals={0} suffix="%" label="Hallucination Rate"     sublabel="Hybrid · T22 (vs 42% baseline)" />
          <StatCard value={0.45}  decimals={2} suffix=""  label="Optimal Threshold"      sublabel="11% OOS refusal · T23" />
        </div>

        {/* Retrieval table */}
        <div ref={tableRef} className={`reveal ${tableVisible ? "visible" : ""}`}>
          <h3 className="font-semibold text-zinc-700 text-sm mb-4">T12 — Retrieval benchmark (n=142)</h3>
          <div className="overflow-x-auto rounded-2xl border border-zinc-100 shadow-card">
            <table className="w-full text-sm bg-white">
              <thead>
                <tr className="border-b border-zinc-100">
                  {["Retriever", "P@3", "Hit@3", "P@5", "Hit@5"].map((h) => (
                    <th key={h} className="px-5 py-3.5 text-left text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {RETRIEVAL_ROWS.map((row) => (
                  <tr
                    key={row.retriever}
                    className={`border-b last:border-0 border-zinc-50 ${row.best ? "bg-zinc-900 text-white" : "hover:bg-zinc-50 transition-colors"}`}
                  >
                    <td className={`px-5 py-4 font-semibold ${row.best ? "text-white" : "text-zinc-800"}`}>
                      {row.retriever}
                      {row.best && <span className="ml-2 text-[10px] bg-emerald-500 text-white px-1.5 py-0.5 rounded font-bold">BEST</span>}
                    </td>
                    {[row.p3, row.hit3, row.p5, row.hit5].map((v, i) => (
                      <td key={i} className={`px-5 py-4 tabular-nums ${row.best ? "text-zinc-300" : "text-zinc-600"}`}>{v}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-[11px] text-zinc-400 mt-3 text-right">58 questions excluded (non-statute gold references)</p>
        </div>
      </div>
    </section>
  );
}
